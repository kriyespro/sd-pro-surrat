#!/usr/bin/env bash
set -euo pipefail

echo "== SuratPro release checks =="

echo "-- Django system check"
python manage.py check

echo "-- Migrations up to date"
python manage.py migrate --check

echo "-- Run test suite"
python manage.py test --verbosity=1

echo "-- Verify critical routes"
python - <<'PY'
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()
from django.test import Client

c = Client(SERVER_NAME='localhost')
paths = ['/', '/auth/login/', '/browse/', '/pricing/', '/referral/']
for p in paths:
    r = c.get(p)
    if r.status_code >= 400:
        raise SystemExit(f"Route check failed: {p} -> {r.status_code}")
print("All route checks passed.")
PY

echo "== All release checks passed. =="
