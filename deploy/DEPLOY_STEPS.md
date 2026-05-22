# SuratPro — Full Docker Deployment Guide

**Server IP:** `62.72.43.194`  
**Domain:** `suratpro.com` / `www.suratpro.com`  
**Stack:** Docker · PostgreSQL · Redis · Gunicorn · Celery · Nginx

---

## Part A — On your Mac (local)

### 1. Commit and push code

```bash
cd /Users/kumarsunilverma/Desktop/sd-suratpro

git status
git add .
git commit -m "Production deploy: Docker, Redis, Google login, env prod"
git push origin main
```

If your branch is not `main`, replace with your branch name (e.g. `master`).

### 2. Do NOT push secrets

These files must stay local / on server only (already in `.gitignore`):

- `.env.prod`
- `.env`
- `.key-google`
- `db.sqlite3`

---

## Part B — First time on VPS (`62.72.43.194`)

SSH into the server:

```bash
ssh root@62.72.43.194
# or: ssh your_user@62.72.43.194
```

### 3. Install Docker (Ubuntu/Debian)

```bash
apt update && apt install -y git curl
curl -fsSL https://get.docker.com | sh
apt install -y docker-compose-plugin
docker --version
docker compose version
```

### 4. Clone the repo

```bash
mkdir -p /opt/suratpro
cd /opt/suratpro
git clone https://github.com/YOUR_USERNAME/sd-suratpro.git .
# OR if repo already exists:
# cd /opt/suratpro && git pull origin main
```

Replace `YOUR_USERNAME` with your GitHub username/repo URL.

### 5. Create `.env.prod` on the server

```bash
cd /opt/suratpro
nano .env.prod
```

Paste the full block from **Part E** below (copy everything between the lines).  
Save: `Ctrl+O`, Enter, `Ctrl+X`.

Verify:

```bash
grep SECRET_KEY .env.prod
grep DATABASE_URL .env.prod
```

### 6. Google OAuth redirect URIs

In [Google Cloud Console](https://console.cloud.google.com/) → Credentials → OAuth client, add:

```
https://suratpro.com/auth/google/callback/
https://www.suratpro.com/auth/google/callback/
https://62.72.43.194/auth/google/callback/
```

### 7. DNS (if not done)

| Type | Name | Value |
|------|------|-------|
| A | `@` | `62.72.43.194` |
| A | `www` | `62.72.43.194` |

---

## Part C — Build and run Docker

```bash
cd /opt/suratpro

chmod +x entrypoint.sh scripts/deploy_prod.sh

# Build images and start all services
docker compose -f docker-compose.prod.yml --env-file .env.prod up -d --build
```

### What starts

| Service | Role |
|---------|------|
| `db` | PostgreSQL 16 |
| `redis` | Cache + sessions + Celery broker |
| `web` | Django + Gunicorn (migrate, collectstatic, seed plans) |
| `celery` | Background tasks |
| `nginx` | Port 80/443 → static + proxy to web |

### 8. Check containers

```bash
docker compose -f docker-compose.prod.yml ps
docker compose -f docker-compose.prod.yml logs -f web
```

Wait until you see: `Starting Gunicorn...`

### 9. Create admin user (first deploy only)

```bash
docker compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
```

### 10. Smoke test

```bash
curl -I http://127.0.0.1/
curl -I -H "Host: suratpro.com" http://127.0.0.1/auth/login/
```

Open in browser:

- http://62.72.43.194/
- https://suratpro.com/ (after SSL)

---

## Part D — Updates (git pull + redeploy)

Every time you push from Mac:

**On Mac:**

```bash
git add .
git commit -m "Your change description"
git push origin main
```

**On server:**

```bash
cd /opt/suratpro
git pull origin main

docker compose -f docker-compose.prod.yml --env-file .env.prod up -d --build
```

### Useful Docker commands

```bash
# Stop everything
docker compose -f docker-compose.prod.yml down

# Stop but keep database volume
docker compose -f docker-compose.prod.yml down
# (volumes pg_data, redis_data, static_data, media_data are kept)

# View logs
docker compose -f docker-compose.prod.yml logs -f web
docker compose -f docker-compose.prod.yml logs -f nginx
docker compose -f docker-compose.prod.yml logs -f celery

# Run migrations only
docker compose -f docker-compose.prod.yml exec web python manage.py migrate

# Django shell
docker compose -f docker-compose.prod.yml exec web python manage.py shell

# Restart one service
docker compose -f docker-compose.prod.yml restart web nginx

# Redis ping
docker compose -f docker-compose.prod.yml exec redis redis-cli ping
```

---

## Part E — SSL with Let's Encrypt (recommended)

On the host (not inside Docker), after DNS points to the server:

```bash
apt install -y certbot
certbot certonly --standalone -d suratpro.com -d www.suratpro.com
```

Mount certs in `docker-compose.prod.yml` nginx service (see comments in `deploy/nginx.prod.conf`), then set in `.env.prod`:

```
SECURE_SSL_REDIRECT=True
```

Restart:

```bash
docker compose -f docker-compose.prod.yml --env-file .env.prod up -d
```

---

## Part F — Troubleshooting

| Problem | Fix |
|---------|-----|
| `redirect_uri_mismatch` (Google) | Add exact callback URL in Google Console |
| `DisallowedHost` | Add host to `ALLOWED_HOSTS` in `.env.prod` |
| `CSRF verification failed` | Add origin to `CSRF_TRUSTED_ORIGINS` |
| Web container exits | `docker compose ... logs web` — often DB password mismatch |
| Static 404 | `docker compose ... exec web python manage.py collectstatic --noinput` |
| DB connection refused | Wait for `db` healthy: `docker compose ... ps` |

---

## Quick reference

```bash
# One-liner deploy after git pull
cd /opt/suratpro && git pull && docker compose -f docker-compose.prod.yml --env-file .env.prod up -d --build
```
