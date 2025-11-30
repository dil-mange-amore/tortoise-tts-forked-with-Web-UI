@echo off
echo ========================================
echo FIX: Apply Known Working Versions
echo ========================================
echo.
echo This script aligns critical dependencies with the officially supported versions.
echo It installs wheels verified for Python 3.10-3.11 on Windows.
echo.

call conda activate tortoise
if %errorlevel% neq 0 (
    echo Error: Could not activate tortoise environment
    pause
    exit /b 1
)

echo Current versions:
python -c "import sys; print('Python:', sys.version.split()[0])"
python -c "try: import numpy; print('NumPy:', numpy.__version__); except Exception as exc: print('NumPy: not installed -', exc)"
python -c "try: import librosa; print('librosa:', librosa.__version__); except Exception as exc: print('librosa: not installed -', exc)"
python -c "try: import numba; print('numba:', numba.__version__); except Exception as exc: print('numba: not installed -', exc)"
python -c "try: import llvmlite; print('llvmlite:', llvmlite.__version__); except Exception as exc: print('llvmlite: not installed -', exc)"

echo.
echo Step 1: Installing verified dependency set...
pip install --upgrade --no-cache-dir numpy==1.23.5 librosa==0.10.1 numba==0.59.1 llvmlite==0.42.0 soundfile==0.12.1 scipy==1.10.1

echo.
echo Step 2: Showing final versions...
python -c "import numpy; print('NumPy:', numpy.__version__)"
python -c "import librosa; print('librosa:', librosa.__version__)"
python -c "import numba; print('numba:', numba.__version__)"
python -c "import llvmlite; print('llvmlite:', llvmlite.__version__)"
python -c "import soundfile; print('soundfile:', soundfile.__version__)"

echo.
echo ========================================
echo DONE! Restart the web UI and test again!
echo ========================================
echo.
echo TIP: If you still see errors, ensure the latest NVIDIA drivers and ffmpeg binary are installed.
echo.
pause
