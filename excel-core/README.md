# Excel Core - L.A.G.T.E.R v1

Ky modul ofron eksport industrial `LAGTER v1` në Excel me tabela + skica dhe API endpoints për procese.

## Çfarë përfshin

- `lagter_v1_excel.py`: Builder kryesor i workbook-it.
- `lagter_v1_models.py`: Modele Pydantic për validim payload-i.
- `excel_reporting_api.py`: API FastAPI me endpoint-e për meta/template/process/export.
- `run_lagter_v1_export.py`: Runner i shpejtë për eksport lokal.
- `test_lagter_v1.py`: Test-harness minimal për smoke test.

## Endpoint-et e LAGTER v1

- `GET /api/lagter/v1/meta`
- `GET /api/lagter/v1/template`
- `GET /api/lagter/v1/process-map`
- `GET /api/lagter/v1/export`
- `POST /api/lagter/v1/export/custom`

## Quick Start (Windows / pwsh)

```powershell
Set-Location "c:\Users\pc\Kloud-cloud\kloud.com"
C:/Python313/python.exe -m pip install -r "excel-core/requirements.txt"
C:/Python313/python.exe "excel-core/run_lagter_v1_export.py"
```

## API Run

```powershell
Set-Location "c:\Users\pc\Kloud-cloud\kloud.com\excel-core"
C:/Python313/python.exe "excel_reporting_api.py"
```

## Smoke Test

```powershell
Set-Location "c:\Users\pc\Kloud-cloud\kloud.com"
C:/Python313/python.exe "excel-core/test_lagter_v1.py"
```

