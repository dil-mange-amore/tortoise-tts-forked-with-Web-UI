@echo off
REM Generate .pth files for all voices that don't have them yet

setlocal enabledelayedexpansion

set PYTHON_PATH=C:\Users\amolm\miniconda3\envs\tortoise\python.exe
set SCRIPT_PATH=tortoise\get_conditioning_latents.py
set VOICES_DIR=tortoise\voices

echo === Tortoise TTS - Batch .pth Generator ===
echo.

set /a PROCESSED=0
set /a SKIPPED=0
set /a FAILED=0

REM Loop through all voice directories
for /d %%V in (%VOICES_DIR%\*) do (
    set VOICE_NAME=%%~nxV
    set VOICE_PATH=%%V
    
    REM Check if .pth already exists
    if exist "%%V\!VOICE_NAME!.pth" (
        echo [SKIP] !VOICE_NAME! - .pth already exists
        set /a SKIPPED+=1
    ) else (
        REM Check if audio files exist
        set HAS_AUDIO=0
        if exist "%%V\*.wav" set HAS_AUDIO=1
        if exist "%%V\*.mp3" set HAS_AUDIO=1
        if exist "%%V\*.flac" set HAS_AUDIO=1
        
        if !HAS_AUDIO!==0 (
            echo [SKIP] !VOICE_NAME! - No audio files found
            set /a SKIPPED+=1
        ) else (
            echo [PROCESSING] !VOICE_NAME!...
            
            REM Generate .pth file
            "%PYTHON_PATH%" "%SCRIPT_PATH%" --voice "!VOICE_NAME!" --output_path "%%V"
            
            REM Check if successful
            if exist "%%V\!VOICE_NAME!.pth" (
                echo [SUCCESS] !VOICE_NAME! - Created .pth file
                set /a PROCESSED+=1
            ) else (
                echo [FAILED] !VOICE_NAME! - Could not create .pth file
                set /a FAILED+=1
            )
            echo.
        )
    )
)

echo === Summary ===
echo Processed: %PROCESSED%
echo Skipped: %SKIPPED%
echo Failed: %FAILED%
echo.
echo Done! Press any key to exit...
pause >nul
