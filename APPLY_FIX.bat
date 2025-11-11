@echo off
echo ========================================
echo FIX: Apply Known Working Versions
echo ========================================
echo.
echo Based on online user guides, this will:
echo   1. Uninstall numba and llvmlite
echo   2. Install numpy 1.20.3
echo.
echo This is known to fix voice cloning quality issues!
echo.

call conda activate tortoise
if %errorlevel% neq 0 (
    echo Error: Could not activate tortoise environment
    pause
    exit /b 1
)

echo Current versions:
python -c "import sys; print('Python:', sys.version.split()[0])"
python -c "try: import numpy; print('NumPy:', numpy.__version__); except: print('NumPy: Not installed')"
python -c "try: import numba; print('numba:', numba.__version__); except: print('numba: Not installed')"
python -c "try: import llvmlite; print('llvmlite:', llvmlite.__version__); except: print('llvmlite: Not installed')"

echo.
echo Step 1: Uninstalling numba and llvmlite...
pip uninstall numba llvmlite -y

echo.
echo Step 2: Installing numpy 1.20.3...
pip install numpy==1.20.3

echo.
echo ========================================
echo New versions:
python -c "import numpy; print('NumPy:', numpy.__version__)"
python -c "try: import numba; print('numba:', numba.__version__); except: print('numba: Not installed (GOOD!)')"

echo.
echo ========================================
echo DONE! Restart the web UI and test again!
echo ========================================
echo.
echo These versions are known to fix voice cloning issues.
echo If still not working, the issue is likely audio quality/quantity.
echo.
pause
