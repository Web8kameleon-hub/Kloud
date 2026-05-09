# =====================================================
# VALIDATE SECRETS CONFIGURATION
# =====================================================
# Kontrollon që secrets të jenë konfiguruar saktë
# Usage: .\scripts\validate-secrets.ps1
# =====================================================

Write-Host "🔍 Validating Secrets Configuration..." -ForegroundColor Cyan

$errors = @()
$warnings = @()

# Check secrets directory
if (-not (Test-Path ".\secrets")) {
    $errors += "❌ Secrets directory not found! Run .\scripts\init-secrets.ps1 first"
} else {
    Write-Host "✓ Secrets directory exists" -ForegroundColor Green
    
    # Check required secrets
    $requiredSecrets = @(
        "postgres_password",
        "postgres_user",
        "minio_root_password",
        "elastic_password",
        "grafana_admin_password",
        "jwt_secret",
        "encryption_key"
    )
    
    foreach ($secret in $requiredSecrets) {
        $path = ".\secrets\$secret.txt"
        if (-not (Test-Path $path)) {
            $errors += "❌ Missing secret: $secret.txt"
        } else {
            $content = Get-Content $path -Raw
            
            # Validate password strength
            if ($secret -like "*password*" -or $secret -like "*secret*" -or $secret -like "*key*") {
                if ($content.Length -lt 16) {
                    $errors += "❌ $secret is too short (< 16 chars)"
                } elseif ($content -match "^(admin|password|changeme|kloud123)") {
                    $errors += "❌ $secret contains weak/default password"
                } else {
                    Write-Host "✓ $secret validated" -ForegroundColor Green
                }
            }
        }
    }
    
    # Check optional secrets
    $optionalSecrets = @(
        "openai_api_key",
        "slack_webhook_url"
    )
    
    foreach ($secret in $optionalSecrets) {
        $path = ".\secrets\$secret.txt"
        if (-not (Test-Path $path)) {
            $warnings += "⚠️  Optional secret missing: $secret.txt"
        } else {
            $content = Get-Content $path -Raw
            if ($content -match "REPLACE|YOUR|WEBHOOK") {
                $warnings += "⚠️  $secret still has placeholder value"
            }
        }
    }
}

# Check .gitignore
if (Test-Path ".\.gitignore") {
    $gitignoreContent = Get-Content ".\.gitignore" -Raw
    
    if ($gitignoreContent -notmatch "secrets/") {
        $errors += "❌ .gitignore doesn't exclude secrets/ directory"
    } else {
        Write-Host "✓ .gitignore properly configured" -ForegroundColor Green
    }
    
    if ($gitignoreContent -notmatch ".env.secrets") {
        $warnings += "⚠️  .gitignore should exclude .env.secrets"
    }
} else {
    $errors += "❌ .gitignore not found"
}

# Check docker-compose.secrets.yml
if (-not (Test-Path ".\docker-compose.secrets.yml")) {
    $errors += "❌ docker-compose.secrets.yml not found"
} else {
    Write-Host "✓ docker-compose.secrets.yml exists" -ForegroundColor Green
    
    # Validate it doesn't have hard-coded passwords
    $composeContent = Get-Content ".\docker-compose.secrets.yml" -Raw
    if ($composeContent -match "password:\s+(kloud|admin|changeme)") {
        $errors += "❌ docker-compose.secrets.yml contains hard-coded passwords!"
    }
}

# Check .env files don't contain secrets
$envFiles = @(".env", ".env.production", ".env.development")
foreach ($envFile in $envFiles) {
    if (Test-Path $envFile) {
        $content = Get-Content $envFile -Raw
        if ($content -match "PASSWORD=\w{8,}|SECRET=\w{8,}|KEY=\w{8,}") {
            $warnings += "⚠️  $envFile may contain secrets (should use \${VAR} references)"
        }
    }
}

# Check file permissions (Windows)
if (Test-Path ".\secrets") {
    $secretFiles = Get-ChildItem ".\secrets\*.txt"
    foreach ($file in $secretFiles) {
        $acl = Get-Acl $file.FullName
        $rules = $acl.Access | Where-Object { $_.FileSystemRights -match "Read" }
        
        if ($rules.Count -gt 1) {
            $warnings += "⚠️  $($file.Name) has multiple read permissions (should be owner only)"
        }
    }
}

# Display results
Write-Host "`n================================================" -ForegroundColor Gray

if ($errors.Count -eq 0 -and $warnings.Count -eq 0) {
    Write-Host "✅ ALL VALIDATIONS PASSED" -ForegroundColor Green
    Write-Host "Your secrets configuration is secure and ready for production!" -ForegroundColor White
    exit 0
}

if ($errors.Count -gt 0) {
    Write-Host "❌ ERRORS FOUND ($($errors.Count)):" -ForegroundColor Red
    foreach ($error in $errors) {
        Write-Host "   $error" -ForegroundColor Red
    }
}

if ($warnings.Count -gt 0) {
    Write-Host "`n⚠️  WARNINGS ($($warnings.Count)):" -ForegroundColor Yellow
    foreach ($warning in $warnings) {
        Write-Host "   $warning" -ForegroundColor Yellow
    }
}

Write-Host "`n================================================" -ForegroundColor Gray

if ($errors.Count -gt 0) {
    Write-Host "❌ Validation failed! Fix errors before deploying." -ForegroundColor Red
    exit 1
} else {
    Write-Host "⚠️  Validation passed with warnings. Review before deploying." -ForegroundColor Yellow
    exit 0
}


