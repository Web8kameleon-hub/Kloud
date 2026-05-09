# setup_Kloud.ps1 - Kloud Cloud Industrial Setup Script
# Author: Ledjan Ahmati
# License: Closed Source

Write-Host "ðŸš€ Kloud Cloud Industrial Setup Starting..."

# Step 1: Install Python dependencies
Write-Host "ðŸ“¦ Installing Python dependencies..."
pip install -r requirements.txt

# Step 2: Install Node.js dependencies
Write-Host "ðŸ“¦ Installing Node.js dependencies..."
npm install

# Step 3: Build Docker images
Write-Host "ðŸ”¨ Building Docker images..."
docker compose build

# Step 4: Start Docker services
Write-Host "ðŸ”„ Starting Docker services..."
docker compose up -d

Write-Host "✅ Setup complete! Kloud Cloud is ready to use."


