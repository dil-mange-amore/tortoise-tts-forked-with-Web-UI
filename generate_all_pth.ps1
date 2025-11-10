# Generate .pth files for all voices that don't have them yet
# This script checks each voice folder and creates conditioning latents

$pythonPath = "C:\Users\amolm\miniconda3\envs\tortoise\python.exe"
$scriptPath = "tortoise\get_conditioning_latents.py"
$voicesDir = "tortoise\voices"

Write-Host "=== Tortoise TTS - Batch .pth Generator ===" -ForegroundColor Cyan
Write-Host ""

# Get all subdirectories in voices folder
$voiceFolders = Get-ChildItem -Path $voicesDir -Directory

$processed = 0
$skipped = 0
$failed = 0

foreach ($folder in $voiceFolders) {
    $voiceName = $folder.Name
    $voicePath = $folder.FullName
    
    # Check if .pth file already exists
    $pthFile = Join-Path $voicePath "$voiceName.pth"
    
    if (Test-Path $pthFile) {
        Write-Host "[SKIP] $voiceName - .pth already exists" -ForegroundColor Yellow
        $skipped++
        continue
    }
    
    # Check if folder has audio files
    $audioFiles = Get-ChildItem -Path $voicePath -Include *.wav,*.mp3,*.flac -File
    
    if ($audioFiles.Count -eq 0) {
        Write-Host "[SKIP] $voiceName - No audio files found" -ForegroundColor Gray
        $skipped++
        continue
    }
    
    Write-Host "[PROCESSING] $voiceName - Found $($audioFiles.Count) audio files" -ForegroundColor Green
    
    # Run the conditioning latents script
    $command = "& `"$pythonPath`" `"$scriptPath`" --voice `"$voiceName`" --output_path `"$voicePath`""
    
    try {
        Invoke-Expression $command
        
        if (Test-Path $pthFile) {
            Write-Host "[SUCCESS] $voiceName - Created $voiceName.pth" -ForegroundColor Green
            $processed++
        } else {
            Write-Host "[FAILED] $voiceName - .pth file not created" -ForegroundColor Red
            $failed++
        }
    } catch {
        Write-Host "[ERROR] $voiceName - $($_.Exception.Message)" -ForegroundColor Red
        $failed++
    }
    
    Write-Host ""
}

# Summary
Write-Host "=== Summary ===" -ForegroundColor Cyan
Write-Host "Processed: $processed" -ForegroundColor Green
Write-Host "Skipped: $skipped" -ForegroundColor Yellow
Write-Host "Failed: $failed" -ForegroundColor Red
Write-Host ""
Write-Host "Done! Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
