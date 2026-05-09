Write-Host "[1] Starting PostgreSQL..." -ForegroundColor Green
docker run -d --rm --name pg-dev -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=kloud -p 5432:5432 postgres:16-alpine
Start-Sleep -Seconds 5

Write-Host "[2] Starting Redis..." -ForegroundColor Green
docker run -d --rm --name redis-dev -p 6379:6379 redis:7-alpine
Start-Sleep -Seconds 2

Write-Host "[3] Starting Backend API (localhost:8000)..." -ForegroundColor Yellow
Start-Process pwsh -ArgumentList "-NoExit", "-Command", "cd c:\Users\Admin\Desktop\neurosonix-cloud\apps\api; npm run dev"
Start-Sleep -Seconds 3

Write-Host "[4] Starting Frontend (localhost:3000)..." -ForegroundColor Yellow
Start-Process pwsh -ArgumentList "-NoExit", "-Command", "cd c:\Users\Admin\Desktop\neurosonix-cloud\apps\web; npm run dev"
Start-Sleep -Seconds 3

Write-Host "=========================================="
Write-Host "[OK] LOCAL DEVELOPMENT STARTED"
Write-Host "=========================================="
Write-Host "Services:"
Write-Host "  PostgreSQL -> localhost:5432"
Write-Host "  Redis      -> localhost:6379"
Write-Host "  Backend    -> localhost:8000"
Write-Host "  Frontend   -> localhost:3000"
Write-Host ""
Write-Host "Test: curl http://localhost:8000/health"
Write-Host "Stop: docker stop pg-dev redis-dev"
Write-Host "=========================================="

Read-Host "Press Enter to exit"

