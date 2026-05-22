# SuratPro Production Deploy Runbook

**Server:** `62.72.43.194` · **Domain:** `suratpro.com` / `www.suratpro.com`

## 1) Pre-deploy checklist

1. Copy `.env.prod` to the server and set:
   - `SECRET_KEY` — `python -c "import secrets; print(secrets.token_urlsafe(50))"`
   - `POSTGRES_PASSWORD` — strong password
   - `DATABASE_URL` — must use the same password: `postgres://postgres:PASSWORD@db:5432/suratpro`
2. Point DNS: `suratpro.com` and `www` → `62.72.43.194`
3. **Google OAuth** — in [Google Cloud Console](https://console.cloud.google.com/) → APIs & Services → Credentials, add **Authorized redirect URIs**:
   - `https://suratpro.com/auth/google/callback/`
   - `https://www.suratpro.com/auth/google/callback/`
   - `https://62.72.43.194/auth/google/callback/`
   - `http://127.0.0.1:8000/auth/google/callback/` (local dev)
4. Set `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` in `.env.prod` (from `.key-google` or Console).
5. Install Docker + Docker Compose on the VPS

## 2) Deploy (one command)

```bash
chmod +x scripts/deploy_prod.sh entrypoint.sh
./scripts/deploy_prod.sh
```

Or manually:

```bash
docker compose -f docker-compose.prod.yml --env-file .env.prod up -d --build
```

Stack: **PostgreSQL** · **Redis** (cache + sessions + Celery) · **Gunicorn** · **Celery** · **Nginx**

## 3) SSL (HTTPS)

After DNS propagates, on the host:

```bash
# Option A: Certbot on host, mount certs into nginx
certbot certonly --standalone -d suratpro.com -d www.suratpro.com
# Mount /etc/letsencrypt/live/suratpro.com/ into docker nginx (see deploy/nginx.prod.conf comments)
```

Set in `.env.prod`:

```
SECURE_SSL_REDIRECT=True
CSRF_TRUSTED_ORIGINS=https://62.72.43.194,https://suratpro.com,https://www.suratpro.com
```

Nginx sets `X-Forwarded-Proto`; Django uses `SECURE_PROXY_SSL_HEADER`.

## 4) Health checks

| URL | Expected |
|-----|----------|
| `https://suratpro.com/` | 200 |
| `https://suratpro.com/auth/login/` | 200 |
| `https://suratpro.com/sd/` | 302 → login |
| Redis | `docker compose -f docker-compose.prod.yml exec redis redis-cli ping` → PONG |

## 5) Performance (built in)

- **CSS:** `MINIFY_STATIC=True` → `style.min.css` via `rcssmin`
- **Static:** WhiteNoise `CompressedManifestStaticFilesStorage` + 1y cache headers
- **Nginx:** gzip for text/css/js, immutable cache for `/static/`
- **Django:** `GZipMiddleware`, Redis cache + sessions
- **Gunicorn:** `preload_app`, workers = `2 * CPU + 1`

## 6) Useful commands

```bash
# Logs
docker compose -f docker-compose.prod.yml logs -f web celery nginx

# Shell
docker compose -f docker-compose.prod.yml exec web python manage.py shell

# Migrations only
docker compose -f docker-compose.prod.yml exec web python manage.py migrate

# Re-collect static
docker compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput
```

## 7) Rollback

```bash
docker compose -f docker-compose.prod.yml down
# restore pg_data volume snapshot if needed
docker compose -f docker-compose.prod.yml --env-file .env.prod up -d
```
