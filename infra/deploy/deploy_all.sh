#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "[ALL] Starting HQ deploy"
"$SCRIPT_DIR/deploy_hq.sh"

echo "[ALL] Starting Compute deploy"
"$SCRIPT_DIR/deploy_compute.sh"

echo "[ALL] Starting Failover deploy"
"$SCRIPT_DIR/deploy_failover.sh"

echo "[ALL] Starting Edge deploy"
"$SCRIPT_DIR/deploy_edge.sh"

echo "[ALL] Full matrix deploy complete."
