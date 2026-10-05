#!/usr/bin/env bash
# Server-side deploy script. Run from the repo root on the VPS:
#   bash deploy/deploy.sh
# Idempotent: safe to run on every deploy (CI runs it after git reset).
# Layout (override with environment variables if yours differs):
#   APP_DIR   /home/deploy/sites/sunrise        the git checkout
#   DATA_DIR  /home/deploy/sites/sunrise-data   live DB + media, OUTSIDE the repo
#   VENV      $APP_DIR/.venv
#   ENV_FILE  $APP_DIR/env
#   SERVICE   sunrise
#   RUN_USER  deploy                             user the systemd service runs as
set -euo pipefail

APP_DIR="${APP_DIR:-/home/deploy/sites/sunrise}"
DATA_DIR="${DATA_DIR:-/home/deploy/sites/sunrise-data}"
VENV="${VENV:-$APP_DIR/.venv}"
ENV_FILE="${ENV_FILE:-$APP_DIR/env}"
SERVICE="${SERVICE:-sunrise}"
RUN_USER="${RUN_USER:-deploy}"

cd "$APP_DIR"

echo "==> Ensuring data directories exist"
mkdir -p "$DATA_DIR/media"

# First run only: seed the live DB and media from the repo copies.
if [ ! -f "$DATA_DIR/db.sqlite3" ] && [ -f "$APP_DIR/db.sqlite3" ]; then
    echo "==> First deploy: seeding live database and media from repository"
    cp "$APP_DIR/db.sqlite3" "$DATA_DIR/db.sqlite3"
    cp -rn "$APP_DIR/media/." "$DATA_DIR/media/" 2>/dev/null || true
fi

echo "==> Ensuring virtualenv exists"
[ -d "$VENV" ] || python3 -m venv "$VENV"

echo "==> Installing dependencies"
"$VENV/bin/pip" install --upgrade pip -q
"$VENV/bin/pip" install -r requirements.txt -q

echo "==> Loading environment from $ENV_FILE"
set -a
# shellcheck disable=SC1090
source "$ENV_FILE"
set +a

# Safety: refuse to run against the in-repo DB, where git could clobber it.
if [ -z "${DJANGO_DB_PATH:-}" ]; then
    echo "ERROR: DJANGO_DB_PATH is not set in $ENV_FILE."
    echo "Add:  DJANGO_DB_PATH=$DATA_DIR/db.sqlite3"
    echo "      DJANGO_MEDIA_ROOT=$DATA_DIR/media"
    exit 1
fi

echo "==> Running migrations"
"$VENV/bin/python" manage.py migrate --noinput

echo "==> Collecting static files"
"$VENV/bin/python" manage.py collectstatic --noinput

# Keep ownership correct for the service user (uploads + sqlite writes),
# in case this script was run as root (e.g. from CI).
if [ "$(id -u)" -eq 0 ]; then
    echo "==> Fixing ownership for $RUN_USER"
    chown -R "$RUN_USER":"$RUN_USER" "$APP_DIR" "$DATA_DIR"
fi

echo "==> Restarting application"
if [ "$(id -u)" -eq 0 ]; then
    systemctl restart "$SERVICE"
    systemctl is-active --quiet "$SERVICE" && echo "==> $SERVICE is running"
else
    sudo /usr/bin/systemctl restart "$SERVICE"
    sudo /usr/bin/systemctl is-active --quiet "$SERVICE" && echo "==> $SERVICE is running"
fi

echo "==> Deploy complete: $(git rev-parse --short HEAD)"
