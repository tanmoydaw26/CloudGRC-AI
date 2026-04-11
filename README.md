# 🛡️ CloudGRC-AI — Automated Cloud Compliance & Risk Scanner

> A production-grade cloud security tool that scans AWS, GCP, and Azure 
> for misconfigurations and maps findings to ISO 27001, NIST CSF, and CIS Benchmarks.

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![AWS](https://img.shields.io/badge/AWS-boto3-orange?logo=amazonaws)
![GCP](https://img.shields.io/badge/GCP-google--cloud-blue?logo=googlecloud)
![Azure](https://img.shields.io/badge/Azure-azure--mgmt-blue?logo=microsoftazure)
![Streamlit](https://img.shields.io/badge/UI-Streamlit-red?logo=streamlit)
![License](https://img.shields.io/badge/License-MIT-green)

---

## What It Does

- Scans cloud environments for IAM, Storage, Network, and Logging misconfigurations
- Maps every finding to ISO 27001:2022, NIST CSF, and CIS Benchmark controls
- Calculates a risk score (0–100) and compliance percentage
- Generates AI-written audit reports using OpenAI GPT
- Exports PDF, JSON, and CSV audit reports
- Includes a full Streamlit dashboard UI

---

## Quick Start

```bash
git clone https://github.com/tanmoydaw26/CloudGRC-AI
cd CloudGRC-AI
pip install -r requirements.txt
cp .env.example .env

# Run demo (no credentials needed)
python main.py --mock --org "Your Organisation"

# Launch dashboard
streamlit run app.py
```

---

## Architecture
