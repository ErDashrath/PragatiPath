@echo off
REM DKT Microservice Startup Script for Windows

echo ====================================================
echo DKT Microservice Startup
echo ====================================================

REM Change to the DKT service directory
cd /d "%~dp0"

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

REM Install dependencies
echo Installing dependencies...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

if errorlevel 1 (
    echo Error: Failed to install dependencies
    pause
    exit /b 1
)

REM Start the service
echo.
echo Starting DKT microservice...
echo Service will be available at: http://localhost:8001
echo Press Ctrl+C to stop the service
echo.

REM Start with reload for development
python -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload

pause