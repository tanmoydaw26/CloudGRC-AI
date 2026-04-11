"""
Compliance Mapping Engine
Maps each finding to ISO 27001:2022, NIST CSF, and CIS Benchmark references.
"""
from typing import Dict

# ─── Framework mappings by category + severity ───
COMPLIANCE_MAP = {
    "IAM": {
        "ISO27001": "A.9.2 — User Access Management; A.9.4 — System and Application Access Control",
        "NIST_CSF": "PR.AC-1: Identities and credentials are managed; PR.AC-4: Access permissions managed",
        "CIS": "CIS Control 5: Account Management; CIS Control 6: Access Control Management",
    },
    "Storage": {
        "ISO27001": "A.8.2 — Information Classification; A.10.1 — Cryptographic Controls; A.13.1 — Network Security",
        "NIST_CSF": "PR.DS-1: Data-at-rest is protected; PR.DS-2: Data-in-transit is protected",
        "CIS": "CIS Control 3: Data Protection; CIS Control 13: Network Monitoring and Defence",
    },
    "Network": {
        "ISO27001": "A.13.1 — Network Security Management; A.13.2 — Information Transfer",
        "NIST_CSF": "PR.AC-5: Network integrity is protected; DE.CM-1: Network is monitored",
        "CIS": "CIS Control 12: Network Infrastructure Management; CIS Control 13: Network Monitoring",
    },
    "Logging": {
        "ISO27001": "A.12.4 — Logging and Monitoring; A.16.1 — Management of Information Security Incidents",
        "NIST_CSF": "DE.AE-3: Event data are aggregated; RS.AN-1: Notifications from detection systems investigated",
        "CIS": "CIS Control 8: Audit Log Management",
    },
}

SEVERITY_SCORE = {"Critical": 10, "High": 7, "Medium": 4, "Low": 1, "Info": 0}

def map_finding(finding: dict) -> dict:
    """Enrich a finding with compliance framework references and score."""
    category = finding.get("category", "IAM")
    severity = finding.get("severity", "Medium")
    fw = COMPLIANCE_MAP.get(category, COMPLIANCE_MAP["IAM"])
    finding["frameworks"] = {
        "ISO27001": fw["ISO27001"],
        "NIST_CSF": fw["NIST_CSF"],
        "CIS":      fw["CIS"],
    }
    finding["score"] = SEVERITY_SCORE.get(severity, 0)
    return finding

def map_all_findings(findings: list) -> list:
    """Apply compliance mapping to all findings."""
    return [map_finding(f) for f in findings]

def calculate_risk_score(findings: list) -> dict:
    """
    Calculate overall risk score (0-100) and compliance percentage.
    Higher score = higher risk.
    """
    if not findings:
        return {"risk_score": 0, "compliance_pct": 100, "breakdown": {}}

    severity_counts = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0, "Info": 0}
    total_score = 0

    for f in findings:
        sev = f.get("severity", "Info")
        severity_counts[sev] = severity_counts.get(sev, 0) + 1
        total_score += SEVERITY_SCORE.get(sev, 0)

    # Max possible score normalised to 100
    max_score = len(findings) * 10
    raw_risk = (total_score / max_score * 100) if max_score > 0 else 0
    risk_score = min(round(raw_risk, 1), 100)

    # Compliance % = inverse of critical+high density
    critical_high = severity_counts["Critical"] + severity_counts["High"]
    compliance_pct = max(0, round(100 - (critical_high / len(findings) * 100), 1))

    return {
        "risk_score": risk_score,
        "compliance_pct": compliance_pct,
        "total_findings": len(findings),
        "breakdown": severity_counts,
    }
