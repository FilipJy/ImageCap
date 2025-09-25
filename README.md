# Imagecap

Imagecap is a playground for generating image captions by combining a Vue-based frontend with a FastAPI backend that proxies requests to a local Ollama model.

## Requirements

- Python 3.10 or later
- Node.js 20 or later (ships with npm)
- [Ollama](https://ollama.com/) running locally with a vision-capable model pulled (for example `ollama pull llava`)

> The backend talks to Ollama at `http://localhost:11434` by default. If your instance runs elsewhere, set `OLLAMA_URL` or `OLLAMA_HOST` before starting (details below).

## Quick start (one command)

1. Open a terminal in the project root.
2. Run the launcher:
   - macOS/Linux: `python3 start.py`
   - Windows: `py start.py`
3. The script will:
   - create `.venv/` if needed and install backend dependencies
   - install frontend dependencies with npm
   - start the FastAPI backend on `http://localhost:8000`
   - start the Vite dev server on `http://localhost:5173`
4. When the logs say `VITE v... ready in ...`, open <http://localhost:5173> in your browser.
5. Press `Ctrl+C` once in the terminal to stop both servers cleanly.

> Tip: rerun the same command any time. Dependencies are reused, so subsequent launches only take a few seconds.

## Caption history

Every successful generation is appended to `backend/caption_log.csv` (spreadsheet-friendly) and `backend/caption_log.json` (human-readable), recording the prompt text, uploaded file name, model, and caption. Delete these files if you want to reset the log.

## Prompt options

Use the prompt panel tabs to switch between saved prompts, adding a new reusable entry, or the one-off "Free prompt mode" for ad-hoc experimentation.

## Batch mode

Switch to the Batch mode panel in the app to drop in multiple images at once. The UI will process them sequentially with the current prompt/model and shows per-image progress, captions, and any errors.

## Customising the backend connection

- To pick a different Ollama API endpoint: `export OLLAMA_URL="http://my-host:11434/api/generate"`
- To set the default model shown in the UI: `export OLLAMA_MODEL="llava"`

Set the variables before invoking `start.py` (on Windows use `set` instead of `export`).

## Manual setup (advanced)

If you prefer to run services yourself:

1. **Backend**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   pip install -r backend/requirements.txt
   uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
   ```
2. **Frontend**
   ```bash
   cd frontend
   npm install
   npm run dev -- --host --port 5173
   ```

Stop each process with `Ctrl+C`.

## Project structure

- `backend/` – FastAPI application serving prompt management and caption generation
- `frontend/` – Vue 3 single-page app built with Vite
- `start.py` – convenience launcher that wires everything together
- `prompts.md` – persisted prompt library editable through the UI

## Troubleshooting

- **Missing Python or Node:** Install the required versions from <https://www.python.org/downloads/> and <https://nodejs.org/en/download>.
- **Ollama connection errors:** Ensure `ollama serve` (or the desktop app) is running and that the chosen model is pulled.
- **Port already in use:** Stop the conflicting program or edit the ports in `start.py` before running.

Happy captioning!
