#!/usr/bin/env bash
# SuratPro SSL helper — run on VPS as root (or sudo)
# Usage: sudo bash deploy/ssl_install.sh your@email.com
set -euo pipefail

EMAIL="${1:-}"
APP_DIR="${APP_DIR:-/opt/suratpro/sd-pro-surrat}"

if [[ -z "$EMAIL" ]]; then
  echo "Usage: sudo bash deploy/ssl_install.sh your@email.com"
  exit 1
fi

if [[ ! -d "$APP_DIR" ]]; then
  echo "APP_DIR not found: $APP_DIR"
  exit 1
fi

cd "$APP_DIR"

echo "==> Install packages"
apt update
apt install -y certbot nginx

echo "==> Check Docker on 8787"
if ! curl -sf -o /dev/null http://127.0.0.1:8787/ ; then
  echo "WARN: http://127.0.0.1:8787/ not responding. Start Docker first."
fi

echo "==> HTTP-only nginx config (for certbot)"
mkdir -p /var/www/certbot
cp deploy/nginx-host-suratpro-http-only.conf /etc/nginx/sites-available/suratpro
ln -sf /etc/nginx/sites-available/suratpro /etc/nginx/sites-enabled/suratpro
nginx -t
systemctl reload nginx

echo "==> Request certificate"
certbot certonly --webroot \
  -w /var/www/certbot \
  -d suratpro.com \
  -d www.suratpro.com \
  --agree-tos \
  -m "$EMAIL" \
  --no-eff-email

echo "==> Enable HTTPS nginx config"
cp deploy/nginx-host-suratpro.conf /etc/nginx/sites-available/suratpro
nginx -t
systemctl reload nginx

echo "==> Done. Test: curl -I https://suratpro.com/"
echo "Next: set SECURE_SSL_REDIRECT=True in .env.prod and restart web container"
