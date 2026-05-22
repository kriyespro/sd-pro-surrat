# SuratPro — SSL (Let's Encrypt) on shared VPS

**Architecture**

```
Browser → Host Nginx :443 (SSL) → http://127.0.0.1:8787 → Docker nginx → Gunicorn
```

Docker stays on **8787**. Host nginx uses **80/443** only for `suratpro.com` / `www.suratpro.com`.

**Prerequisites**

- DNS A records: `suratpro.com` and `www.suratpro.com` → your VPS IP
- SuratPro running: `curl -I http://127.0.0.1:8787/` returns 200/302
- Port **8787** working

---

## Step 1 — Install certbot (on VPS)

```bash
sudo apt update
sudo apt install -y certbot
sudo mkdir -p /var/www/certbot
```

If host nginx is not installed:

```bash
sudo apt install -y nginx
```

---

## Step 2 — Add SuratPro site to **host** nginx

```bash
cd /opt/suratpro/sd-pro-surrat

# First time only: HTTP config (no SSL files yet)
sudo cp deploy/nginx-host-suratpro-http-only.conf /etc/nginx/sites-available/suratpro
sudo ln -sf /etc/nginx/sites-available/suratpro /etc/nginx/sites-enabled/suratpro

# If default site conflicts, disable it only if safe:
# sudo rm -f /etc/nginx/sites-enabled/default

sudo nginx -t
sudo systemctl reload nginx
```

Test:

```bash
curl -I http://suratpro.com/
```

---

## Step 3 — Get SSL certificate

```bash
sudo certbot certonly --webroot \
  -w /var/www/certbot \
  -d suratpro.com \
  -d www.suratpro.com \
  --agree-tos \
  -m your-email@example.com \
  --no-eff-email
```

Replace email with yours.

If certbot says port 80 busy, your **main** nginx already listens on 80. Add this inside the existing `server { listen 80; server_name suratpro.com www.suratpro.com; ...}` block:

```nginx
location /.well-known/acme-challenge/ {
    root /var/www/certbot;
    allow all;
}
```

Then run certbot again.

---

## Step 4 — Enable HTTPS config

```bash
cd /opt/suratpro/sd-pro-surrat
sudo cp deploy/nginx-host-suratpro.conf /etc/nginx/sites-available/suratpro
sudo nginx -t
sudo systemctl reload nginx
```

Test:

```bash
curl -I https://suratpro.com/
```

---

## Step 5 — Update Django `.env.prod`

```bash
nano /opt/suratpro/sd-pro-surrat/.env.prod
```

Set:

```env
SECURE_SSL_REDIRECT=True
CSRF_TRUSTED_ORIGINS=https://suratpro.com,https://www.suratpro.com,https://62.72.43.194,http://62.72.43.194:8787
```

Restart app:

```bash
cd /opt/suratpro/sd-pro-surrat
docker compose -f docker-compose.prod.yml --env-file .env.prod restart web
```

---

## Step 6 — Google OAuth redirect URIs

In Google Cloud Console add:

```
https://suratpro.com/auth/google/callback/
https://www.suratpro.com/auth/google/callback/
```

(Keep `http://IP:8787/...` only if you still test without domain.)

---

## Auto-renew certificate

```bash
sudo certbot renew --dry-run
```

Cron is usually installed by certbot. Check:

```bash
systemctl list-timers | grep certbot
```

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `nginx: [emerg] cannot load certificate` | Run Step 3 first; certs must exist before Step 4 |
| `502 Bad Gateway` | Docker not running: `docker compose ... ps` — start web/nginx |
| `Connection refused` on 8787 | `docker compose -f docker-compose.prod.yml --env-file .env.prod up -d` |
| Certbot 404 on challenge | `location /.well-known/acme-challenge/` missing on host nginx port 80 |
| Other site broke | Only edit `sites-available/suratpro`; do not remove other vhosts |
| Redirect loop | Set `SECURE_SSL_REDIRECT=False` until host nginx sends `X-Forwarded-Proto: https` |

---

## IP access without domain

SSL for raw IP is not supported by Let's Encrypt. Use:

- **https://suratpro.com** (recommended)
- or **http://YOUR_IP:8787** (no SSL)
