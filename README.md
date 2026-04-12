# 🛡️ CloudGRC-AI — Automated Cloud Compliance & Risk Scanner

> A production-grade, open-source multi-cloud security scanner that detects misconfigurations across **AWS, GCP, and Azure**, maps every finding to **ISO 27001:2022, NIST CSF, and CIS Benchmarks**, and generates a professional **PDF audit report** — with an AI-written narrative via OpenAI GPT.

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)
![AWS](https://img.shields.io/badge/AWS-boto3-orange?logo=amazonaws&logoColor=white)
![GCP](https://img.shields.io/badge/GCP-google--cloud-4285F4?logo=googlecloud&logoColor=white)
![Azure](https://img.shields.io/badge/Azure-azure--mgmt-0078D4?logo=microsoftazure&logoColor=white)
![Streamlit](https://img.shields.io/badge/UI-Streamlit-FF4B4B?logo=streamlit&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Production--Ready-brightgreen)

---

## 📋 Table of Contents

- [What It Does](#-what-it-does)
- [Architecture](#-architecture)
- [Quick Start — Demo Mode](#-quick-start--demo-mode-no-credentials-needed)
- [Real Environment Setup](#-real-environment-setup)
  - [AWS Setup](#-aws-setup)
  - [GCP Setup](#-gcp-setup)
  - [Azure Setup](#-azure-setup)
  - [OpenAI Setup](#-openai-setup-optional)
- [Running a Real Scan](#-running-a-real-scan)
- [Getting a PDF Report](#-getting-a-pdf-report)
- [Streamlit Dashboard](#-streamlit-dashboard)
- [Security Checks Covered](#-security-checks-covered)
- [Compliance Frameworks](#-compliance-frameworks)
- [Troubleshooting](#-troubleshooting)
- [Built By](#-built-by)

---

## 🔍 What It Does

- Scans **AWS, GCP, and Azure** for security misconfigurations across IAM, Storage, Network, and Logging
- Maps every finding to **ISO 27001:2022 Annex A**, **NIST CSF**, and **CIS Benchmark** controls
- Calculates a **risk score (0–100)** and **compliance percentage**
- Generates an **AI-written audit report** with Executive Summary, Business Impact, and Remediation Plan
- Exports **PDF, JSON, and CSV** audit reports
- Includes a full **Streamlit dashboard UI**

---

## 🏗️ Architecture

```
CloudGRC-AI/
├── connectors/
│   ├── aws.py            ← boto3 authentication & session
│   ├── gcp.py            ← Google Cloud SDK authentication
│   └── azure.py          ← Azure Service Principal authentication
├── checks/
│   ├── iam.py            ← MFA, root usage, wildcard policies, stale keys
│   ├── storage.py        ← Public buckets, encryption, HTTPS enforcement
│   ├── network.py        ← Open ports, 0.0.0.0/0 rules, VPC flow logs
│   └── logging.py        ← CloudTrail, log sinks, retention policies
├── compliance/
│   └── mapping.py        ← ISO 27001, NIST CSF, CIS mapping + risk scoring
├── reporting/
│   ├── ai_summary.py     ← OpenAI GPT narrative + template fallback
│   └── pdf_generator.py  ← ReportLab PDF with cover page and findings table
├── main.py               ← CLI orchestrator
├── app.py                ← Streamlit dashboard
├── requirements.txt
└── .env.example
```

---

## ⚡ Quick Start — Demo Mode (No Credentials Needed)

> Works immediately on any machine. Uses 14 built-in realistic findings.

```bash
# 1. Clone the repository
git clone https://github.com/tanmoydaw26/CloudGRC-AI
cd CloudGRC-AI

# 2. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run demo scan (no credentials needed)
python main.py --mock --org "Your Organisation"

# 5. Launch the dashboard
streamlit run app.py
# Opens at http://localhost:8501
# Tick "Use Mock Data" in the sidebar → click RUN SCAN
```

---

## 🔐 Real Environment Setup

### Step 1 — Create Your .env File

```bash
cp .env.example .env
nano .env          # or use any text editor
```

Fill in the credentials for the cloud providers you want to scan:

```bash
# ── AWS ──────────────────────────────────────────
AWS_ACCESS_KEY_ID=AKIAxxxxxxxxxxxxxxxxx
AWS_SECRET_ACCESS_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
AWS_DEFAULT_REGION=ap-south-1

# ── GCP ──────────────────────────────────────────
GCP_PROJECT_ID=your-gcp-project-id
GOOGLE_APPLICATION_CREDENTIALS=/absolute/path/to/gcp-service-account.json

# ── Azure ─────────────────────────────────────────
AZURE_SUBSCRIPTION_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
AZURE_TENANT_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
AZURE_CLIENT_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
AZURE_CLIENT_SECRET=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# ── OpenAI (optional — AI report narrative) ───────
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

Save and close: **Ctrl+O → Enter → Ctrl+X**

---

### ☁️ AWS Setup

#### 1. Create an IAM User for CloudGRC-AI

1. Go to **AWS Console → IAM → Users → Create User**
2. Name: `cloudgrc-scanner` (or any name)
3. Select **"Attach policies directly"**
4. Click **"Create inline policy"** and paste this JSON:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "iam:ListUsers",
        "iam:ListMFADevices",
        "iam:GetAccountSummary",
        "iam:ListAccessKeys",
        "iam:ListAttachedUserPolicies",
        "iam:ListUserPolicies",
        "iam:GetLoginProfile",
        "s3:ListAllMyBuckets",
        "s3:GetBucketAcl",
        "s3:GetBucketEncryption",
        "s3:GetBucketLogging",
        "s3:GetBucketVersioning",
        "s3:GetBucketPublicAccessBlock",
        "ec2:DescribeSecurityGroups",
        "ec2:DescribeInstances",
        "ec2:DescribeVpcs",
        "ec2:DescribeFlowLogs",
        "cloudtrail:DescribeTrails",
        "cloudtrail:GetTrailStatus",
        "cloudwatch:DescribeAlarms",
        "config:DescribeConfigurationRecorders"
      ],
      "Resource": "*"
    }
  ]
}
```

5. Name the policy: `CloudGRC-ReadOnly`
6. Click **Create User**

#### 2. Generate Access Keys

1. Click your new user → **Security credentials** tab
2. Click **Create access key** → Select **"Application running outside AWS"**
3. Copy the **Access Key ID** and **Secret Access Key** into your `.env` file

> ⚠️ **Security Note:** These are read-only permissions. CloudGRC-AI never modifies your environment.

---

### 🌐 GCP Setup

#### 1. Create a Service Account

```bash
# Using gcloud CLI
gcloud iam service-accounts create cloudgrc-scanner     --description="CloudGRC-AI read-only scanner"     --display-name="CloudGRC Scanner"
```

#### 2. Assign Read-Only Roles

```bash
PROJECT_ID="your-project-id"
SA_EMAIL="cloudgrc-scanner@${PROJECT_ID}.iam.gserviceaccount.com"

gcloud projects add-iam-policy-binding $PROJECT_ID     --member="serviceAccount:${SA_EMAIL}"     --role="roles/viewer"

gcloud projects add-iam-policy-binding $PROJECT_ID     --member="serviceAccount:${SA_EMAIL}"     --role="roles/iam.securityReviewer"
```

#### 3. Download Service Account Key

```bash
gcloud iam service-accounts keys create gcp-creds.json     --iam-account=$SA_EMAIL

# Move to project folder
mv gcp-creds.json /home/kali/CloudGRC-AI/gcp-creds.json
```

Update your `.env`:
```bash
GCP_PROJECT_ID=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=/home/kali/CloudGRC-AI/gcp-creds.json
```

---

### 🔵 Azure Setup

#### 1. Create a Service Principal

```bash
# Using Azure CLI
az login

az ad sp create-for-rbac     --name "cloudgrc-scanner"     --role "Reader"     --scopes /subscriptions/YOUR_SUBSCRIPTION_ID
```

This outputs:
```json
{
  "appId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "password": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "tenant": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
}
```

Copy these values into `.env`:
```bash
AZURE_SUBSCRIPTION_ID=YOUR_SUBSCRIPTION_ID
AZURE_TENANT_ID=tenant value above
AZURE_CLIENT_ID=appId value above
AZURE_CLIENT_SECRET=password value above
```

---

### 🤖 OpenAI Setup (Optional)

The AI report works without OpenAI — it falls back to a structured template.
To enable GPT-written narrative:

1. Go to **platform.openai.com → API Keys → Create new secret key**
2. Add to `.env`:
```bash
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

> GPT-4o-mini is used by default (low cost — typically under $0.01 per report).

---

## 🚀 Running a Real Scan

```bash
# Activate your virtual environment first
source venv/bin/activate

# Load credentials from .env
export $(grep -v '^#' .env | xargs)

# Scan AWS only
python main.py --providers aws --org "Your Company Name"

# Scan GCP only
python main.py --providers gcp --org "Your Company Name"

# Scan Azure only
python main.py --providers azure --org "Your Company Name"

# Scan all three clouds at once
python main.py --providers aws gcp azure --org "Your Company Name"
```

---

## 📄 Getting a PDF Report

### Option 1 — Automatic (CLI)

The PDF is generated automatically after every scan:

```bash
python main.py --providers aws --org "Your Company"
# PDF saved to: reports/cloudgrc_report_YYYYMMDD_HHMMSS.pdf
ls -la reports/
```

### Option 2 — Streamlit Dashboard

```bash
streamlit run app.py
```

1. Open **http://localhost:8501**
2. Enter your credentials in the sidebar (or upload `.env`)
3. Untick **"Use Mock Data"**
4. Select your cloud provider(s)
5. Click **▶ RUN SCAN**
6. Scroll to **Export Reports** section
7. Click **⬇ Download PDF**

### Fix PDF Not Generating

```bash
pip install reportlab
python -c "from reporting.pdf_generator import generate_pdf_report; print('PDF OK')"
```

---

## 📊 Streamlit Dashboard

```bash
source venv/bin/activate
streamlit run app.py
```

| Feature | Description |
|---|---|
| Multi-cloud selector | Choose AWS, GCP, Azure or all three |
| Mock mode | Demo with 14 realistic findings — no credentials needed |
| Findings table | Filter by severity, cloud, and category |
| Risk gauge | Visual risk score 0–100 |
| Severity pie chart | Breakdown by Critical / High / Medium / Low |
| AI report tabs | Executive Summary, Technical Findings, Business Impact, Remediation |
| Export buttons | Download PDF, JSON, CSV in one click |

---

## 🔎 Security Checks Covered

| Category | Check | Severity |
|---|---|---|
| **IAM** | Root account MFA disabled | Critical |
| **IAM** | Users without MFA | High |
| **IAM** | Wildcard `*` policies attached | High |
| **IAM** | Access keys not rotated in 90+ days | Medium |
| **Storage** | S3 / GCS bucket publicly accessible | Critical |
| **Storage** | Encryption at rest disabled | High |
| **Storage** | Access logging disabled | Medium |
| **Network** | Port 22 (SSH) open to 0.0.0.0/0 | Critical |
| **Network** | Port 3389 (RDP) open to 0.0.0.0/0 | Critical |
| **Network** | Port 3306 (MySQL) open to 0.0.0.0/0 | High |
| **Network** | VPC Flow Logs disabled | Medium |
| **Logging** | CloudTrail disabled | Critical |
| **Logging** | No multi-region CloudTrail | High |
| **Logging** | CloudWatch alarms not configured | Medium |

---

## 📋 Compliance Frameworks

| Framework | Controls Mapped |
|---|---|
| **ISO/IEC 27001:2022** | Annex A — A.5, A.8, A.9, A.10, A.12, A.13 |
| **NIST Cybersecurity Framework** | PR.AC, PR.DS, PR.IP, DE.CM, RS.AN |
| **CIS Benchmarks** | Controls 3, 5, 6, 8, 12, 13 |

---

## 🛠️ Troubleshooting

| Error | Fix |
|---|---|
| `externally-managed-environment` | Use `python3 -m venv venv && source venv/bin/activate` before pip install |
| `main.py not found` | Run from the `CloudGRC-AI` root directory, not a subfolder |
| `streamlit: command not found` | Run `pip install streamlit` inside the venv |
| `NoCredentialsError` | Run `export $(grep -v '^#' .env \| xargs)` to load your .env |
| `PDF not generating` | Run `pip install reportlab` |
| `ModuleNotFoundError` | Make sure venv is active: `source venv/bin/activate` |
| GCP `DefaultCredentialsError` | Set `GOOGLE_APPLICATION_CREDENTIALS` to the full absolute path of your JSON key |
| Azure `AuthenticationError` | Verify all four Azure variables are set in `.env` |

---

## 👤 Built By

**Tanmoy Daw** — Cybersecurity GRC Consultant & Information Security Auditor

CERT-In Empanelled | ISO 27001:2022 Lead Auditor | CEH v13 Master | CPENT v2 | DPDPA Act 2023

[![LinkedIn](https://img.shields.io/badge/LinkedIn-tanmoy--daw-0077B5?logo=linkedin)](https://linkedin.com/in/tanmoy-daw-a27a162aa)
[![GitHub](https://img.shields.io/badge/GitHub-tanmoydaw26-181717?logo=github)](https://github.com/tanmoydaw26)
[![TryHackMe](https://img.shields.io/badge/TryHackMe-Top%202%25-red?logo=tryhackme)](https://tryhackme.com/p/BORDA26)
[![Portfolio](https://img.shields.io/badge/Portfolio-tanmoydaw26.github.io-00ffe7)](https://tanmoydaw26.github.io/portfolio)

---

## 📜 License

MIT License — free to use, modify, and distribute with attribution.

---

> ⚠️ **Disclaimer:** CloudGRC-AI performs read-only operations only. It never modifies, deletes,
> or writes to your cloud environment. Always follow your organisation's change management
> and security policies before running any security tool against production environments.
