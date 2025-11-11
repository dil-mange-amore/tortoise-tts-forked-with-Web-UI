@echo off
echo ========================================
echo FIX: Apply Compatible Versions for Python 3.11
echo ========================================
echo.
echo Python 3.11 needs different numpy versions
echo Using numpy 1.23.5 (closest stable to 1.20.3 for Python 3.11)
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
echo Step 1: Uninstalling problematic packages...
pip uninstall numba llvmlite -y

echo.
echo Step 2: Installing numpy 1.23.5 (compatible with Python 3.11)...
pip install numpy==1.23.5

echo.
echo ========================================
echo Installed versions:
python -c "import numpy; print('NumPy:', numpy.__version__)"
python -c "try: import numba; print('numba:', numba.__version__); except: print('numba: Not installed (GOOD!)')"
python -c "try: import llvmlite; print('llvmlite:', llvmlite.__version__); except: print('llvmlite: Not installed (GOOD!)')"

echo.
echo ========================================
echo DONE! Restart the web UI to test:
echo   .\START_WEB_UI.bat
echo ========================================
pause
