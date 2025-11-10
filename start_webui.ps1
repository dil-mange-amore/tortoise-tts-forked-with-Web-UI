# Tortoise TTS Web UI Starter (PowerShell)
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Tortoise TTS Web UI" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if conda is available
$condaCmd = Get-Command conda -ErrorAction SilentlyContinue
if (-not $condaCmd) {
    Write-Host "ERROR: Conda not found in PATH" -ForegroundColor Red
    Write-Host "Please install Miniconda or Anaconda first" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Activate conda environment
Write-Host "Activating tortoise environment..." -ForegroundColor Yellow

# Initialize conda for PowerShell
& conda shell.powershell hook | Out-String | Invoke-Expression

# Activate the environment
conda activate tortoise

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Could not activate tortoise environment" -ForegroundColor Red
    Write-Host "Please run the installation first" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Start the web UI
Write-Host ""
Write-Host "Starting Tortoise TTS Web UI..." -ForegroundColor Green
Write-Host "Web interface will be available at: http://localhost:5000" -ForegroundColor Cyan
Write-Host "Output folder: $env:USERPROFILE\Music\Tortoise Output" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the service" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

python web_ui.py

Read-Host "Press Enter to exit"
