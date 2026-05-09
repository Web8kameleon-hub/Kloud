#!/usr/bin/env pwsh
# 🔐 GitHub Secrets Setup Script
# Usage: ./setup-github-secrets.ps1

Write-Host "🔐 KLOUD CLOUD - GITHUB SECRETS SETUP" -ForegroundColor Cyan
Write-Host ""
Write-Host "⚠️  MANUAL STEP REQUIRED - Cannot set secrets programmatically" -ForegroundColor Yellow
Write-Host ""
Write-Host "Follow these steps to set GitHub Secrets:" -ForegroundColor Green
Write-Host ""
Write-Host "1. Open: https://github.com/LedjanAhmati/Kloud-cloud/settings/secrets/actions" -ForegroundColor White
Write-Host ""
Write-Host "2. Click 'New repository secret' and add these CRITICAL variables:" -ForegroundColor White
Write-Host ""

$secrets = @(
    @{Name="DB_HOST"; Value="localhost or your database IP"; Required=$true},
    @{Name="DB_USER"; Value="kloud"; Required=$true},
    @{Name="DB_PASSWORD"; Value="your-secure-password"; Required=$true},
    @{Name="JWT_SECRET"; Value="random-string-32-chars-or-more"; Required=$true},
    @{Name="STRIPE_API_KEY"; Value="sk_test_..."; Required=$false},
    @{Name="SENTRY_DSN"; Value="https://..."; Required=$false}
)

foreach ($secret in $secrets) {
    $indicator = if ($secret.Required) { "🔴 CRITICAL" } else { "🟡 OPTIONAL" }
    Write-Host "   $indicator - $($secret.Name)" -ForegroundColor Yellow
    Write-Host "      Example: $($secret.Value)" -ForegroundColor Gray
    Write-Host ""
}

Write-Host "3. After adding secrets:" -ForegroundColor White
Write-Host "   • Make a test commit (even empty): git commit --allow-empty -m 'test: CI trigger'" -ForegroundColor Gray
Write-Host "   • Push: git push origin main" -ForegroundColor Gray
Write-Host "   • Monitor: GitHub → Actions tab" -ForegroundColor Gray
Write-Host ""
Write-Host "✅ When setup is complete, CI will pass all security checks!" -ForegroundColor Green

