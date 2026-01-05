# Check SpaceLink Services Status
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "SpaceLink Enterprise Gateway Status" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Check API Gateway
Write-Host "Checking API Gateway..." -ForegroundColor Yellow
try {
    $api = Invoke-RestMethod -Uri "http://127.0.0.1:8000/health" -Method Get -TimeoutSec 3
    Write-Host "✓ API Gateway: RUNNING" -ForegroundColor Green
    Write-Host "  Status: $($api.status)" -ForegroundColor Gray
    Write-Host "  Service: $($api.service)" -ForegroundColor Gray
    $apiRunning = $true
} catch {
    Write-Host "✗ API Gateway: Not responding" -ForegroundColor Red
    Write-Host "  Error: $_" -ForegroundColor Gray
    $apiRunning = $false
}

Write-Host ""

# Check Dashboard
Write-Host "Checking Dashboard..." -ForegroundColor Yellow
try {
    $dash = Invoke-WebRequest -Uri "http://127.0.0.1:8501" -UseBasicParsing -TimeoutSec 3
    Write-Host "✓ Dashboard: RUNNING (Status: $($dash.StatusCode))" -ForegroundColor Green
    $dashRunning = $true
} catch {
    Write-Host "✗ Dashboard: Not responding" -ForegroundColor Red
    Write-Host "  Error: $_" -ForegroundColor Gray
    $dashRunning = $false
}

Write-Host ""

# Check Telemetry Data
if ($apiRunning) {
    Write-Host "Checking Telemetry Data..." -ForegroundColor Yellow
    try {
        $body = @{
            username = "enterprise_admin"
            password = "admin123"
        }
        $tokenResponse = Invoke-RestMethod -Uri "http://127.0.0.1:8000/v1/auth/token" -Method Post -Body $body -ContentType "application/x-www-form-urlencoded"
        $token = $tokenResponse.access_token
        $headers = @{
            Authorization = "Bearer $token"
        }
        $telemetry = Invoke-RestMethod -Uri "http://127.0.0.1:8000/v1/telemetry/latest" -Method Get -Headers $headers -TimeoutSec 3
        Write-Host "✓ Telemetry Data: $($telemetry.Count) devices reporting" -ForegroundColor Green
        if ($telemetry.Count -gt 0) {
            Write-Host "  Devices:" -ForegroundColor Gray
            foreach ($device in $telemetry) {
                Write-Host "    - $($device.device_id): $($device.status)" -ForegroundColor Gray
            }
        }
    } catch {
        Write-Host "⚠ Telemetry Data: No data yet (devices may still be connecting)" -ForegroundColor Yellow
    }
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Access Points:" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "API Gateway:    http://127.0.0.1:8000" -ForegroundColor White
Write-Host "API Docs:       http://127.0.0.1:8000/docs" -ForegroundColor White
Write-Host "Dashboard:      http://127.0.0.1:8501" -ForegroundColor White
Write-Host "`n"

