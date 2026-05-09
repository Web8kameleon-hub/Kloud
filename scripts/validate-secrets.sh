#!/bin/bash
# =====================================================
# VALIDATE SECRETS CONFIGURATION (Linux/Mac)
# =====================================================
# Kontrollon që secrets të jenë konfiguruar saktë
# Usage: ./scripts/validate-secrets.sh
# =====================================================

set -e

echo "🔍 Validating Secrets Configuration..."

errors=()
warnings=()

# Check secrets directory
if [ ! -d "./secrets" ]; then
    errors+=("❌ Secrets directory not found! Run ./scripts/init-secrets.sh first")
else
    echo "✓ Secrets directory exists"
    
    # Check required secrets
    required_secrets=(
        "postgres_password"
        "postgres_user"
        "minio_root_password"
        "elastic_password"
        "grafana_admin_password"
        "jwt_secret"
        "encryption_key"
    )
    
    for secret in "${required_secrets[@]}"; do
        path="./secrets/$secret.txt"
        if [ ! -f "$path" ]; then
            errors+=("❌ Missing secret: $secret.txt")
        else
            content=$(cat "$path")
            
            # Validate password strength
            if [[ $secret == *"password"* ]] || [[ $secret == *"secret"* ]] || [[ $secret == *"key"* ]]; then
                if [ ${#content} -lt 16 ]; then
                    errors+=("❌ $secret is too short (< 16 chars)")
                elif echo "$content" | grep -qE "^(admin|password|changeme|kloud123)"; then
                    errors+=("❌ $secret contains weak/default password")
                else
                    echo "✓ $secret validated"
                fi
            fi
        fi
    done
    
    # Check optional secrets
    optional_secrets=(
        "openai_api_key"
        "slack_webhook_url"
    )
    
    for secret in "${optional_secrets[@]}"; do
        path="./secrets/$secret.txt"
        if [ ! -f "$path" ]; then
            warnings+=("⚠️  Optional secret missing: $secret.txt")
        else
            content=$(cat "$path")
            if echo "$content" | grep -qE "REPLACE|YOUR|WEBHOOK"; then
                warnings+=("⚠️  $secret still has placeholder value")
            fi
        fi
    done
fi

# Check .gitignore
if [ -f "./.gitignore" ]; then
    if ! grep -q "secrets/" .gitignore; then
        errors+=("❌ .gitignore doesn't exclude secrets/ directory")
    else
        echo "✓ .gitignore properly configured"
    fi
    
    if ! grep -q ".env.secrets" .gitignore; then
        warnings+=("⚠️  .gitignore should exclude .env.secrets")
    fi
else
    errors+=("❌ .gitignore not found")
fi

# Check docker-compose.secrets.yml
if [ ! -f "./docker-compose.secrets.yml" ]; then
    errors+=("❌ docker-compose.secrets.yml not found")
else
    echo "✓ docker-compose.secrets.yml exists"
    
    # Validate it doesn't have hard-coded passwords
    if grep -qE "password:\s+(kloud|admin|changeme)" docker-compose.secrets.yml; then
        errors+=("❌ docker-compose.secrets.yml contains hard-coded passwords!")
    fi
fi

# Check .env files don't contain secrets
env_files=(".env" ".env.production" ".env.development")
for env_file in "${env_files[@]}"; do
    if [ -f "$env_file" ]; then
        if grep -qE "PASSWORD=\w{8,}|SECRET=\w{8,}|KEY=\w{8,}" "$env_file"; then
            warnings+=("⚠️  $env_file may contain secrets (should use \${VAR} references)")
        fi
    fi
done

# Check file permissions
if [ -d "./secrets" ]; then
    for file in ./secrets/*.txt; do
        if [ -f "$file" ]; then
            perms=$(stat -c "%a" "$file" 2>/dev/null || stat -f "%Lp" "$file" 2>/dev/null)
            if [ "$perms" != "600" ]; then
                warnings+=("⚠️  $(basename $file) has permissions $perms (should be 600)")
            fi
        fi
    done
fi

# Display results
echo ""
echo "================================================"

if [ ${#errors[@]} -eq 0 ] && [ ${#warnings[@]} -eq 0 ]; then
    echo "✅ ALL VALIDATIONS PASSED"
    echo "Your secrets configuration is secure and ready for production!"
    exit 0
fi

if [ ${#errors[@]} -gt 0 ]; then
    echo "❌ ERRORS FOUND (${#errors[@]}):"
    for error in "${errors[@]}"; do
        echo "   $error"
    done
fi

if [ ${#warnings[@]} -gt 0 ]; then
    echo ""
    echo "⚠️  WARNINGS (${#warnings[@]}):"
    for warning in "${warnings[@]}"; do
        echo "   $warning"
    done
fi

echo ""
echo "================================================"

if [ ${#errors[@]} -gt 0 ]; then
    echo "❌ Validation failed! Fix errors before deploying."
    exit 1
else
    echo "⚠️  Validation passed with warnings. Review before deploying."
    exit 0
fi


