# Clean Restart Script for SpaceLink
Write-Host "Stopping all SpaceLink processes..." -ForegroundColor Yellow

# Kill all Python processes (be careful - this kills ALL Python processes)
Get-Process python -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowTitle -like "*SpaceLink*" -or $_.CommandLine -like "*uvicorn*" -or $_.CommandLine -like "*streamlit*" } | Stop-Process -Force -ErrorAction SilentlyContinue

# Wait a moment
Start-Sleep -Seconds 2

# Check if port 8000 is still in use
$port8000 = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
if ($port8000) {
    Write-Host "Port 8000 is still in use. Killing process..." -ForegroundColor Red
    $process = Get-Process -Id $port8000.OwningProcess -ErrorAction SilentlyContinue
    if ($process) {
        Stop-Process -Id $process.Id -Force
        Start-Sleep -Seconds 2
    }
}

# Check if port 8501 is still in use
$port8501 = Get-NetTCPConnection -LocalPort 8501 -ErrorAction SilentlyContinue
if ($port8501) {
    Write-Host "Port 8501 is still in use. Killing process..." -ForegroundColor Red
    $process = Get-Process -Id $port8501.OwningProcess -ErrorAction SilentlyContinue
    if ($process) {
        Stop-Process -Id $process.Id -Force
        Start-Sleep -Seconds 2
    }
}

Write-Host "All processes stopped. Ready to restart." -ForegroundColor Green

