@echo off
echo ================================================
echo Voice Cloning Quality Fix Script
echo ================================================
echo.

REM Activate conda environment
call conda activate tortoise

echo Step 1: Diagnosing current voice quality...
echo.
python diagnose_voice.py Amol
echo.

echo Step 2: Delete old .pth file to regenerate...
if exist "tortoise\voices\Amol\Amol.pth" (
    del "tortoise\voices\Amol\Amol.pth"
    echo ✓ Deleted old Amol.pth
) else (
    echo - No .pth file to delete
)
echo.

echo Step 3: Reprocess all audio files with DC offset removal...
echo.
echo IMPORTANT: Please restart web_ui.py and re-upload your voice
echo The new code will:
echo   - Remove DC offset (center audio around zero)
echo   - Proper normalization to [-1, 1]
echo   - Verify both positive and negative values exist
echo.

echo ================================================
echo Next Steps:
echo ================================================
echo 1. Stop the web server (Ctrl+C)
echo 2. Run: python web_ui.py
echo 3. Go to "Manage Voices" → "Record Voice" 
echo 4. Record 7-10 new clips OR re-upload your audio files
echo 5. The system will automatically fix the audio
echo 6. Try generating with 'fast' or 'standard' preset
echo ================================================
echo.

pause
