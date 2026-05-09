# deploy.ps1 - Kloud Cloud Industrial Deployment Script
# Author: Ledjan Ahmati
# License: Closed Source

Write-Host "ðŸš€ Kloud Cloud Industrial Deployment Starting..."

# Step 1: Build Docker images
Write-Host "ðŸ”¨ Building Docker images..."
docker compose build

# Step 2: Restart Docker services
Write-Host "ðŸ”„ Restarting Docker services..."
docker compose up -d

# Step 3: Health check (optional)
# You can add health check logic here if needed

Write-Host "âœ… Deployment complete!"


