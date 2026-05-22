#!/usr/bin/env bash
# Always load .env.prod for docker compose (avoids POSTGRES_PASSWORD interpolation errors)
set -euo pipefail
cd "$(dirname "$0")/.."
exec docker compose -f docker-compose.prod.yml --env-file .env.prod "$@"
