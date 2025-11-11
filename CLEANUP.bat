@echo off
echo ========================================
echo CLEANUP: Remove Temporary Files
echo ========================================
echo.
echo This will delete temporary scripts and documentation we created
echo during troubleshooting.
echo.
echo Files to be deleted:
echo.

echo BAT Scripts:
echo   - fix_device_mismatch.bat
echo   - FIX_NUMPY.bat
echo   - FIX_NUMPY_COMPAT.bat
echo   - fix_voice_quality.bat
echo   - REVERT_PACKAGES.bat
echo   - SETUP_PYTHON39.bat
echo   - start_webui.bat
echo   - start_webui.ps1
echo.

echo Python Scripts:
echo   - check_audio_quality.py
echo   - diagnose_voice.py
echo   - fix_voice_normalization.py
echo   - quick_diagnose.py
echo   - test_audio_normalization.py
echo   - test_generation.py
echo   - test_normalization.py
echo   - test_pth_quality.py
echo.

echo Documentation:
echo   - PROGRESS_MONITORING.md
echo   - QUICK_START.md
echo   - SOUNDFILE_FIX.md
echo   - SPEED_GUIDE.md
echo   - TROUBLESHOOTING_RESULTS.md
echo   - VERSION_COMPATIBILITY.md
echo   - VOICE_CLONING_FIX.md
echo   - VOICE_CLONING_FIXED_README.md
echo   - VOICE_CLONING_GUIDE.md
echo   - VOICE_CLONING_IMPLEMENTATION.md
echo   - VOICE_CLONING_TROUBLESHOOTING.md
echo   - WEB_UI_README.md
echo.

echo Other:
echo   - test_output.wav
echo   - test.wav (if exists)
echo.

set /p CONFIRM="Are you sure you want to delete these files? (Y/N): "
if /i not "%CONFIRM%"=="Y" (
    echo Cleanup cancelled.
    pause
    exit /b 0
)

echo.
echo Deleting files...
echo.

REM BAT scripts
del /q fix_device_mismatch.bat 2>nul
del /q FIX_NUMPY.bat 2>nul
del /q FIX_NUMPY_COMPAT.bat 2>nul
del /q fix_voice_quality.bat 2>nul
del /q REVERT_PACKAGES.bat 2>nul
del /q SETUP_PYTHON39.bat 2>nul
del /q start_webui.bat 2>nul
del /q start_webui.ps1 2>nul

REM Python scripts
del /q check_audio_quality.py 2>nul
del /q diagnose_voice.py 2>nul
del /q fix_voice_normalization.py 2>nul
del /q quick_diagnose.py 2>nul
del /q test_audio_normalization.py 2>nul
del /q test_generation.py 2>nul
del /q test_normalization.py 2>nul
del /q test_pth_quality.py 2>nul

REM Documentation
del /q PROGRESS_MONITORING.md 2>nul
del /q QUICK_START.md 2>nul
del /q SOUNDFILE_FIX.md 2>nul
del /q SPEED_GUIDE.md 2>nul
del /q TROUBLESHOOTING_RESULTS.md 2>nul
del /q VERSION_COMPATIBILITY.md 2>nul
del /q VOICE_CLONING_FIX.md 2>nul
del /q VOICE_CLONING_FIXED_README.md 2>nul
del /q VOICE_CLONING_GUIDE.md 2>nul
del /q VOICE_CLONING_IMPLEMENTATION.md 2>nul
del /q VOICE_CLONING_TROUBLESHOOTING.md 2>nul
del /q WEB_UI_README.md 2>nul

REM Test files
del /q test_output.wav 2>nul
del /q test.wav 2>nul

echo.
echo ========================================
echo CLEANUP COMPLETE!
echo ========================================
echo.
echo Files kept (essential):
echo   - web_ui.py (main web interface)
echo   - START_WEB_UI.bat (to start the server)
echo   - templates/index.html (web UI template)
echo   - generate_all_pth manually.bat (utility)
echo.
echo To start Tortoise TTS:
echo   START_WEB_UI.bat
echo.
pause
