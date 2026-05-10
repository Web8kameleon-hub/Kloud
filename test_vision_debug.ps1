# Debug vision endpoint - test POST with error handling
param([string]$Url = "http://127.0.0.1:9999/api/v1/vision/analyze")

Write-Host "Testing: $Url" -ForegroundColor Cyan

$imageBase64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
$payload = @{
    image_base64 = $imageBase64
    prompt       = "Test"
} | ConvertTo-Json -Compress

Write-Host "Sending POST request...`n" -ForegroundColor Yellow

# Use Invoke-RestMethod which handles JSON automatically  
try {
    $response = Invoke-RestMethod -Uri $Url `
        -Method POST `
        -Body $payload `
        -ContentType "application/json" `
        -TimeoutSec 120 `
        -ErrorAction Stop
    
    Write-Host "Success! Response:" -ForegroundColor Green
    Write-Host ($response | ConvertTo-Json -Depth 10) -ForegroundColor White
    
    # Check for nanogrid
    $responseStr = $response | ConvertTo-Json
    if ($responseStr -like "*nanogrid*" -or $responseStr -like "*zeiss*") {
        Write-Host "`nNANOGRID-ZEISS CONFIRMED!" -ForegroundColor Green
    }
    
}
catch {
    $statusCode = $_.Exception.Response.StatusCode.value__
    Write-Host "HTTP Status Code: $statusCode" -ForegroundColor Yellow
    
    # For error responses, try to read the content
    try {
        $errStream = $_.Exception.Response.GetResponseStream()
        $reader = New-Object System.IO.StreamReader($errStream)
        $errContent = $reader.ReadToEnd()
        $reader.Dispose()
        
        Write-Host "`nError Response Body:" -ForegroundColor Red
        Write-Host $errContent -ForegroundColor White
        
        # Check if nanogrid appears in error message
        if ($errContent -like "*nanogrid*" -or $errContent -like "*zeiss*") {
            Write-Host "`nNANOGRID-ZEISS REFERENCE FOUND IN ERROR = Model targeting IS ACTIVE!" -ForegroundColor Green
        }
    }
    catch {
        Write-Host "Could not read response body: $($_.Exception.Message)" -ForegroundColor Gray
    }
}

Write-Host "`nTest complete." -ForegroundColor Cyan
