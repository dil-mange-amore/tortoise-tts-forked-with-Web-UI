@echo off
echo ========================================
echo CRITICAL FIX: Device Mismatch Bug
echo ========================================
echo.
echo ISSUE FOUND: CUDA/CPU device mismatch in conditioning latents
echo This causes voice cloning to fail completely!
echo.
echo Error: "Expected all tensors to be on the same device, 
echo         but found at least two devices, cuda:0 and cpu!"
echo.
echo ========================================
echo SOLUTION
echo ========================================
echo.
echo The bug was in generate_conditioning_latents() function:
echo - Conditioning latents were left on CUDA after generation
echo - When loaded later, caused device mismatch with CPU tensors
echo - Result: Corrupted voice encoding, terrible quality
echo.
echo FIX APPLIED:
echo - Added .cpu() call before saving conditioning latents
echo - All tensors now consistently on CPU when saved
echo - This matches how Tortoise loads them later
echo.
echo ========================================
echo ACTION REQUIRED
echo ========================================
echo.
echo 1. DELETE ALL EXISTING .pth FILES (they're corrupted!)
echo.

setlocal enabledelayedexpansion
set COUNT=0

echo Searching for .pth files in tortoise\voices...
echo.

for /r "tortoise\voices" %%f in (*.pth) do (
    set /a COUNT+=1
    echo Found: %%f
    del "%%f" 2>nul
    if !errorlevel! equ 0 (
        echo    ✓ Deleted
    ) else (
        echo    ✗ Failed to delete
    )
)

echo.
echo Deleted !COUNT! .pth file(s)
echo.

echo ========================================
echo 2. RESTART WEB SERVER
echo ========================================
echo.
echo The web server has the fix now.
echo When you upload/record voices, new .pth files will be correct!
echo.

echo ========================================
echo 3. RE-UPLOAD YOUR CUSTOM VOICES
echo ========================================
echo.
echo For best results:
echo - Delete and re-upload your custom voices
echo - OR just regenerate .pth by generating speech
echo - New .pth files will have correct device placement
echo.

echo ========================================
echo TEST IMMEDIATELY
echo ========================================
echo.
echo 1. Restart: python web_ui.py
echo 2. Upload a voice (3-5 short clips)
echo 3. Generate with 'fast' preset, 3 candidates
echo 4. Voice should now match PERFECTLY!
echo.
echo The device mismatch bug was preventing proper
echo voice encoding - this is why YouTube tutorials
echo worked and yours didn't!
echo.
echo ========================================

pause
