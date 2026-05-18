#!/bin/sh
set -e

echo "==> Waiting for database and Redis..."
python scripts/wait_for_services.py

if [ "${MINIFY_STATIC:-false}" = "True" ] || [ "${MINIFY_STATIC:-false}" = "true" ]; then
  echo "==> Minifying CSS..."
  python scripts/minify_css.py
fi

echo "==> Running migrations..."
python manage.py migrate --noinput

echo "==> Collecting static files (gzip + manifest via WhiteNoise)..."
python manage.py collectstatic --noinput

echo "==> Seeding plans..."
python manage.py seed_plans

echo "==> Starting Gunicorn..."
exec gunicorn core.wsgi:application -c gunicorn.conf.py
