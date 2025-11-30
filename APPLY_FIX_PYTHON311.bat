@echo off
echo ========================================
echo FIX: Apply Compatible Versions for Python 3.11
echo ========================================
echo.
echo Python 3.11 needs compatible wheels for librosa/numba.
echo This script installs the tested versions for TorToiSe.
echo.

call conda activate tortoise
if %errorlevel% neq 0 (
    echo Error: Could not activate tortoise environment
    pause
    exit /b 1
)

echo Current Python version:
python -c "import sys; print('Python:', sys.version.split()[0])"

echo.
echo Installing verified wheels...
pip install --upgrade --no-cache-dir numpy==1.23.5 librosa==0.10.1 numba==0.59.1 llvmlite==0.42.0 soundfile==0.12.1 scipy==1.10.1

echo.
echo Installed versions:
python -c "import numpy; print('NumPy:', numpy.__version__)"
python -c "import librosa; print('librosa:', librosa.__version__)"
python -c "import numba; print('numba:', numba.__version__)"
python -c "import llvmlite; print('llvmlite:', llvmlite.__version__)"
python -c "import soundfile; print('soundfile:', soundfile.__version__)"

echo.
echo ========================================
echo DONE! Restart the web UI to test:
echo   .\START_WEB_UI.bat
echo ========================================
pause
