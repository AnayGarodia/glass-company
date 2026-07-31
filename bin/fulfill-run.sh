#!/bin/bash
# launchd entrypoint for the fulfillment run
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p logs
set -a; source "$HOME/.config/glass-company/env"; set +a
/Users/aakritigarodia/.local/bin/claude -p "$(cat RUNBOOK-FULFILL.md)" \
  --permission-mode acceptEdits --max-turns 60 \
  >> logs/fulfill.log 2>&1
