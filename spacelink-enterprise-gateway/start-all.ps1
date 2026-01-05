# SpaceLink Enterprise Gateway - Start All Services
$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "SpaceLink Enterprise Gateway" -ForegroundColor Cyan
Write-Host "Starting all services..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Start API Gateway
Write-Host "[1/2] Starting API Gateway..." -ForegroundColor Yellow
Set-Location "$PSScriptRoot\api-gateway"
Start-Process python -ArgumentList "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000" -WindowStyle Normal
Start-Sleep -Seconds 2

# Start Dashboard
Write-Host "[2/2] Starting Dashboard..." -ForegroundColor Yellow
Set-Location $PSScriptRoot
Start-Process python -ArgumentList "-m", "streamlit", "run", "dashboard.py", "--server.port", "8501", "--server.address", "0.0.0.0" -WindowStyle Normal
Start-Sleep -Seconds 2

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Services Started!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "API Gateway:    http://127.0.0.1:8000" -ForegroundColor White
Write-Host "API Docs:      http://127.0.0.1:8000/docs" -ForegroundColor White
Write-Host "Dashboard:     http://127.0.0.1:8501" -ForegroundColor White
Write-Host ""
Write-Host "Test Credentials:" -ForegroundColor Cyan
Write-Host "  Admin:    enterprise_admin / admin123" -ForegroundColor Gray
Write-Host "  Partner:  acme_partner / partner123" -ForegroundColor Gray
Write-Host "  Customer: customer_user / customer123" -ForegroundColor Gray
Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

