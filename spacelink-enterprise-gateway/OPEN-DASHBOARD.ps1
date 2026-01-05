# Open SpaceLink Dashboard in Default Browser
Write-Host "Opening SpaceLink Dashboard..." -ForegroundColor Cyan

$dashboardUrl = "http://127.0.0.1:8501"

# Check if dashboard is running
try {
    $response = Invoke-WebRequest -Uri $dashboardUrl -UseBasicParsing -TimeoutSec 3
    Write-Host "✓ Dashboard is running!" -ForegroundColor Green
    Write-Host "Opening in browser: $dashboardUrl" -ForegroundColor Yellow
    
    # Open in default browser
    Start-Process $dashboardUrl
} catch {
    Write-Host "✗ Dashboard is not running!" -ForegroundColor Red
    Write-Host "Error: $_" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Please start the dashboard first:" -ForegroundColor Cyan
    Write-Host "  .\start-dashboard.ps1" -ForegroundColor White
    Write-Host "  OR" -ForegroundColor White
    Write-Host "  .\START-COMPLETE-SYSTEM.ps1" -ForegroundColor White
}

