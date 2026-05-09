# =====================================================
# INITIALIZE DOCKER SECRETS
# =====================================================
# Krijon secrets directory dhe gjeneron passwords
# Usage: .\scripts\init-secrets.ps1
# =====================================================

Write-Host "🔐 Initializing Docker Secrets..." -ForegroundColor Cyan

# Krijo secrets directory
$secretsDir = ".\secrets"
if (-not (Test-Path $secretsDir)) {
    New-Item -ItemType Directory -Path $secretsDir | Out-Null
    Write-Host "✓ Created secrets directory" -ForegroundColor Green
}

# Function për të gjeneruar password të fortë
function New-SecurePassword {
    param(
        [int]$Length = 32
    )
    $chars = "ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz23456789!@#$%^&*"
    $password = -join ((1..$Length) | ForEach-Object { $chars[(Get-Random -Maximum $chars.Length)] })
    return $password
}

# Function për të krijuar secret file
function New-SecretFile {
    param(
        [string]$Name,
        [string]$Value
    )
    $path = Join-Path $secretsDir "$Name.txt"
    
    if (Test-Path $path) {
        Write-Host "⚠️  $Name already exists, skipping..." -ForegroundColor Yellow
        return
    }
    
    $Value | Out-File -FilePath $path -NoNewline -Encoding ASCII
    Write-Host "✓ Created secret: $Name" -ForegroundColor Green
}

# Krijo të gjitha secrets
Write-Host "`n📝 Generating secure passwords..." -ForegroundColor Yellow

New-SecretFile -Name "postgres_password" -Value (New-SecurePassword)
New-SecretFile -Name "postgres_user" -Value "kloud"
New-SecretFile -Name "redis_password" -Value (New-SecurePassword)
New-SecretFile -Name "minio_root_password" -Value (New-SecurePassword)
New-SecretFile -Name "elastic_password" -Value (New-SecurePassword)
New-SecretFile -Name "grafana_admin_password" -Value (New-SecurePassword)
New-SecretFile -Name "jwt_secret" -Value (New-SecurePassword -Length 64)
New-SecretFile -Name "encryption_key" -Value (New-SecurePassword -Length 32)

# Placeholder secrets (user duhet t'i plotësojë)
New-SecretFile -Name "openai_api_key" -Value "sk-REPLACE_WITH_YOUR_KEY"
New-SecretFile -Name "slack_webhook_url" -Value "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"

# Vendos permissions (vetëm owner mund të lexojë)
Write-Host "`n🔒 Setting secure permissions..." -ForegroundColor Yellow
Get-ChildItem $secretsDir -File | ForEach-Object {
    $acl = Get-Acl $_.FullName
    $acl.SetAccessRuleProtection($true, $false)
    $adminRule = New-Object System.Security.AccessControl.FileSystemAccessRule(
        [System.Security.Principal.WindowsIdentity]::GetCurrent().Name,
        "FullControl",
        "Allow"
    )
    $acl.AddAccessRule($adminRule)
    Set-Acl $_.FullName $acl
}

Write-Host "✓ Permissions set (owner only)" -ForegroundColor Green

# Shfaq passwordet (vetëm për administratorin)
Write-Host "`n📋 Generated Passwords:" -ForegroundColor Cyan
Write-Host "=====================================================`n" -ForegroundColor Gray

Get-ChildItem $secretsDir -Filter "*.txt" | ForEach-Object {
    $name = $_.BaseName
    $value = Get-Content $_.FullName -Raw
    
    if ($name -like "*password*" -or $name -like "*secret*" -or $name -like "*key*") {
        Write-Host "$name : $value" -ForegroundColor White
    } else {
        Write-Host "$name : $value" -ForegroundColor Gray
    }
}

Write-Host "`n=====================================================" -ForegroundColor Gray
Write-Host "⚠️  IMPORTANT: Save these passwords in a secure location!" -ForegroundColor Red
Write-Host "⚠️  Add 'secrets/' to .gitignore to prevent commits!" -ForegroundColor Red

# Shto në .gitignore
$gitignorePath = ".\.gitignore"
$gitignoreContent = Get-Content $gitignorePath -ErrorAction SilentlyContinue

if ($gitignoreContent -notcontains "secrets/") {
    Add-Content -Path $gitignorePath -Value "`n# Docker Secrets`nsecrets/`n.env.secrets"
    Write-Host "✓ Added secrets/ to .gitignore" -ForegroundColor Green
}

Write-Host "`n✅ Secrets initialization complete!" -ForegroundColor Green
Write-Host "📝 Next steps:" -ForegroundColor Cyan
Write-Host "   1. Review generated passwords above" -ForegroundColor White
Write-Host "   2. Update API keys in secrets/ directory" -ForegroundColor White
Write-Host "   3. Run: docker stack deploy -c docker-compose.secrets.yml kloud" -ForegroundColor White


