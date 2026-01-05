# SpaceLink Dashboard Startup Script
$ErrorActionPreference = "Stop"

Write-Host "Starting SpaceLink Dashboard..." -ForegroundColor Green

Set-Location $PSScriptRoot

# Start Dashboard
Start-Process python -ArgumentList "-m", "streamlit", "run", "dashboard.py", "--server.port", "8501", "--server.address", "0.0.0.0" -WindowStyle Normal

Write-Host "Dashboard starting on http://127.0.0.1:8501" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press any key to continue..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

