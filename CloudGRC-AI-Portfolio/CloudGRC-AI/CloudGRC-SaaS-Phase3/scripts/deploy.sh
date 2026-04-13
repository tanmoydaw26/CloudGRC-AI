#!/bin/bash
# ═══════════════════════════════════════════════════════════
#  CloudGRC-AI — Production Deployment Script
#  Works on: Ubuntu 22.04 / 24.04 (AWS EC2, DigitalOcean, Hetzner)
#  Run as root or with sudo
# ═══════════════════════════════════════════════════════════

set -euo pipefail
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'

log()  { echo -e "${GREEN}[$(date +%H:%M:%S)] $1${NC}"; }
warn() { echo -e "${YELLOW}[WARN] $1${NC}"; }
err()  { echo -e "${RED}[ERROR] $1${NC}"; exit 1; }

DOMAIN="${1:-}"
EMAIL="${2:-}"
APP_DIR="/opt/cloudgrc"

[[ -z "$DOMAIN" ]] && err "Usage: ./deploy.sh your-domain.com admin@email.com"
[[ -z "$EMAIL"  ]] && err "Usage: ./deploy.sh your-domain.com admin@email.com"

log "Starting CloudGRC-AI deployment for $DOMAIN"

# ── Step 1: System packages ──
log "Installing system dependencies..."
apt-get update -qq
apt-get install -y -qq curl git ufw fail2ban unattended-upgrades

# ── Step 2: Docker ──
if ! command -v docker &>/dev/null; then
  log "Installing Docker..."
  curl -fsSL https://get.docker.com | sh
  usermod -aG docker ubuntu 2>/dev/null || true
  log "Docker installed: $(docker --version)"
else
  log "Docker already installed: $(docker --version)"
fi

# ── Step 3: Docker Compose plugin ──
if ! docker compose version &>/dev/null; then
  log "Installing Docker Compose plugin..."
  apt-get install -y docker-compose-plugin
fi

# ── Step 4: Firewall ──
log "Configuring UFW firewall..."
ufw --force reset
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable
log "Firewall configured"

# ── Step 5: fail2ban ──
log "Enabling fail2ban..."
systemctl enable --now fail2ban

# ── Step 6: Clone repo ──
log "Setting up application directory..."
mkdir -p "$APP_DIR"
if [[ -d "$APP_DIR/.git" ]]; then
  cd "$APP_DIR" && git pull origin main
else
  cd /opt
  git clone https://github.com/tanmoydaw26/CloudGRC-SaaS.git cloudgrc 2>/dev/null || {
    warn "Repo clone failed — copying files manually if needed"
    mkdir -p "$APP_DIR"
  }
fi

# ── Step 7: Environment file ──
if [[ ! -f "$APP_DIR/.env" ]]; then
  warn ".env file not found — copying template"
  [[ -f "$APP_DIR/.env.production.example" ]] && cp "$APP_DIR/.env.production.example" "$APP_DIR/.env"
  err "STOP: Fill in $APP_DIR/.env before continuing. Re-run after editing."
fi

log ".env file found"

# ── Step 8: SSL with Let's Encrypt ──
log "Obtaining SSL certificate for $DOMAIN..."
# First: start nginx on HTTP only to allow ACME challenge
cd "$APP_DIR"
docker compose -f docker-compose.prod.yml up -d nginx certbot 2>/dev/null || true
sleep 5

docker compose -f docker-compose.prod.yml run --rm certbot certonly \
  --webroot --webroot-path=/var/www/certbot \
  --email "$EMAIL" --agree-tos --no-eff-email \
  -d "$DOMAIN" -d "www.$DOMAIN" || warn "SSL cert failed — check domain DNS and try again"

# ── Step 9: Update nginx config with domain ──
log "Updating nginx config with domain $DOMAIN..."
sed -i "s/your-domain.com/$DOMAIN/g" "$APP_DIR/infrastructure/nginx/nginx.prod.conf"

# ── Step 10: Build and start all services ──
log "Building Docker images (this takes 3-5 minutes)..."
cd "$APP_DIR"
docker compose -f docker-compose.prod.yml build --no-cache

log "Starting all services..."
docker compose -f docker-compose.prod.yml up -d

# ── Step 11: Wait for health ──
log "Waiting for services to become healthy..."
sleep 20
if curl -sf "https://$DOMAIN/health" &>/dev/null; then
  log "Health check PASSED"
else
  warn "Health check failed — check logs: docker compose -f docker-compose.prod.yml logs backend"
fi

# ── Step 12: SSL auto-renewal cron ──
log "Setting up SSL auto-renewal..."
(crontab -l 2>/dev/null; echo "0 3 * * * cd $APP_DIR && docker compose -f docker-compose.prod.yml run --rm certbot renew && docker compose -f docker-compose.prod.yml exec nginx nginx -s reload") | crontab -

log "═══════════════════════════════════════════════"
log "  CloudGRC-AI Deployment Complete!"
log "  URL:       https://$DOMAIN"
log "  API Docs:  https://$DOMAIN/api/docs"
log "  Flower:    https://$DOMAIN/flower/"
log "  Logs:      docker compose -f docker-compose.prod.yml logs -f"
log "═══════════════════════════════════════════════"
