#!/usr/bin/env python3
"""Wait for PostgreSQL and Redis before Django migrations (Docker entrypoint)."""
import os
import sys
import time

MAX_WAIT = int(os.environ.get("WAIT_MAX_SECONDS", "90"))


def wait_db():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
    import django
    for i in range(MAX_WAIT):
        try:
            django.setup()
            from django.db import connection
            connection.ensure_connection()
            print("Database is ready.")
            return
        except Exception as exc:
            if i == 0:
                print(f"Waiting for database... ({exc})")
            time.sleep(1)
    sys.exit("Database not ready after timeout.")


def wait_redis():
    url = os.environ.get("REDIS_URL", "redis://redis:6379/0")
    use_redis = os.environ.get("USE_REDIS_CACHE", "") or os.environ.get("USE_REDIS_SESSIONS", "")
    if use_redis.lower() not in ("true", "1", "yes"):
        return
    import redis
    for i in range(MAX_WAIT):
        try:
            redis.from_url(url).ping()
            print("Redis is ready.")
            return
        except Exception as exc:
            if i == 0:
                print(f"Waiting for Redis... ({exc})")
            time.sleep(1)
    sys.exit("Redis not ready after timeout.")


if __name__ == "__main__":
    wait_db()
    wait_redis()
