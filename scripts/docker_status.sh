#!/usr/bin/env bash
set -euo pipefail

# Quick Docker container status (requires docker CLI).

if ! command -v docker >/dev/null 2>&1; then
  echo "docker CLI not available."
  exit 0
fi

docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Image}}"

