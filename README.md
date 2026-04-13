<div align="center">

<img src="https://img.shields.io/badge/CloudGRC--AI-v2.0-00ffe7?style=for-the-badge&logo=shield&logoColor=black" />
<img src="https://img.shields.io/badge/AWS-boto3-FF9900?style=for-the-badge&logo=amazonaws&logoColor=white" />
<img src="https://img.shields.io/badge/GCP-google--cloud-4285F4?style=for-the-badge&logo=googlecloud&logoColor=white" />
<img src="https://img.shields.io/badge/Azure-azure--mgmt-00A4EF?style=for-the-badge&logo=microsoftazure&logoColor=white" />
<img src="https://img.shields.io/badge/FastAPI-0.111-009688?style=for-the-badge&logo=fastapi&logoColor=white" />
<img src="https://img.shields.io/badge/Next.js-14-black?style=for-the-badge&logo=next.js&logoColor=white" />
<img src="https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white" />
<img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" />

# 🛡️ CloudGRC-AI
### Automated Cloud Compliance & Risk Scanner

**A production-grade, multi-cloud security scanning SaaS platform.**
Scans AWS, GCP, and Azure environments for misconfigurations — maps findings to ISO 27001, NIST CSF, and CIS Benchmarks — and generates AI-powered audit reports.

[Live Demo](#) · [API Docs](#api-documentation) · [Report Bug](https://github.com/tanmoydaw26/CloudGRC-AI/issues) · [Request Feature](https://github.com/tanmoydaw26/CloudGRC-AI/issues)

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Architecture](#-architecture)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Quick Start](#-quick-start)
- [Environment Variables](#-environment-variables)
- [API Documentation](#-api-documentation)
- [Compliance Mapping](#-compliance-mapping)
- [Pricing Plans](#-pricing-plans)
- [Deployment](#-deployment)
- [CI/CD Pipeline](#-cicd-pipeline)
- [Security](#-security)
- [Screenshots](#-screenshots)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🎯 Overview

**CloudGRC-AI** is a full-stack SaaS platform that automates cloud security compliance scanning across AWS, GCP, and Azure. It is built for security engineers, GRC analysts, and compliance teams who need audit-ready reports mapped to international frameworks.

### What It Does

```
Your Cloud Environment
        │
        ▼
┌───────────────────────────────────────────┐
│           CloudGRC-AI Scanner             │
│                                           │
│  IAM Checks → Storage Checks → Network   │
│  Checks → Logging Checks                 │
└───────────────────┬───────────────────────┘
                    │
                    ▼
        Compliance Mapping Engine
        ISO 27001 │ NIST CSF │ CIS
                    │
                    ▼
          AI Report Generator (GPT)
                    │
                    ▼
    PDF Report │ JSON Export │ Dashboard
```

---

## ✨ Features

### 🔍 Security Checks

| Category | Check | AWS | GCP | Azure |
|---|---|:---:|:---:|:---:|
| **IAM** | Overly permissive roles (`*:*`) | ✅ | ✅ | ✅ |
| **IAM** | MFA disabled users | ✅ | ✅ | ✅ |
| **IAM** | Root / super-admin account usage | ✅ | ✅ | ✅ |
| **IAM** | Stale access keys (>90 days) | ✅ | — | — |
| **Storage** | Public S3 / GCS / Blob exposure | ✅ | ✅ | ✅ |
| **Storage** | Encryption disabled | ✅ | ✅ | ✅ |
| **Storage** | HTTPS not enforced | ✅ | ✅ | ✅ |
| **Network** | Open ports to `0.0.0.0/0` | ✅ | ✅ | ✅ |
| **Network** | Misconfigured firewall rules | ✅ | ✅ | ✅ |
| **Network** | VPC flow logs disabled | ✅ | ✅ | — |
| **Logging** | CloudTrail / Audit log disabled | ✅ | ✅ | ✅ |
| **Logging** | Log retention < 90 days | ✅ | ✅ | ✅ |
| **Logging** | Monitoring / alerts not configured | ✅ | ✅ | ✅ |

### 🗺️ Compliance Mapping Engine
Every finding is automatically mapped to:
- **ISO 27001:2022** — Annex A controls (A.5 through A.18)
- **NIST CSF 2.0** — Identify, Protect, Detect, Respond, Recover
- **CIS Benchmarks** — Controls 1–18

### 🤖 AI Report Generator
- Executive Summary for C-suite
- Technical Findings for security teams
- Business Impact analysis
- Step-by-step Remediation Plan
- Powered by **OpenAI GPT-4o-mini** with template fallback

### 📊 Risk Scoring
- Severity: **Critical / High / Medium / Low / Info**
- Risk Score: **0–100** (weighted by severity count)
- Compliance Percentage: **0–100%**

### 💳 SaaS Billing
- Free / Starter / Pro / Enterprise tiers
- **Razorpay** payment gateway (INR)
- Monthly scan quota enforcement
- Automatic plan upgrade on payment verification

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                      NGINX (SSL/TLS)                    │
│              Rate Limiting + Security Headers           │
└──────────────────┬────────────────┬────────────────────┘
                   │                │
          ┌────────▼──────┐  ┌──────▼────────┐
          │  Next.js 14   │  │  FastAPI       │
          │  Frontend     │  │  Backend       │
          │  (Port 3000)  │  │  (Port 8000)   │
          └───────────────┘  └──────┬─────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
             ┌──────▼─────┐ ┌──────▼─────┐ ┌──────▼──────┐
             │ PostgreSQL  │ │   Redis    │ │   Celery    │
             │  (DB)       │ │  (Cache/   │ │  Worker     │
             │             │ │   Queue)   │ │  (Scans)    │
             └─────────────┘ └────────────┘ └─────────────┘
                                                   │
                              ┌────────────────────┘
                              │
              ┌───────────────▼──────────────────┐
              │         Scan Engine              │
              │  AWS (boto3) │ GCP │ Azure SDK   │
              │  IAM · Storage · Network · Logs  │
              │  Compliance Mapping Engine       │
              │  AI Report (OpenAI)              │
              │  PDF Generator (ReportLab)       │
              └──────────────────────────────────┘
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | Next.js 14, TypeScript, Tailwind CSS, Recharts, Zustand, React Query |
| **Backend** | FastAPI, Python 3.12, SQLAlchemy (async), Pydantic v2 |
| **Database** | PostgreSQL 16 (findings stored as JSONB) |
| **Task Queue** | Celery + Redis |
| **Cloud SDKs** | boto3 (AWS), google-cloud SDK (GCP), azure-mgmt (Azure) |
| **AI** | OpenAI GPT-4o-mini |
| **PDF** | ReportLab |
| **Payments** | Razorpay |
| **Auth** | JWT (access + refresh tokens), bcrypt, Fernet encryption |
| **Infra** | Docker Compose, Nginx, Let's Encrypt (certbot) |
| **CI/CD** | GitHub Actions |
| **Monitoring** | Celery Flower, Prometheus-ready |

---

## 📁 Project Structure

```
CloudGRC-AI/
│
├── 📂 backend/                    # FastAPI Backend
│   ├── core/
│   │   ├── config.py              # Pydantic settings
│   │   └── security.py            # JWT + bcrypt + Fernet
│   ├── db/
│   │   └── base.py                # Async SQLAlchemy engine
│   ├── api/
│   │   ├── models/                # SQLAlchemy ORM models
│   │   │   ├── user.py
│   │   │   ├── scan.py
│   │   │   └── credential.py
│   │   ├── schemas/               # Pydantic request/response schemas
│   │   ├── routes/                # API route handlers
│   │   │   ├── auth.py
│   │   │   ├── scans.py
│   │   │   ├── credentials.py
│   │   │   ├── billing.py
│   │   │   └── dashboard.py
│   │   ├── services/              # Business logic layer
│   │   └── middleware/            # JWT auth + rate limiter
│   ├── workers/
│   │   ├── celery_app.py          # Celery configuration
│   │   └── tasks.py               # Async scan execution task
│   └── main.py                    # FastAPI app entry point
│
├── 📂 scan_engine/                # Cloud Security Scanner
│   ├── connectors/
│   │   ├── aws.py                 # boto3 session management
│   │   ├── gcp.py                 # Google Cloud auth
│   │   └── azure.py               # Azure Service Principal
│   ├── checks/
│   │   ├── iam.py                 # IAM security checks
│   │   ├── storage.py             # Storage checks
│   │   ├── network.py             # Network/firewall checks
│   │   └── logging.py             # Logging/monitoring checks
│   ├── compliance/
│   │   └── mapping.py             # ISO 27001 · NIST · CIS mapping
│   └── reporting/
│       ├── ai_summary.py          # OpenAI GPT report
│       └── pdf_generator.py       # ReportLab PDF
│
├── 📂 frontend/                   # Next.js 14 Frontend
│   └── src/
│       ├── app/
│       │   ├── (auth)/            # Login + Register pages
│       │   └── (dashboard)/       # Protected dashboard pages
│       │       ├── dashboard/     # Overview + charts
│       │       ├── scans/         # Scan list + detail + findings
│       │       ├── credentials/   # Cloud credential management
│       │       ├── billing/       # Pricing + Razorpay checkout
│       │       └── settings/      # Profile + security
│       ├── services/api.ts        # Axios client + interceptors
│       ├── store/authStore.ts     # Zustand global auth state
│       └── types/index.ts         # TypeScript interfaces
│
├── 📂 infrastructure/
│   ├── nginx/
│   │   ├── nginx.prod.conf        # Production: SSL + rate limiting
│   │   └── nginx.dev.conf         # Development: HTTP only
│   └── postgres/
│       └── init.sql               # DB extensions init
│
├── 📂 scripts/
│   ├── deploy.sh                  # One-command EC2 deployment
│   ├── update.sh                  # Zero-downtime rolling update
│   ├── backup.sh                  # PostgreSQL → S3 backup
│   └── setup_dev.sh               # Local dev environment setup
│
├── 📂 .github/workflows/
│   └── deploy.yml                 # CI/CD: test → build → deploy
│
├── docker-compose.prod.yml        # Production: 8 services
├── docker-compose.dev.yml         # Development: 5 services
├── .env.production.example        # Environment variable template
└── README.md
```

---

## 🚀 Quick Start

### Option A — Local Development (Recommended for beginners)

**Prerequisites:** Docker Desktop installed

```bash
# 1. Clone the repository
git clone https://github.com/tanmoydaw26/CloudGRC-AI.git
cd CloudGRC-AI

# 2. Run the automated setup script
chmod +x scripts/setup_dev.sh
./scripts/setup_dev.sh

# 3. Open your browser
# Frontend:  http://localhost:3000
# API Docs:  http://localhost:8000/api/docs
# Flower:    http://localhost:5555
```

### Option B — Manual Setup

```bash
# 1. Clone
git clone https://github.com/tanmoydaw26/CloudGRC-AI.git
cd CloudGRC-AI

# 2. Set up environment
cp .env.production.example backend/.env.dev
# Edit backend/.env.dev with your values

cp frontend/.env.local.example frontend/.env.local
# Edit frontend/.env.local

# 3. Start with Docker Compose
docker compose -f docker-compose.dev.yml up --build

# 4. Access
# Frontend:  http://localhost:3000
# API:       http://localhost:8000
# API Docs:  http://localhost:8000/api/docs
```

### Option C — Run Without Docker (Pure Python + Node)

```bash
# Backend
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn backend.main:app --reload --port 8000

# In a new terminal — Frontend
cd frontend
npm install
npm run dev
```

---

## 🔐 Environment Variables

Copy `.env.production.example` to `.env` and fill in these required values:

| Variable | Description | Required |
|---|---|:---:|
| `SECRET_KEY` | JWT signing key (64 chars) — `openssl rand -hex 32` | ✅ |
| `FERNET_KEY` | AES-256 encryption key — see below | ✅ |
| `DATABASE_URL` | PostgreSQL async connection string | ✅ |
| `REDIS_URL` | Redis connection string | ✅ |
| `RAZORPAY_KEY_ID` | Razorpay API key ID | ✅ |
| `RAZORPAY_KEY_SECRET` | Razorpay secret key | ✅ |
| `OPENAI_API_KEY` | OpenAI API key (for AI reports) | ⚪ Optional |
| `AWS_ACCESS_KEY_ID` | AWS key for S3 PDF storage | ⚪ Optional |
| `SMTP_USER` | SMTP email for notifications | ⚪ Optional |
| `SENTRY_DSN` | Sentry error tracking | ⚪ Optional |

**Generate a Fernet key:**
```python
from cryptography.fernet import Fernet
print(Fernet.generate_key().decode())
```

---

## 📡 API Documentation

Interactive docs available at `/api/docs` (Swagger UI) and `/api/redoc`.

### Authentication
```
POST /api/v1/auth/register   — Create account
POST /api/v1/auth/login      — Login, receive JWT tokens
POST /api/v1/auth/refresh    — Refresh access token
GET  /api/v1/auth/me         — Get current user profile
```

### Scans
```
POST   /api/v1/scans          — Trigger new scan
GET    /api/v1/scans          — List all scans (paginated)
GET    /api/v1/scans/{id}     — Full scan detail + findings + AI report
GET    /api/v1/scans/{id}/download — Download PDF report
DELETE /api/v1/scans/{id}     — Delete scan record
```

### Credentials
```
POST   /api/v1/credentials    — Save encrypted cloud credentials
GET    /api/v1/credentials    — List saved credentials (labels only)
DELETE /api/v1/credentials/{id} — Delete credential
```

### Billing
```
GET  /api/v1/billing/plans    — List all pricing plans
POST /api/v1/billing/order    — Create Razorpay payment order
POST /api/v1/billing/verify   — Verify payment + upgrade plan
GET  /api/v1/billing/status   — Current plan and usage
```

### Dashboard
```
GET /api/v1/dashboard/stats   — Aggregated stats + recent scans
```

### Sample Finding Response
```json
{
  "cloud": "AWS",
  "category": "IAM",
  "issue": "Root account does not have MFA enabled",
  "resource": "root-account",
  "severity": "Critical",
  "detail": "AWS root account MFA is disabled. This is a critical risk.",
  "frameworks": {
    "ISO27001": "A.9.2 — User Access Management; A.9.4 — System Access Control",
    "NIST_CSF": "PR.AC-1: Identities and credentials are managed",
    "CIS": "CIS Control 5: Account Management"
  }
}
```

---

## 🗺️ Compliance Mapping

| Severity | ISO 27001 Controls | NIST CSF | CIS Controls |
|---|---|---|---|
| Critical IAM | A.9.2, A.9.4 | PR.AC-1, PR.AC-6 | CIS 5, CIS 6 |
| Storage Public | A.8.2, A.13.1 | PR.DS-1, PR.DS-5 | CIS 3, CIS 13 |
| Network Open | A.13.1, A.13.2 | PR.AC-5, DE.CM-1 | CIS 12 |
| Logging Disabled | A.12.4, A.16.1 | DE.CM-1, DE.CM-7 | CIS 8 |
| Encryption Off | A.10.1, A.8.2 | PR.DS-1, PR.DS-2 | CIS 3, CIS 10 |

---

## 💰 Pricing Plans

| Feature | Free | Starter ₹999/mo | Pro ₹2999/mo | Enterprise |
|---|:---:|:---:|:---:|:---:|
| Scans per month | 1 (demo) | 10 | Unlimited | Unlimited |
| Real cloud scan | ❌ | ✅ (1 cloud) | ✅ (all 3) | ✅ |
| PDF reports | ❌ | ✅ | ✅ | ✅ |
| AI reports | ❌ | ❌ | ✅ | ✅ |
| API access | ❌ | ❌ | ✅ | ✅ |
| White-label | ❌ | ❌ | ❌ | ✅ |
| SLA | ❌ | ❌ | ❌ | ✅ |
| Support | Community | Email | Priority | Dedicated |

---

## ☁️ Deployment

### Deploy to AWS EC2 (One Command)

```bash
# SSH into your Ubuntu 22.04/24.04 EC2 instance
ssh -i your-key.pem ubuntu@YOUR_EC2_IP

# Upload project
# (from local machine)
scp -r CloudGRC-AI/ ubuntu@YOUR_EC2_IP:/opt/cloudgrc

# On server — fill in .env then run:
sudo /opt/cloudgrc/scripts/deploy.sh your-domain.com your@email.com
```

The deploy script automatically:
- ✅ Installs Docker and Docker Compose
- ✅ Configures UFW firewall (ports 22, 80, 443 only)
- ✅ Enables fail2ban
- ✅ Obtains Let's Encrypt SSL certificate
- ✅ Builds all Docker images
- ✅ Starts all 8 services
- ✅ Sets up SSL auto-renewal cron

### Alternative Platforms

| Platform | Command |
|---|---|
| **Railway** | Connect GitHub repo → set env vars → deploy |
| **Render** | `render.yaml` supported — contact for template |
| **DigitalOcean** | Same as EC2 — use `deploy.sh` on Ubuntu droplet |
| **Vercel (frontend only)** | `cd frontend && vercel --prod` |

---

## 🔄 CI/CD Pipeline

Every push to `main` triggers:

```
Push to main
     │
     ▼
┌─────────────────┐    ┌──────────────────┐
│  Test Backend   │    │  Test Frontend   │
│  pytest + lint  │    │  TypeScript + ESLint │
└────────┬────────┘    └────────┬─────────┘
         └──────────┬───────────┘
                    ▼
         ┌──────────────────────┐
         │  Build Docker Images │
         │  Push to GHCR        │
         └──────────┬───────────┘
                    ▼
         ┌──────────────────────┐
         │  SSH → EC2           │
         │  docker compose pull │
         │  Zero-downtime restart│
         └──────────────────────┘
```

**Required GitHub Secrets:**

```
EC2_HOST              → Your server IP
EC2_SSH_KEY           → Your .pem file contents
DOMAIN                → your-domain.com
NEXT_PUBLIC_API_URL   → https://your-domain.com/api/v1
NEXT_PUBLIC_RAZORPAY_KEY_ID → rzp_live_xxx
```

---

## 🔒 Security

This project follows security best practices:

- **No hardcoded credentials** — all secrets via environment variables
- **AES-256 encryption** (Fernet) for all stored cloud credentials
- **JWT authentication** with short-lived access tokens + refresh tokens
- **bcrypt** password hashing (cost factor 12)
- **Rate limiting** — 30 req/min per IP on API, 10 req/min on auth
- **Security headers** — HSTS, CSP, X-Frame-Options, X-Content-Type-Options
- **TLS 1.2/1.3 only** — older protocols disabled in Nginx
- **Non-root Docker containers** — all services run as `appuser` (UID 1000)
- **Internal Docker network** — DB and Redis not exposed to public
- **Principle of least privilege** — IAM roles use minimal permissions

### Responsible Disclosure

Found a security issue? Email: **security@cloudgrc.ai**
Please do NOT create public GitHub issues for security vulnerabilities.

---

## 🤝 Contributing

Contributions are welcome! Here is how:

```bash
# 1. Fork the repository
# 2. Create your feature branch
git checkout -b feature/AmazingFeature

# 3. Make changes and commit
git commit -m "Add: AmazingFeature"

# 4. Push to your branch
git push origin feature/AmazingFeature

# 5. Open a Pull Request
```

Please follow the existing code style and add tests for new features.

---

## 📄 License

Distributed under the **MIT License**. See `LICENSE` for details.

---

## 👨‍💻 Author

**Tanmoy Daw**
Cybersecurity & Data Privacy Compliance Professional

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0077B5?style=flat&logo=linkedin)](https://linkedin.com/in/tanmoydaw26)
[![GitHub](https://img.shields.io/badge/GitHub-Follow-181717?style=flat&logo=github)](https://github.com/tanmoydaw26)

---

<div align="center">

**⭐ If this project helped you, please give it a star on GitHub!**

Made with ❤️ in Kolkata, India 🇮🇳

</div>
