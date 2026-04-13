#!/bin/bash
# Zero-downtime rolling update
set -euo pipefail
APP_DIR="/opt/cloudgrc"
cd "$APP_DIR"
echo "Pulling latest code..."
git pull origin main
echo "Rebuilding images..."
docker compose -f docker-compose.prod.yml build backend frontend
echo "Restarting services (zero-downtime)..."
docker compose -f docker-compose.prod.yml up -d --no-deps backend frontend celery_worker
docker compose -f docker-compose.prod.yml exec nginx nginx -s reload
echo "Update complete. Cleaning old images..."
docker image prune -f
echo "Done!"
