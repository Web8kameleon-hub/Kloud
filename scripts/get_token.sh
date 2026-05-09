#!/usr/bin/env bash
set -euo pipefail

REALM=${KC_REALM:-kloud}
CLIENT=${KC_CLIENT:-neuro-api}
SECRET=${KC_SECRET:-changeme}
KC=${KC_URL:-http://localhost:8089}
USER=${1:?"username required"}
PASS=${2:?"password required"}

curl -s \
  -d grant_type=password \
  -d client_id="${CLIENT}" \
  -d client_secret="${SECRET}" \
  -d username="${USER}" \
  -d password="${PASS}" \
  "${KC}/realms/${REALM}/protocol/openid-connect/token" | jq -r '.access_token'


