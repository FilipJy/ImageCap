import base64
import csv
import json
import os
import re
import uuid
from pathlib import Path
from threading import Lock
from typing import List, Optional
from urllib.parse import urlparse

import httpx
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

PROMPTS_FILE = Path(__file__).with_name("prompts.md")
CAPTION_LOG_FILE = Path(__file__).with_name("caption_log.csv")
CAPTION_LOG_JSON_FILE = Path(__file__).with_name("caption_log.json")
DEFAULT_MODEL = os.getenv("OLLAMA_MODEL", "")
_CAPTION_LOG_LOCK = Lock()


def _resolve_ollama_urls() -> tuple[str, str]:
    """Derive base and generate endpoints for the local Ollama API."""
    host_override = os.getenv("OLLAMA_HOST")
    if host_override:
        base_url = host_override.rstrip("/")
        return base_url, f"{base_url}/api/generate"

    generate_url = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
    parsed = urlparse(generate_url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"
    return base_url, generate_url


OLLAMA_BASE_URL, OLLAMA_GENERATE_URL = _resolve_ollama_urls()
OLLAMA_TAGS_URL = f"{OLLAMA_BASE_URL}/api/tags"


class Prompt(BaseModel):
    id: str
    label: str
    prompt: str


class PromptCreate(BaseModel):
    label: str
    prompt: str


PROMPT_SECTION_PATTERN = re.compile(
    r"^##\s+(?P<label>.+?)\s*$"  # label line
    r"\n\s*id:\s*(?P<id>[^\n]+)\s*$"  # id line
    r"\n\n(?P<body>.*?)(?=^##\s+|\Z)",
    re.MULTILINE | re.DOTALL,
)


def _sanitize_markdown(text: str) -> str:
    return text.replace("\r\n", "\n").strip("\n")


class PromptStore:
    def __init__(self, file_path: Path) -> None:
        self._path = file_path
        self._lock = Lock()
        self._prompts = self._load()

    def _load(self) -> List[Prompt]:
        if not self._path.exists():
            return []
        raw_text = self._path.read_text(encoding="utf-8")
        prompts: list[Prompt] = []
        for match in PROMPT_SECTION_PATTERN.finditer(raw_text):
            label = match.group("label").strip()
            prompt_id = match.group("id").strip()
            body = _sanitize_markdown(match.group("body"))
            if not (label and prompt_id and body):
                continue
            prompts.append(Prompt(id=prompt_id, label=label, prompt=body))
        return prompts

    def _persist(self) -> None:
        lines = ["# Prompts"]
        for prompt in self._prompts:
            lines.append("")
            lines.append(f"## {prompt.label.strip() or 'Untitled prompt'}")
            lines.append(f"id: {prompt.id}")
            lines.append("")
            lines.append(prompt.prompt.strip() + "\n")
        content = "\n".join(lines).rstrip() + "\n"
        self._path.write_text(content, encoding="utf-8")

    def list_prompts(self) -> List[Prompt]:
        with self._lock:
            return list(self._prompts)

    def get_prompt(self, prompt_id: str) -> Prompt:
        with self._lock:
            for prompt in self._prompts:
                if prompt.id == prompt_id:
                    return prompt
        raise KeyError(prompt_id)

    def add_prompt(self, label: str, prompt_text: str) -> Prompt:
        with self._lock:
            new_prompt = Prompt(id=str(uuid.uuid4()), label=label, prompt=prompt_text)
            self._prompts.append(new_prompt)
            self._persist()
            return new_prompt


class GenerationResponse(BaseModel):
    prompt_id: Optional[str]
    prompt_text: str
    model: str
    output: str


store = PromptStore(PROMPTS_FILE)

app = FastAPI(title="Image Captioning Playground", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/prompts", response_model=List[Prompt])
def list_prompts() -> List[Prompt]:
    return store.list_prompts()


@app.post("/prompts", response_model=Prompt, status_code=201)
def create_prompt(prompt: PromptCreate) -> Prompt:
    label = prompt.label.strip()
    prompt_text = prompt.prompt.strip()
    if not label:
        raise HTTPException(status_code=400, detail="Label cannot be empty.")
    if not prompt_text:
        raise HTTPException(status_code=400, detail="Prompt cannot be empty.")
    return store.add_prompt(label=label, prompt_text=prompt_text)


@app.get("/models", response_model=List[str])
async def list_models() -> List[str]:
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(30.0)) as client:
            response = await client.get(OLLAMA_TAGS_URL)
            response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
    except httpx.RequestError as exc:
        raise HTTPException(status_code=503, detail=f"Failed to reach Ollama: {exc}")

    payload = response.json()
    if isinstance(payload, dict):
        models = [item["name"] for item in payload.get("models", []) if isinstance(item, dict) and "name" in item]
        return sorted({model for model in models})

    raise HTTPException(status_code=502, detail="Unexpected response from Ollama.")


def _flatten_for_csv(text: str) -> str:
    return " ".join(text.split())


def _log_caption(prompt_text: str, image_name: str, model: str, caption: str) -> None:
    image = image_name or "uploaded_image"
    entry = {
        "prompt": prompt_text,
        "image_name": image,
        "model": model,
        "caption": caption,
    }
    with _CAPTION_LOG_LOCK:
        write_header = not CAPTION_LOG_FILE.exists()
        with CAPTION_LOG_FILE.open("a", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle)
            if write_header:
                writer.writerow(["prompt", "image_name", "model", "caption"])
            writer.writerow([
                _flatten_for_csv(prompt_text),
                _flatten_for_csv(image),
                _flatten_for_csv(model),
                _flatten_for_csv(caption),
            ])

        existing: list[dict[str, str]] = []
        if CAPTION_LOG_JSON_FILE.exists():
            try:
                payload = json.loads(CAPTION_LOG_JSON_FILE.read_text(encoding="utf-8"))
                if isinstance(payload, list):
                    existing = payload
            except json.JSONDecodeError:
                existing = []
        existing.append(entry)
        CAPTION_LOG_JSON_FILE.write_text(
            json.dumps(existing, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )


async def _call_ollama(model: str, prompt_text: str, image_bytes: bytes) -> str:
    image_b64 = base64.b64encode(image_bytes).decode("utf-8")
    payload = {
        "model": model,
        "prompt": prompt_text,
        "images": [image_b64],
        "stream": False,
    }

    async with httpx.AsyncClient(timeout=httpx.Timeout(480.0)) as client:
        response = await client.post(OLLAMA_GENERATE_URL, json=payload)
        response.raise_for_status()
    data = response.json()
    if isinstance(data, dict):
        if "response" in data:
            return data["response"].strip()
        if "message" in data and isinstance(data["message"], dict):
            content = data["message"].get("content")
            if isinstance(content, str):
                return content.strip()
    raise HTTPException(status_code=502, detail="Unexpected response from Ollama.")


@app.post("/generate", response_model=GenerationResponse)
async def generate_caption(
    file: UploadFile = File(...),
    prompt_id: Optional[str] = Form(None),
    prompt_text: Optional[str] = Form(None),
    model: Optional[str] = Form(None),
) -> GenerationResponse:
    if not prompt_text and not prompt_id:
        raise HTTPException(status_code=400, detail="Either prompt_text or prompt_id is required.")

    chosen_model = (model or DEFAULT_MODEL).strip()
    if not chosen_model:
        raise HTTPException(status_code=400, detail="Model name cannot be empty.")

    resolved_prompt = (prompt_text or "").strip()
    resolved_prompt_id: Optional[str] = None
    if not resolved_prompt and prompt_id:
        try:
            resolved_prompt = store.get_prompt(prompt_id).prompt
            resolved_prompt_id = prompt_id
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=f"Prompt {exc.args[0]} not found.") from exc
    elif prompt_id:
        resolved_prompt_id = prompt_id

    if not resolved_prompt:
        raise HTTPException(status_code=400, detail="Prompt text is empty.")

    image_bytes = await file.read()
    if not image_bytes:
        raise HTTPException(status_code=400, detail="Uploaded image is empty.")

    try:
        output_text = await _call_ollama(chosen_model, resolved_prompt, image_bytes)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
    except httpx.RequestError as exc:
        raise HTTPException(status_code=503, detail=f"Failed to reach Ollama: {exc}")

    _log_caption(resolved_prompt, file.filename or "", chosen_model, output_text)

    return GenerationResponse(
        prompt_id=resolved_prompt_id,
        prompt_text=resolved_prompt,
        model=chosen_model,
        output=output_text,
    )


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
