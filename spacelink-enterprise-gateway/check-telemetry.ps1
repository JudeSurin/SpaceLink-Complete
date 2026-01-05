# Check Telemetry Data
Write-Host "`nChecking Telemetry Data..." -ForegroundColor Cyan

try {
    # Authenticate
    $body = @{
        username = "enterprise_admin"
        password = "admin123"
    }
    $tokenResponse = Invoke-RestMethod -Uri "http://127.0.0.1:8000/v1/auth/token" -Method Post -Body $body -ContentType "application/x-www-form-urlencoded"
    $token = $tokenResponse.access_token
    
    # Get telemetry
    $headers = @{
        Authorization = "Bearer $token"
    }
    $telemetry = Invoke-RestMethod -Uri "http://127.0.0.1:8000/v1/telemetry/latest" -Method Get -Headers $headers -TimeoutSec 3
    
    if ($telemetry.Count -gt 0) {
        Write-Host "✓ SUCCESS! $($telemetry.Count) device(s) reporting telemetry:" -ForegroundColor Green
        $telemetry | ForEach-Object {
            Write-Host "  - $($_.device_id): $($_.status)" -ForegroundColor White
            Write-Host "    Latency: $($_.latency_ms)ms | Loss: $($_.packet_loss_percent)%" -ForegroundColor Gray
        }
    } else {
        Write-Host "⚠ No telemetry data yet. Devices may need more time to connect." -ForegroundColor Yellow
        Write-Host "  Make sure the device simulators are running in their PowerShell windows." -ForegroundColor Gray
    }
} catch {
    Write-Host "⚠ Error checking telemetry: $_" -ForegroundColor Yellow
}

Write-Host ""

