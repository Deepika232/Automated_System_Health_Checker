#!/usr/bin/env bash
set -euo pipefail

# Quick service status check (Linux/systemd).
# Usage: SERVICE_NAMES="ssh,cron,docker" ./scripts/services_status.sh

SERVICE_NAMES="${SERVICE_NAMES:-ssh,cron,docker}"

IFS=',' read -ra SERVICES <<< "${SERVICE_NAMES}"

if ! command -v systemctl >/dev/null 2>&1; then
  echo "systemctl not available (non-systemd OS)."
  exit 0
fi

for s in "${SERVICES[@]}"; do
  s="$(echo "$s" | xargs)"
  [[ -z "$s" ]] && continue
  echo -n "${s}: "
  systemctl is-active "${s}" || true
done

