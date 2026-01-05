# SpaceLink API Gateway Startup Script
$ErrorActionPreference = "Stop"

Write-Host "Starting SpaceLink API Gateway..." -ForegroundColor Green

Set-Location "$PSScriptRoot\api-gateway"

# Start API Gateway
Start-Process python -ArgumentList "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000" -WindowStyle Normal

Write-Host "API Gateway starting on http://127.0.0.1:8000" -ForegroundColor Yellow
Write-Host "API Documentation: http://127.0.0.1:8000/docs" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press any key to continue..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

