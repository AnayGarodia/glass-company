#!/bin/bash
# launchd entrypoint for the fulfillment run
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p logs
set -a; source "$HOME/.config/glass-company/env"; set +a
export PATH="$PWD/.venv/bin:/opt/homebrew/bin:$PATH"

{
  echo "=== fulfill-run $(date -u +%Y-%m-%dT%H:%M:%SZ) ==="
  /Users/aakritigarodia/.local/bin/claude -p "$(cat RUNBOOK-FULFILL.md)" \
    --permission-mode acceptEdits --max-turns 60 \
    || echo "[wrapper] claude -p exited non-zero; continuing to sync regardless"

  # Claude Code sandboxes network egress inside headless -p sessions by
  # design (git push, npx). The agent's job is to fetch/decide/generate/
  # write files; syncing what it wrote happens here, in plain bash, which
  # has no such sandbox. Runs unconditionally so a partial or failed agent
  # turn still gets whatever it produced onto the live site.
  echo "[wrapper] syncing repo + deploying dashboard"
  git add -A
  git commit -m "ops: fulfillment run" || echo "[wrapper] nothing to commit"
  git push origin main || echo "[wrapper] push failed"
  npx wrangler pages deploy site --project-name glasscompany --branch main --commit-dirty=true \
    || echo "[wrapper] wrangler deploy failed"
} >> logs/fulfill.log 2>&1
