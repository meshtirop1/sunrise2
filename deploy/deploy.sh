#!/usr/bin/env bash
# Server-side deploy script. Run from the repo root on the VPS:
#   bash deploy/deploy.sh
# Idempotent: safe to run on every deploy. The live database and uploaded
# media live in /srv/sunrise/data (outside the repo), so git never touches them.
set -euo pipefail

APP_DIR="/srv/sunrise/app"
DATA_DIR="/srv/sunrise/data"
VENV="/srv/sunrise/venv"
ENV_FILE="/srv/sunrise/.env"
SERVICE="sunrise"

cd "$APP_DIR"

echo "==> Ensuring data directories exist"
mkdir -p "$DATA_DIR/media"

# First deploy only: seed the production DB from the repo copy.
if [ ! -f "$DATA_DIR/db.sqlite3" ] && [ -f "$APP_DIR/db.sqlite3" ]; then
    echo "==> First deploy: seeding database from repository copy"
    cp "$APP_DIR/db.sqlite3" "$DATA_DIR/db.sqlite3"
    # Seed media uploads referenced by the seeded DB.
    cp -rn "$APP_DIR/media/." "$DATA_DIR/media/" 2>/dev/null || true
fi

echo "==> Ensuring virtualenv exists"
if [ ! -d "$VENV" ]; then
    python3 -m venv "$VENV"
fi

echo "==> Installing dependencies"
"$VENV/bin/pip" install --upgrade pip -q
"$VENV/bin/pip" install -r requirements.txt -q

echo "==> Loading environment from $ENV_FILE"
set -a
# shellcheck disable=SC1090
source "$ENV_FILE"
set +a

echo "==> Running migrations"
"$VENV/bin/python" manage.py migrate --noinput

echo "==> Collecting static files"
"$VENV/bin/python" manage.py collectstatic --noinput

echo "==> Restarting application"
sudo /usr/bin/systemctl restart "$SERVICE"
sleep 2
sudo /usr/bin/systemctl is-active --quiet "$SERVICE" && echo "==> $SERVICE is running"

echo "==> Deploy complete: $(git rev-parse --short HEAD)"
