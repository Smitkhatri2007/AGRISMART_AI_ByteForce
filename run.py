
#!/usr/bin/env python3
"""
AgriSmart AI - Universal Setup & Launch Script
Works on: Windows, Linux, macOS — any terminal, any OS.

Usage (one command):
    python run.py

Ref: SIH 2026 Problem Statement 1, Section 7.2
"""

import os
import sys
import subprocess
import platform


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(SCRIPT_DIR, "backend")
VENV_DIR = os.path.join(BACKEND_DIR, "venv")


def print_banner(msg):
    print(f"\n{'='*60}")
    print(f"  {msg}")
    print(f"{'='*60}\n")


def get_venv_python():
    """Return the path to the Python binary inside the venv."""
    if platform.system() == "Windows":
        return os.path.join(VENV_DIR, "Scripts", "python.exe")
    return os.path.join(VENV_DIR, "bin", "python3")


def get_venv_pip():
    """Return the path to pip inside the venv."""
    if platform.system() == "Windows":
        return os.path.join(VENV_DIR, "Scripts", "pip.exe")
    return os.path.join(VENV_DIR, "bin", "pip")


def run(cmd, cwd=None):
    """Run a command and stream output live."""
    result = subprocess.run(cmd, cwd=cwd or SCRIPT_DIR, shell=isinstance(cmd, str))
    if result.returncode != 0:
        print(f"[ERROR] Command failed with exit code {result.returncode}")
        sys.exit(result.returncode)


def main():
    print_banner("AgriSmart AI - Setup and Start")

    os_name = platform.system()
    print(f"[INFO] OS: {os_name} ({platform.platform()})")
    print(f"[INFO] Python: {sys.version.split()[0]}")

    # ── Step 1: Create venv ──────────────────────────────────────
    if not os.path.isdir(VENV_DIR):
        print("[INFO] Creating virtual environment...")
        run([sys.executable, "-m", "venv", VENV_DIR])
    else:
        print("[INFO] Virtual environment found.")

    venv_python = get_venv_python()
    venv_pip = get_venv_pip()

    # Verify venv python exists
    if not os.path.isfile(venv_python):
        # Fallback: some systems use "python" not "python3" inside venv
        alt = os.path.join(VENV_DIR, "bin", "python")
        if os.path.isfile(alt):
            venv_python = alt
        else:
            print(f"[ERROR] Virtual environment Python not found at {venv_python}")
            sys.exit(1)

    # ── Step 2: Install dependencies ─────────────────────────────
    print("[INFO] Installing dependencies...")
    run([venv_pip, "install", "--upgrade", "pip", "-q"])
    root_req = os.path.join(SCRIPT_DIR, "requirements.txt")
    if os.path.isfile(root_req):
        run([venv_pip, "install", "-r", root_req, "-q"])
    run([venv_pip, "install", "-r", os.path.join(BACKEND_DIR, "requirements.txt"), "-q"])

    # ── Step 3: Setup .env ───────────────────────────────────────
    env_file = os.path.join(BACKEND_DIR, ".env")
    env_example = os.path.join(BACKEND_DIR, ".env.example")
    if not os.path.isfile(env_file) and os.path.isfile(env_example):
        import shutil
        shutil.copy2(env_example, env_file)
        print("[INFO] Created backend/.env from .env.example")
        print("[INFO] Add your GROQ_API_KEY in backend/.env for full AI chat (optional).")

    # ── Step 4: Verify model weights ─────────────────────────────
    print("[INFO] Verifying model weights...")
    run([venv_python, os.path.join(BACKEND_DIR, "model", "download_weights.py")])

    # ── Step 5: Start server ─────────────────────────────────────
    print_banner("Starting FastAPI server at http://localhost:8000")
    run(
        [venv_python, "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"],
        cwd=BACKEND_DIR
    )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[INFO] Server stopped by user.")
        sys.exit(0)
