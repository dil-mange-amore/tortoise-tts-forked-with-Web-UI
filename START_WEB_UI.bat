@echo off
echo ========================================
echo Starting Tortoise TTS Web UI
echo ========================================
echo.
echo Using conda environment: tortoise
echo.

call conda activate tortoise
if %errorlevel% neq 0 (
    echo Error: Could not activate tortoise environment
    pause
    exit /b 1
)

echo Environment activated!
echo Starting web server on http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

python web_ui.py

pause
