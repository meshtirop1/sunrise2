# Deployment Guide — Sunrise Drilling (VPS + CI/CD)

How the pipeline works:

- **Every push / pull request** → GitHub Actions runs migrations check,
  Django checks, the full test suite, collectstatic and a production
  settings check. A red ✗ means do not deploy.
- **Every push to `main` that passes tests** → GitHub automatically SSHes
  into the VPS, pulls the code, installs dependencies, migrates,
  collects static files and restarts the app — then hits the site URL to
  confirm it's up. Zero manual steps.

The live database and uploaded media live in `/srv/sunrise/data/`,
**outside the repository**, so deployments can never overwrite them.

---

## 1. One-time VPS setup (Ubuntu 22.04/24.04)

Run as root (or with sudo):

```bash
# Packages
apt update && apt install -y python3-venv python3-pip nginx git certbot python3-certbot-nginx

# Deploy user and directory layout
adduser --disabled-password --gecos "" deploy
usermod -aG www-data deploy
mkdir -p /srv/sunrise/{data/media,logs}
chown -R deploy:www-data /srv/sunrise

# Clone the repository
sudo -u deploy git clone https://github.com/meshtirop1/sunrise2.git /srv/sunrise/app
```

### Environment file

Create `/srv/sunrise/.env` (owner `deploy`, mode 600) based on
`.env.example` in the repo:

```bash
DJANGO_SECRET_KEY=<generate: python3 -c "import secrets; print(secrets.token_urlsafe(50))">
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=sunrisedrillingltd.com,www.sunrisedrillingltd.com,<server-ip>
DJANGO_CSRF_TRUSTED_ORIGINS=https://sunrisedrillingltd.com,https://www.sunrisedrillingltd.com
DJANGO_DB_PATH=/srv/sunrise/data/db.sqlite3
DJANGO_MEDIA_ROOT=/srv/sunrise/data/media
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=sunrisedrillingltd@gmail.com
EMAIL_HOST_PASSWORD=<Gmail App Password>
DEFAULT_FROM_EMAIL=sunrisedrillingltd@gmail.com
```

```bash
chown deploy:deploy /srv/sunrise/.env && chmod 600 /srv/sunrise/.env
```

### First deploy + services

```bash
# First deploy (creates venv, seeds the data dir, migrates, collectstatic)
sudo -u deploy bash -c "cd /srv/sunrise/app && bash deploy/deploy.sh" || true  # service not installed yet

# Install the systemd service
cp /srv/sunrise/app/deploy/sunrise.service /etc/systemd/system/sunrise.service
systemctl daemon-reload
systemctl enable --now sunrise
systemctl status sunrise

# Allow the deploy user to restart the app without a password (CI needs this)
echo "deploy ALL=(ALL) NOPASSWD: /usr/bin/systemctl restart sunrise, /usr/bin/systemctl is-active --quiet sunrise" \
  > /etc/sudoers.d/sunrise-deploy
chmod 440 /etc/sudoers.d/sunrise-deploy

# Nginx
cp /srv/sunrise/app/deploy/nginx.conf /etc/nginx/sites-available/sunrise
ln -s /etc/nginx/sites-available/sunrise /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl reload nginx

# HTTPS (after the domain's DNS A record points at this server)
certbot --nginx -d sunrisedrillingltd.com -d www.sunrisedrillingltd.com
```

### Create your admin account

```bash
sudo -u deploy bash -c "cd /srv/sunrise/app && set -a && source /srv/sunrise/.env && set +a && /srv/sunrise/venv/bin/python manage.py createsuperuser"
```

## 2. One-time GitHub setup

Generate a deploy SSH key **on the VPS** as the deploy user:

```bash
sudo -u deploy ssh-keygen -t ed25519 -f /home/deploy/.ssh/github_deploy -N ""
sudo -u deploy bash -c "cat /home/deploy/.ssh/github_deploy.pub >> /home/deploy/.ssh/authorized_keys"
sudo -u deploy chmod 600 /home/deploy/.ssh/authorized_keys
cat /home/deploy/.ssh/github_deploy   # <- this PRIVATE key goes into GitHub
```

Then in GitHub: **repo → Settings → Secrets and variables → Actions →
New repository secret**, add:

| Secret | Value |
|---|---|
| `VPS_HOST` | your server IP or hostname |
| `VPS_USER` | `deploy` |
| `VPS_SSH_KEY` | the private key printed above (whole file) |
| `VPS_PORT` | `22` (optional, only if different) |
| `SITE_URL` | `https://sunrisedrillingltd.com` (optional health check) |

Until `VPS_HOST` is set, the deploy job skips itself with a warning and
only the tests run — so CI is useful immediately and CD switches on the
moment you add the secrets.

## 3. Day-to-day

- Push to `main` → tests run → site deploys itself. Watch it under the
  repo's **Actions** tab.
- A failing test **blocks** the deployment.
- Rollback: `git revert <bad commit> && git push` — the pipeline deploys
  the revert the same way.

## 4. Backups (recommended)

Everything that matters lives in `/srv/sunrise/data/`. A simple nightly
backup:

```bash
echo '0 2 * * * deploy tar czf /srv/sunrise/backup-$(date +\%F).tar.gz -C /srv/sunrise data && find /srv/sunrise -name "backup-*.tar.gz" -mtime +14 -delete' \
  > /etc/cron.d/sunrise-backup
```
