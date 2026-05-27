# =============================================================================
# GITHUB SECRETS REQUIRED FOR CI/CD
# =============================================================================
# These secrets must be configured in GitHub Repository Settings:
# Settings → Secrets and variables → Actions → New repository secret
# =============================================================================

## REQUIRED SECRETS
## ================

### HETZNER_SSH_KEY (REQUIRED)
# Your SSH private key for connecting to the Hetzner server
# Generate with: ssh-keygen -t ed25519 -C "github-actions"
# Copy the PRIVATE key (id_ed25519, not id_ed25519.pub)
# 
# Example format:
# -----BEGIN OPENSSH PRIVATE KEY-----
# b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAA...
# -----END OPENSSH PRIVATE KEY-----

### GITHUB_TOKEN (AUTO-PROVIDED)
# Automatically provided by GitHub Actions
# No configuration needed

## OPTIONAL SECRETS
## =================

### DB_PASSWORD
# PostgreSQL database password
# Default: 'kloud' if not set

### STRIPE_SECRET_KEY
# Stripe API secret key for payment processing
# Get from: https://dashboard.stripe.com/apikeys

### STRIPE_WEBHOOK_SECRET
# Stripe webhook signing secret
# Get from: https://dashboard.stripe.com/webhooks

### PAYPAL_CLIENT_ID
# PayPal API client ID
# Get from: https://developer.paypal.com/dashboard/

### PAYPAL_CLIENT_SECRET
# PayPal API client secret

### SLACK_WEBHOOK_URL
# Slack webhook for notifications
# Get from: https://api.slack.com/messaging/webhooks

# =============================================================================
# HOW TO ADD SSH KEY TO GITHUB
# =============================================================================
# 
# 1. Generate SSH key on your local machine:
#    ssh-keygen -t ed25519 -C "github-actions-kloud" -f ~/.ssh/github_deploy
#
# 2. Copy public key to server:
#    ssh-copy-id -i ~/.ssh/github_deploy.pub root@46.62.210.251
#
# 3. Copy private key content:
#    cat ~/.ssh/github_deploy
#
# 4. Add to GitHub:
#    - Go to: https://github.com/Web8kameleon-hub/kloud.com/settings/secrets/actions
#    - Click "New repository secret"
#    - Name: HETZNER_SSH_KEY
#    - Value: Paste the entire private key (including BEGIN/END lines)
#    - Click "Add secret"
#
# =============================================================================
# VERIFICATION
# =============================================================================
#
# After adding secrets, you can verify by running the workflow manually:
# Actions → Deploy Docker Compose → Run workflow
#
# The workflow will show ✅ if SSH connection is successful.
#

