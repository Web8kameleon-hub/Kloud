#!/bin/bash
# =====================================================
# INITIALIZE DOCKER SECRETS (Linux/Mac)
# =====================================================
# Krijon secrets directory dhe gjeneron passwords
# Usage: ./scripts/init-secrets.sh
# =====================================================

set -e

echo "🔐 Initializing Docker Secrets..."

# Krijo secrets directory
SECRETS_DIR="./secrets"
mkdir -p "$SECRETS_DIR"
echo "✓ Created secrets directory"

# Function për të gjeneruar password të fortë
generate_password() {
    local length=${1:-32}
    openssl rand -base64 $length | tr -d "=+/" | cut -c1-$length
}

# Function për të krijuar secret file
create_secret() {
    local name=$1
    local value=$2
    local path="$SECRETS_DIR/$name.txt"
    
    if [ -f "$path" ]; then
        echo "⚠️  $name already exists, skipping..."
        return
    fi
    
    echo -n "$value" > "$path"
    chmod 600 "$path"
    echo "✓ Created secret: $name"
}

# Krijo të gjitha secrets
echo ""
echo "📝 Generating secure passwords..."

create_secret "postgres_password" "$(generate_password 32)"
create_secret "postgres_user" "kloud"
create_secret "redis_password" "$(generate_password 32)"
create_secret "minio_root_password" "$(generate_password 32)"
create_secret "elastic_password" "$(generate_password 32)"
create_secret "grafana_admin_password" "$(generate_password 32)"
create_secret "jwt_secret" "$(generate_password 64)"
create_secret "encryption_key" "$(generate_password 32)"

# Placeholder secrets
create_secret "openai_api_key" "sk-REPLACE_WITH_YOUR_KEY"
create_secret "slack_webhook_url" "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"

# Shfaq passwordet
echo ""
echo "📋 Generated Passwords:"
echo "====================================================="
echo ""

for file in "$SECRETS_DIR"/*.txt; do
    name=$(basename "$file" .txt)
    value=$(cat "$file")
    echo "$name : $value"
done

echo ""
echo "====================================================="
echo "⚠️  IMPORTANT: Save these passwords in a secure location!"
echo "⚠️  Add 'secrets/' to .gitignore to prevent commits!"

# Shto në .gitignore
if ! grep -q "secrets/" .gitignore 2>/dev/null; then
    echo -e "\n# Docker Secrets\nsecrets/\n.env.secrets" >> .gitignore
    echo "✓ Added secrets/ to .gitignore"
fi

echo ""
echo "✅ Secrets initialization complete!"
echo "📝 Next steps:"
echo "   1. Review generated passwords above"
echo "   2. Update API keys in secrets/ directory"
echo "   3. Run: docker stack deploy -c docker-compose.secrets.yml kloud"


