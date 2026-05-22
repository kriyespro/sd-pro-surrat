#!/usr/bin/env bash
# Deploy SuratPro on production server (62.72.43.194 / suratpro.com)
set -euo pipefail

cd "$(dirname "$0")/.."

if [[ ! -f .env.prod ]]; then
  echo "ERROR: Copy .env.prod and set SECRET_KEY + POSTGRES_PASSWORD + DATABASE_URL"
  exit 1
fi

# Sync DATABASE_URL password with POSTGRES_PASSWORD
set -a
source .env.prod
set +a

echo "==> Building images..."
docker compose -f docker-compose.prod.yml --env-file .env.prod build

echo "==> Starting stack (db, redis, web, celery, nginx)..."
docker compose -f docker-compose.prod.yml --env-file .env.prod up -d

echo "==> Waiting for web health..."
sleep 8

echo "==> Smoke checks..."
for path in / /auth/login/; do
  code=$(curl -s -o /dev/null -w "%{http_code}" -H "Host: suratpro.com" "http://127.0.0.1:8787${path}" || echo "000")
  echo "  GET ${path} -> ${code}"
done

echo ""
echo "Deploy complete. Open:"
echo "  http://127.0.0.1:8787"
echo "  http://62.72.43.194:8787"
echo "  https://suratpro.com (if main nginx proxies to :8787)"
echo ""
echo "Logs: docker compose -f docker-compose.prod.yml logs -f web nginx"
