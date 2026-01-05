# SpaceLink Enterprise Gateway - Complete System Startup
# This script starts all services and telemetry sources

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "SpaceLink Enterprise Gateway" -ForegroundColor Cyan
Write-Host "Starting Complete System..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

# 1. Start API Gateway
Write-Host "[1/5] Starting API Gateway..." -ForegroundColor Yellow
Set-Location "$scriptPath\api-gateway"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; Write-Host 'SpaceLink API Gateway' -ForegroundColor Green; python -m uvicorn app.main:app --host 127.0.0.1 --port 8000" -WindowStyle Normal
Start-Sleep -Seconds 3

# 2. Start Dashboard
Write-Host "[2/5] Starting Dashboard..." -ForegroundColor Yellow
Set-Location $scriptPath
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; Write-Host 'SpaceLink Dashboard' -ForegroundColor Green; python -m streamlit run dashboard.py --server.port 8501 --server.address 0.0.0.0" -WindowStyle Normal
Start-Sleep -Seconds 3

# 3. Start Telemetry Agent
Write-Host "[3/5] Starting Telemetry Agent..." -ForegroundColor Yellow
Set-Location "$scriptPath\telemetry-agent"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; Write-Host 'Telemetry Agent (device-001)' -ForegroundColor Green; python agent.py" -WindowStyle Normal
Start-Sleep -Seconds 2

# 4. Start Satellite Terminal
Write-Host "[4/5] Starting Satellite Terminal..." -ForegroundColor Yellow
Set-Location "$scriptPath\devices"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; Write-Host 'Satellite Terminal (sat-001)' -ForegroundColor Green; python satellite_terminal.py" -WindowStyle Normal
Start-Sleep -Seconds 2

# 5. Start Mobile Unit
Write-Host "[5/5] Starting Mobile Unit..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; Write-Host 'Mobile Unit (mobile-001)' -ForegroundColor Green; python mobile_unit.py" -WindowStyle Normal
Start-Sleep -Seconds 2

Set-Location $scriptPath

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "All Services Started!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Access Points:" -ForegroundColor Cyan
Write-Host "  Dashboard:    http://127.0.0.1:8501  (NOT 0.0.0.0!)" -ForegroundColor White
Write-Host "  API Gateway:  http://127.0.0.1:8000" -ForegroundColor White
Write-Host "  API Docs:     http://127.0.0.1:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "⚠️  IMPORTANT: Use 127.0.0.1 or localhost, NOT 0.0.0.0!" -ForegroundColor Yellow
Write-Host "   Opening dashboard in browser..." -ForegroundColor Cyan
Start-Sleep -Seconds 2
Start-Process "http://127.0.0.1:8501"
Write-Host ""
Write-Host "Telemetry Sources Running:" -ForegroundColor Cyan
Write-Host "  ✓ Telemetry Agent (device-001)" -ForegroundColor Green
Write-Host "  ✓ Satellite Terminal (sat-001)" -ForegroundColor Green
Write-Host "  ✓ Mobile Unit (mobile-001)" -ForegroundColor Green
Write-Host ""
Write-Host "Note: Data will start appearing in the dashboard within 5-10 seconds" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press any key to exit this window (services will continue running)..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

