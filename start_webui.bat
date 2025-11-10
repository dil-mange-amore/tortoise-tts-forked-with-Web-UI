@echo off
REM Tortoise TTS Web UI Starter
echo ========================================
echo    Tortoise TTS Web UI
echo ========================================
echo.

REM Check if conda environment exists
where conda >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Conda not found in PATH
    echo Please install Miniconda or Anaconda first
    pause
    exit /b 1
)

REM Activate conda environment
echo Activating tortoise environment...
call conda activate tortoise

if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Could not activate tortoise environment
    echo Please run the installation first
    pause
    exit /b 1
)

REM Start the web UI
echo.
echo Starting Tortoise TTS Web UI...
echo Web interface will be available at: http://localhost:5000
echo Output folder: %USERPROFILE%\Music\Tortoise Output
echo.
echo Press Ctrl+C to stop the service
echo ========================================
echo.

python web_ui.py

pause
