# LAGTER v1 API (Port 4010)

Dedicated API for LAGTER v1 industrial Excel exports.

## Endpoints

- `GET /health`
- `GET /api/lagter/v1/meta` (real-data metadata)
- `GET /api/lagter/v1/template` (schema only)
- `GET /api/lagter/v1/process-map`
- `GET /api/lagter/v1/export`

## Run (PowerShell)

```powershell
Set-Location "c:\Users\pc\Clisonix-cloud\clisonix.com"
$env:PORT="4010"
C:/Python313/python.exe "excel-core/run_lagter_v1_api.py"
```

## Quick test

```powershell
Set-Location "c:\Users\pc\Clisonix-cloud\clisonix.com"
$job = Start-Job -ScriptBlock { Set-Location "c:\Users\pc\Clisonix-cloud\clisonix.com"; $env:PORT="4010"; C:/Python313/python.exe "excel-core/run_lagter_v1_api.py" }
Start-Sleep -Seconds 2
(Invoke-WebRequest "http://127.0.0.1:4010/api/lagter/v1/meta" -UseBasicParsing).StatusCode
(Invoke-WebRequest "http://127.0.0.1:4010/api/lagter/v1/template" -UseBasicParsing).StatusCode
(Invoke-WebRequest "http://127.0.0.1:4010/api/lagter/v1/process-map" -UseBasicParsing).StatusCode
Stop-Job $job; Remove-Job $job
```
