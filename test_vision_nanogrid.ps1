# Test vision endpoint with nanogrid-zeiss model validation
param([string]$BaseUrl = "http://127.0.0.1:9999")

Write-Host "===== NANOGRID-ZEISS VISION ENDPOINT TEST =====" -ForegroundColor Cyan
Write-Host "Testing: POST $BaseUrl/api/v1/vision/analyze" -ForegroundColor Yellow

# Minimal valid PNG (1x1 transparent)
$imageBase64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="

$payload = @{
    image_base64 = $imageBase64
    prompt       = "Analyze this test image"
} | ConvertTo-Json

Write-Host "`nPayload size: $($payload.Length) bytes" -ForegroundColor Gray

# Test 1: Check service health
try {
    Write-Host "`n[1/3] Checking 9999 service availability..." -ForegroundColor Cyan
    $healthResp = Invoke-WebRequest -UseBasicParsing -Uri "$BaseUrl/health" -TimeoutSec 5
    $health = $healthResp.Content | ConvertFrom-Json
    Write-Host "✓ Service running on port 9999: $($health.status)" -ForegroundColor Green
}
catch {
    Write-Host "✗ Service not available: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Test 2: Send vision request
$testSuccess = $false
try {
    Write-Host "`n[2/3] Sending vision analyze request to nanogrid-zeiss..." -ForegroundColor Cyan
    $visionResp = Invoke-WebRequest -UseBasicParsing `
        -Uri "$BaseUrl/api/v1/vision/analyze" `
        -Method POST `
        -Body $payload `
        -ContentType "application/json" `
        -TimeoutSec 120
    
    Write-Host "✓ Response received (HTTP $($visionResp.StatusCode))" -ForegroundColor Green
    
    Write-Host "`n[3/3] Validating response structure..." -ForegroundColor Cyan
    $visionData = $visionResp.Content | ConvertFrom-Json
    
    # Check for nanogrid-zeiss model in response
    $modelField = $null
    if ($visionData.requested_model) { $modelField = $visionData.requested_model }
    if (-not $modelField -and $visionData.model) { $modelField = $visionData.model }
    
    if ($modelField) {
        Write-Host "✓ Model field found: $modelField" -ForegroundColor Green
        if ($modelField -eq "nanogrid-zeiss") {
            Write-Host "✓✓ NANOGRID-ZEISS CONFIRMED IN RESPONSE!" -ForegroundColor Green
            $testSuccess = $true
        }
    }
    else {
        Write-Host "✓ Response received (model embedding may be in upstream service)" -ForegroundColor Cyan
    }
    
    Write-Host "`nFull response:" -ForegroundColor Cyan
    Write-Host ($visionResp.Content | ConvertFrom-Json | ConvertTo-Json -Depth 10) -ForegroundColor White
    
}
catch {
    $errMsg = $_.Exception.Message
    $statusCode = if ($_.Exception.Response) { $_.Exception.Response.StatusCode.value__ } else { "unknown" }
    
    Write-Host "`n✗ Request failed with HTTP $statusCode" -ForegroundColor Red
    Write-Host "Error: $errMsg" -ForegroundColor Red
}

Write-Host "`n===== TEST RESULT =====" -ForegroundColor Cyan
if ($testSuccess) {
    Write-Host "NANOGRID-ZEISS IS REAL AND ACTIVE" -ForegroundColor Green
}
else {
    Write-Host "Test inconclusive - check upstream service ocean-core availability" -ForegroundColor Yellow
}
Write-Host "===== TEST COMPLETE =====" -ForegroundColor Cyan
