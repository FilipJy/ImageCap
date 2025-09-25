#!/usr/bin/env python3
"""Bootstrap and run the Image Captioning playground locally."""
from __future__ import annotations

import os
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parent
BACKEND_DIR = ROOT / "backend"
FRONTEND_DIR = ROOT / "frontend"
VENV_DIR = ROOT / ".venv"
PYTHON_BIN = VENV_DIR / ("Scripts/python.exe" if os.name == "nt" else "bin/python")


class SetupError(RuntimeError):
    """Raised when an expected tool is missing."""


def _run(command: Iterable[str], *, cwd: Path | None = None) -> None:
    display_cwd = cwd if cwd else ROOT
    print(f"\n→ Running {' '.join(command)} (cwd={display_cwd})")
    subprocess.run(command, cwd=cwd, check=True)


def ensure_tool(name: str, message: str) -> None:
    if shutil.which(name) is None:
        raise SetupError(message)


def ensure_virtualenv() -> None:
    if PYTHON_BIN.exists():
        return
    print("Creating virtual environment under .venv …")
    subprocess.run([sys.executable, "-m", "venv", str(VENV_DIR)], check=True)


def install_backend_dependencies() -> None:
    print("Installing backend dependencies …")
    _run([str(PYTHON_BIN), "-m", "pip", "install", "--upgrade", "pip"], cwd=ROOT)
    _run([str(PYTHON_BIN), "-m", "pip", "install", "-r", str(BACKEND_DIR / "requirements.txt")], cwd=ROOT)


def install_frontend_dependencies() -> None:
    print("Installing frontend dependencies …")
    _run(["npm", "install"], cwd=FRONTEND_DIR)


def start_services() -> None:
    env = os.environ.copy()
    backend_cmd = [
        str(PYTHON_BIN),
        "-m",
        "uvicorn",
        "backend.main:app",
        "--reload",
        "--host",
        "0.0.0.0",
        "--port",
        "8000",
    ]
    frontend_cmd = ["npm", "run", "dev", "--", "--host", "--port", "5173"]

    print("\nStarting backend and frontend. Press Ctrl+C to stop both.")
    backend_proc = subprocess.Popen(backend_cmd, cwd=ROOT, env=env)
    frontend_proc = subprocess.Popen(frontend_cmd, cwd=FRONTEND_DIR, env=env)
    processes = [backend_proc, frontend_proc]

    def _terminate(*_: object) -> None:
        print("\nShutting down services …")
        for proc in processes:
            if proc.poll() is None:
                proc.terminate()
        for proc in processes:
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
        sys.exit(0)

    signal.signal(signal.SIGINT, _terminate)
    if os.name != "nt":
        signal.signal(signal.SIGTERM, _terminate)

    try:
        while True:
            for proc in processes:
                code = proc.poll()
                if code is not None:
                    print(f"\nProcess {'backend' if proc is backend_proc else 'frontend'} exited with code {code}.")
                    _terminate()
            time.sleep(0.5)
    except KeyboardInterrupt:
        _terminate()


def main() -> None:
    python_cmd = "python" if os.name == "nt" else "python3"
    try:
        ensure_tool(python_cmd, "Python 3.10+ is required to run this project.")
        ensure_tool("npm", "Node.js 20 (which includes npm) is required to run the frontend.")
        ensure_virtualenv()
        install_backend_dependencies()
        install_frontend_dependencies()
        start_services()
    except SetupError as exc:
        print(f"\nERROR: {exc}")
        sys.exit(1)
    except subprocess.CalledProcessError as exc:
        cmd_repr = ' '.join(str(arg) for arg in exc.cmd)
        print(f"\nCommand {cmd_repr} failed with exit code {exc.returncode}.")
        sys.exit(exc.returncode)


if __name__ == "__main__":
    main()
