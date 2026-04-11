"""
AI Report Generator — uses OpenAI GPT to summarise findings,
explain business impact, and generate remediation guidance.
"""
import os
import json
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()


def generate_ai_report(findings: List[Dict], risk_data: Dict) -> Dict[str, str]:
    """
    Calls OpenAI API to produce:
      - Executive Summary
      - Technical Findings Narrative
      - Business Impact Analysis
      - Remediation Plan
    Falls back to a structured template if API key is not set.
    """
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        return _template_report(findings, risk_data)

    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)

        findings_summary = json.dumps([
            {
                "issue": f.get("issue"),
                "severity": f.get("severity"),
                "cloud": f.get("cloud"),
                "category": f.get("category"),
            }
            for f in findings[:30]  # Limit to 30 for token management
        ], indent=2)

        prompt = f"""
You are a senior cybersecurity GRC consultant writing a formal audit report.

Cloud Security Scan Results:
- Total Findings: {risk_data["total_findings"]}
- Risk Score: {risk_data["risk_score"]}/100
- Compliance Score: {risk_data["compliance_pct"]}%
- Severity Breakdown: {json.dumps(risk_data["breakdown"])}

Top Findings:
{findings_summary}

Generate a professional audit report with exactly these four sections:

1. EXECUTIVE SUMMARY (3-4 sentences, non-technical, for board/CISO audience)
2. TECHNICAL FINDINGS (concise bullet-point narrative of key issues found)
3. BUSINESS IMPACT (explain real-world risk in business terms)
4. REMEDIATION PLAN (prioritised, actionable steps with timeframes)

Use formal, clear language. Be specific. Reference ISO 27001, NIST, and CIS where relevant.
"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert cybersecurity GRC auditor."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=2000,
        )

        full_text = response.choices[0].message.content
        return _parse_ai_sections(full_text)

    except Exception as e:
        print(f"[AI] OpenAI call failed: {e}. Falling back to template report.")
        return _template_report(findings, risk_data)


def _parse_ai_sections(text: str) -> Dict[str, str]:
    """Parse AI output into named sections."""
    sections = {
        "executive_summary": "",
        "technical_findings": "",
        "business_impact": "",
        "remediation_plan": "",
    }
    markers = {
        "EXECUTIVE SUMMARY": "executive_summary",
        "TECHNICAL FINDINGS": "technical_findings",
        "BUSINESS IMPACT": "business_impact",
        "REMEDIATION PLAN": "remediation_plan",
    }
    current = None
    for line in text.splitlines():
        for marker, key in markers.items():
            if marker in line.upper():
                current = key
                break
        else:
            if current:
                sections[current] += line + "\n"
    return {k: v.strip() for k, v in sections.items()}


def _template_report(findings: List[Dict], risk_data: Dict) -> Dict[str, str]:
    """Fallback structured report when no OpenAI key is available."""
    breakdown = risk_data.get("breakdown", {})
    critical = breakdown.get("Critical", 0)
    high = breakdown.get("High", 0)

    exec_summary = (
        f"The automated cloud security scan identified {risk_data['total_findings']} findings "
        f"across the assessed environments, yielding an overall risk score of {risk_data['risk_score']}/100 "
        f"and a compliance posture of {risk_data['compliance_pct']}%. "
        f"Of these, {critical} findings were rated Critical and {high} were rated High, "
        f"requiring immediate remediation to reduce organisational exposure."
    )

    categories = {}
    for f in findings:
        cat = f.get("category", "Other")
        categories.setdefault(cat, []).append(f)

    tech = ""
    for cat, items in categories.items():
        tech += f"\n{cat} ({len(items)} findings):\n"
        for item in items[:5]:
            tech += f"  - [{item['severity']}] {item['issue']}\n"

    impact = (
        "Critical and High severity findings represent direct attack vectors that could lead to "
        "unauthorised data access, regulatory non-compliance (RBI ITIS, ISO 27001, DPDP Act), "
        "financial penalties, and reputational damage. Public storage exposure and open network "
        "ports are particularly high-risk in regulated environments."
    )

    remediation = (
        "Immediate (0-7 days): Remediate all Critical findings — enable MFA on root/admin accounts, "
        "remove public bucket access, close unrestricted inbound ports (22, 3389).\n"
        "Short-term (7-30 days): Address all High findings — enforce encryption, enable CloudTrail/logging, "
        "review IAM wildcard policies.\n"
        "Medium-term (30-90 days): Resolve Medium findings — rotate stale access keys, enable versioning, "
        "configure log retention policies.\n"
        "Ongoing: Integrate CloudGRC-AI into CI/CD pipelines for continuous compliance monitoring."
    )

    return {
        "executive_summary": exec_summary,
        "technical_findings": tech.strip(),
        "business_impact": impact,
        "remediation_plan": remediation,
    }
