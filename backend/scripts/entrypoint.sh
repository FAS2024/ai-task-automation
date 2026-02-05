#!/usr/bin/env sh
set -e

export PYTHONPATH="/app"

echo "Waiting for database..."
python - <<'PY'
import os
import time
from sqlalchemy import create_engine, text

url = os.environ.get("DATABASE_URL", "")
if not url:
    raise SystemExit("DATABASE_URL not set")

for _ in range(30):
    try:
        engine = create_engine(url, pool_pre_ping=True)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        break
    except Exception:
        time.sleep(1)
else:
    raise SystemExit("Database not ready")
PY

if [ "${RUN_MIGRATIONS:-true}" = "true" ]; then
  echo "Running migrations..."
  alembic upgrade head
fi

exec "$@"
