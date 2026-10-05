# Deployment — Sunrise Drilling on the VPS (167.233.160.177)

Live layout (what is actually on the server):

| What | Where |
|---|---|
| App checkout | `/home/deploy/sites/sunrise` |
| Virtualenv | `/home/deploy/sites/sunrise/.venv` |
| Env file | `/home/deploy/sites/sunrise/env` |
| Live DB + media | `/home/deploy/sites/sunrise-data/` (**outside the repo**) |
| Gunicorn | `127.0.0.1:8110`, systemd service `sunrise`, user `deploy` |
| Nginx site | `/etc/nginx/sites-available/sunrise` → `sunrise.mtirop.com` |

How CI/CD works:

- **Every push / PR** → GitHub Actions runs migration checks, Django checks,
  the test suite, collectstatic and a production-settings audit.
- **Every push to `main` that passes** → GitHub SSHes into the VPS, runs
  `git reset --hard origin/main` and `deploy/deploy.sh` (deps → migrate →
  collectstatic → restart), then curls `SITE_URL` and fails if not HTTP 200.

---

## Finish the server setup (run once, as root)

The app is installed but needs these fixes before it works properly:

### 1. Move live data OUT of the repo

`git update-index --skip-worktree db.sqlite3` is not enough — CI deploys
with `git reset --hard`, which can still clobber the file. The settings
already support external paths:

```bash
cd /home/deploy/sites/sunrise
systemctl stop sunrise

mkdir -p /home/deploy/sites/sunrise-data/media
cp db.sqlite3 /home/deploy/sites/sunrise-data/db.sqlite3
cp -rn media/. /home/deploy/sites/sunrise-data/media/

cat >> env <<'ENV'
DJANGO_DB_PATH=/home/deploy/sites/sunrise-data/db.sqlite3
DJANGO_MEDIA_ROOT=/home/deploy/sites/sunrise-data/media
ENV

git update-index --no-skip-worktree db.sqlite3 && git checkout -- db.sqlite3
```

### 2. Fix ownership (cloned as root, service runs as deploy)

SQLite and uploads need write access for the `deploy` user, or the
contact form and admin image uploads will error:

```bash
chown -R deploy:deploy /home/deploy/sites/sunrise /home/deploy/sites/sunrise-data
```

### 3. HTTPS — or the site redirects into a wall

With `DJANGO_DEBUG=False` the app force-redirects to HTTPS (good for
production). Until the certificate exists, plain HTTP will loop/fail.
Either get the cert now (DNS for `sunrise.mtirop.com` must already point
at the server):

```bash
apt install -y certbot python3-certbot-nginx
certbot --nginx -d sunrise.mtirop.com
```

…or, only as a temporary measure, add `DJANGO_SSL_REDIRECT=False` to the
env file and remove it after certbot.

### 4. Nginx media path + restart everything

Point `/media/` at the external data dir (or copy the repo's
`deploy/nginx.conf` which already has it):

```bash
sed -i 's#alias /home/deploy/sites/sunrise/media/#alias /home/deploy/sites/sunrise-data/media/#' /etc/nginx/sites-available/sunrise
nginx -t && systemctl reload nginx
systemctl start sunrise
curl -sI http://127.0.0.1:8110/ | head -1   # expect HTTP 301 (to https) or 200
```

### 5. Email + admin account

```bash
# Gmail App Password (Google Account -> Security -> 2-Step Verification -> App passwords)
sed -i 's/^EMAIL_HOST_PASSWORD=.*/EMAIL_HOST_PASSWORD=<app password>/' /home/deploy/sites/sunrise/env
systemctl restart sunrise

# Admin login for /admin/ and /dashboard/
cd /home/deploy/sites/sunrise
set -a; . ./env; set +a
.venv/bin/python manage.py createsuperuser
```

## Connect GitHub auto-deploy (once)

Repo → **Settings → Secrets and variables → Actions** → add:

| Secret | Value |
|---|---|
| `VPS_HOST` | `167.233.160.177` |
| `VPS_USER` | `root` (or `deploy` + sudoers rule below) |
| `VPS_SSH_KEY` | contents of the matching **private** key (e.g. `C:\Users\mtiro\.ssh\mtirop_deploy`) |
| `SITE_URL` | `https://sunrise.mtirop.com` (optional health check) |

The deploy script fixes file ownership automatically when CI connects as
root. To use the `deploy` user instead, allow it to restart the service:

```bash
echo "deploy ALL=(ALL) NOPASSWD: /usr/bin/systemctl restart sunrise, /usr/bin/systemctl is-active --quiet sunrise" > /etc/sudoers.d/sunrise-deploy
chmod 440 /etc/sudoers.d/sunrise-deploy
```

From then on: **push to `main` → tests run → server updates itself.**
Watch runs under the repo's Actions tab. Rollback = `git revert` + push.

## Backups

Everything that matters is in `/home/deploy/sites/sunrise-data/`:

```bash
echo '0 2 * * * root tar czf /root/sunrise-backup-$(date +\%F).tar.gz -C /home/deploy/sites sunrise-data && find /root -name "sunrise-backup-*.tar.gz" -mtime +14 -delete' > /etc/cron.d/sunrise-backup
```

## Useful commands

```bash
systemctl status sunrise            # app status
journalctl -u sunrise -n 50 -f      # app logs (gunicorn logs to journal)
sudo -u deploy bash /home/deploy/sites/sunrise/deploy/deploy.sh   # manual deploy
```
