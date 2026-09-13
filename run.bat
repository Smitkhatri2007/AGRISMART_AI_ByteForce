@echo off
title AgriSmart AI - Server
echo ==================================================
echo         AgriSmart AI - Setup and Start
echo ==================================================
echo.

cd /d "%~dp0backend"

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Please install Python 3.10+ and try again.
    pause
    exit /b
)

:: Check for virtual environment
if not exist "venv\Scripts\activate.bat" (
    echo [INFO] Virtual environment not found. Creating one...
    python -m venv venv
)

:: Activate virtual environment
echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat

:: Install requirements
echo [INFO] Checking and installing dependencies...
pip install -r requirements.txt

:: Check for .env file
if not exist ".env" (
    echo [INFO] .env file not found. Creating from .env.example...
    if exist ".env.example" (
        copy .env.example .env
        echo.
        echo [WARNING] A new .env file was created in the backend folder.
        echo [WARNING] Please open backend\.env and add your GROQ_API_KEY for the AI features to work.
        pause
    ) else (
        echo [ERROR] .env.example is missing!
    )
)

echo.
echo ==================================================
echo Starting FastAPI server...
echo The app will be available at http://localhost:8000
echo ==================================================
echo.
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

pause
