#!/bin/bash
# 🚀 Hetzner Deployment Setup Script
# Gjeneron SSH keys dhe konfiguron sekretet në GitHub

set -e

echo "🔑 Kloud Cloud - Hetzner Deployment Setup"
echo "=============================================="
echo ""

# Check prerequisites
echo "📋 Checking prerequisites..."
command -v ssh-keygen >/dev/null 2>&1 || { echo "ssh-keygen required but not installed."; exit 1; }
command -v gh >/dev/null 2>&1 || { echo "GitHub CLI (gh) required but not installed."; exit 1; }

echo "✅ Prerequisites OK"
echo ""

# Generate SSH key for Hetzner
echo "🔑 Generating SSH key for Hetzner..."
SSH_KEY_FILE="$HOME/.ssh/hetzner_deploy_key"

if [ -f "$SSH_KEY_FILE" ]; then
    echo "⚠️  SSH key already exists at $SSH_KEY_FILE"
    read -p "Overwrite? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Using existing key"
        SSH_KEY_FILE_EXISTING=true
    fi
fi

if [ ! "$SSH_KEY_FILE_EXISTING" = "true" ]; then
    ssh-keygen -t ed25519 -f "$SSH_KEY_FILE" -N "" -C "kloud-hetzner-deploy"
    chmod 600 "$SSH_KEY_FILE"
    chmod 644 "$SSH_KEY_FILE.pub"
    echo "✅ SSH key generated"
fi

echo ""

# Get SSH public key content
SSH_PUBLIC_KEY=$(cat "$SSH_KEY_FILE.pub")
SSH_PRIVATE_KEY=$(cat "$SSH_KEY_FILE" | base64 -w 0)

echo "📝 SSH Public Key:"
echo "$SSH_PUBLIC_KEY"
echo ""

# Setup GitHub secrets
echo "🔐 Setting up GitHub Secrets..."
echo ""

# Check if authenticated with GitHub
if ! gh auth status >/dev/null 2>&1; then
    echo "❌ Not authenticated with GitHub CLI"
    echo "Please run: gh auth login"
    exit 1
fi

# Get repository
REPO=${1:-.}
if [ "$REPO" = "." ]; then
    REPO=$(git config --get remote.origin.url | sed 's/.*[:/]\(.*\)\/\(.*\)\.git$/\1\/\2/')
fi

echo "📦 Repository: $REPO"
echo ""

# Set secrets
echo "Setting secrets..."

# SSH Key (private - base64 encoded)
echo "  - HETZNER_SSH_KEY"
gh secret set HETZNER_SSH_KEY -b "$SSH_PRIVATE_KEY" -R "$REPO"

# Server IP - ask user
echo ""
read -p "Enter Hetzner Server IP: " HETZNER_IP
gh secret set HETZNER_SERVER_IP -b "$HETZNER_IP" -R "$REPO"

# API Token - ask user
echo ""
read -p "Enter Hetzner API Token: " -s HETZNER_TOKEN
echo ""
gh secret set HETZNER_API_TOKEN -b "$HETZNER_TOKEN" -R "$REPO"

# Database password
echo ""
read -p "Enter Database Password (or press Enter for auto-generate): " -s DB_PASSWORD
echo ""
if [ -z "$DB_PASSWORD" ]; then
    DB_PASSWORD=$(openssl rand -base64 32)
fi
gh secret set DB_PASSWORD -b "$DB_PASSWORD" -R "$REPO"

# Grafana password
echo ""
read -p "Enter Grafana Password (or press Enter for auto-generate): " -s GRAFANA_PASSWORD
echo ""
if [ -z "$GRAFANA_PASSWORD" ]; then
    GRAFANA_PASSWORD=$(openssl rand -base64 16)
fi
gh secret set GRAFANA_PASSWORD -b "$GRAFANA_PASSWORD" -R "$REPO"

# Slack webhook (optional)
echo ""
read -p "Enter Slack Webhook URL (optional, press Enter to skip): " SLACK_WEBHOOK
if [ -n "$SLACK_WEBHOOK" ]; then
    gh secret set SLACK_WEBHOOK -b "$SLACK_WEBHOOK" -R "$REPO"
fi

# Kubeconfig (optional for K8s deployment)
echo ""
read -p "Enter path to kubeconfig file (optional, press Enter to skip): " KUBE_CONFIG_PATH
if [ -n "$KUBE_CONFIG_PATH" ] && [ -f "$KUBE_CONFIG_PATH" ]; then
    KUBE_CONFIG_B64=$(cat "$KUBE_CONFIG_PATH" | base64 -w 0)
    gh secret set KUBE_CONFIG -b "$KUBE_CONFIG_B64" -R "$REPO"
fi

echo ""
echo "✅ All secrets set successfully!"
echo ""

# Print summary
echo "📋 Summary:"
echo "=============================================="
echo "Repository: $REPO"
echo "SSH Key: $SSH_KEY_FILE"
echo "Server IP: $HETZNER_IP"
echo ""
echo "Next steps:"
echo "1. Add SSH public key to Hetzner server:"
echo "   ssh-copy-id -i $SSH_KEY_FILE.pub root@$HETZNER_IP"
echo ""
echo "2. SSH into server and setup:"
echo "   ssh -i $SSH_KEY_FILE root@$HETZNER_IP"
echo ""
echo "3. Run deployment setup on server:"
echo "   bash /opt/kloud-cloud/scripts/hetzner-server-setup.sh"
echo ""
echo "4. Verify deployment workflow secrets:"
echo "   gh secret list -R $REPO"
echo ""
echo "=============================================="

