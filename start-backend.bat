@echo off
echo ================================
echo Starting Sherlock.ai Backend
echo ================================
echo.

cd /d D:\Sherlock.ai\backend

echo [1/3] Checking Python installation...
python --version
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Please install Python from https://www.python.org/
    pause
    exit /b 1
)
echo.

echo [2/3] Checking dependencies...
python -c "import fastapi, uvicorn, torch" 2>nul
if errorlevel 1 (
    echo WARNING: Some dependencies missing!
    echo Installing requirements...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies!
        pause
        exit /b 1
    )
)
echo Dependencies OK
echo.

echo [3/3] Starting FastAPI server...
echo Backend will be available at: http://127.0.0.1:8000
echo Press CTRL+C to stop the server
echo.
echo ================================
echo.

python app.py

if errorlevel 1 (
    echo.
    echo ================================
    echo ERROR: Backend failed to start!
    echo ================================
    echo.
    pause
)
