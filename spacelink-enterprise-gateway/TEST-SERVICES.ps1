# Test SpaceLink Services
Write-Host "Testing SpaceLink Services..." -ForegroundColor Cyan
Write-Host ""

# Test API Gateway
Write-Host "Testing API Gateway (http://127.0.0.1:8000/health)..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://127.0.0.1:8000/health" -Method Get -TimeoutSec 3
    Write-Host "✓ API Gateway is RUNNING" -ForegroundColor Green
    $response | ConvertTo-Json
} catch {
    Write-Host "✗ API Gateway is NOT running: $_" -ForegroundColor Red
    Write-Host "  Start it with: .\start-api.ps1" -ForegroundColor Yellow
}

Write-Host ""

# Test Dashboard
Write-Host "Testing Dashboard (http://127.0.0.1:8501)..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://127.0.0.1:8501" -UseBasicParsing -TimeoutSec 3
    Write-Host "✓ Dashboard is RUNNING (Status: $($response.StatusCode))" -ForegroundColor Green
} catch {
    Write-Host "✗ Dashboard is NOT running: $_" -ForegroundColor Red
    Write-Host "  Start it with: .\start-dashboard.ps1" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Done!" -ForegroundColor Cyan

