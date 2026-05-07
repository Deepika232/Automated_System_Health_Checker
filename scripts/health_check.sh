#!/usr/bin/env bash
set -euo pipefail

# Automated System Health Checker (Bash wrapper)
# Generates reports/health_report.txt by calling the Flask app health endpoint.

APP_URL="${APP_URL:-http://localhost:5000/health}"

echo "Running health check against: ${APP_URL}"

if command -v curl >/dev/null 2>&1; then
  curl -fsS "${APP_URL}" | python -m json.tool >/dev/null
  echo "Health check complete. Report written by app to reports/health_report.txt"
else
  echo "curl not found. Install curl to run this script."
  exit 1
fi
