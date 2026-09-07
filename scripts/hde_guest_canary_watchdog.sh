#!/usr/bin/env bash
# Quiet HDE guest runtime watchdog for Hermes cron no_agent mode.
# Success: no output. Failure: concise alert + canary JSON.
set -euo pipefail
REPO=/home/ubuntu/work/hd-platform-staging
OUT=$(mktemp /tmp/hde-guest-canary-watchdog.XXXXXX.json)
trap 'rm -f "$OUT"' EXIT
cd "$REPO"
if python3 scripts/hde_guest_canary.py --guest-id 23 --pretty >"$OUT" 2>&1; then
  exit 0
fi
printf '🔴 HDE guest canary failed. George runtime needs attention.\n\n'
printf 'Command: python3 scripts/hde_guest_canary.py --guest-id 23 --pretty\n\n'
sed -E 's/[0-9]+:[A-Za-z0-9_-]+/[REDACTED_TOKEN]/g' "$OUT"
