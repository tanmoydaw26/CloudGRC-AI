#!/bin/bash
# Quick local development setup
set -euo pipefail
GREEN='\033[0;32m'; NC='\033[0m'
log() { echo -e "${GREEN}[setup] $1${NC}"; }

log "Setting up CloudGRC-AI local development environment..."

# Check Docker
command -v docker &>/dev/null || { echo "Install Docker first: https://docs.docker.com/get-docker/"; exit 1; }

# Copy env files
[[ ! -f backend/.env.dev ]] && cp .env.production.example backend/.env.dev && log "Created backend/.env.dev — edit it with your values"
[[ ! -f frontend/.env.local ]] && cp frontend/.env.local.example frontend/.env.local && log "Created frontend/.env.local"

# Start dev stack
log "Starting development stack..."
docker compose -f docker-compose.dev.yml up -d

log "Waiting for services..."
sleep 15

log "═══════════════════════════════════"
log "  Dev environment ready!"
log "  Frontend:  http://localhost:3000"
log "  API:       http://localhost:8000"
log "  API Docs:  http://localhost:8000/api/docs"
log "═══════════════════════════════════"
