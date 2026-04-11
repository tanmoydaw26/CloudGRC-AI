"""
Logging & Monitoring Checks — AWS, GCP, Azure
Detects: CloudTrail disabled, log retention issues, monitoring alerts missing.
"""
from typing import List, Dict


def check_aws_logging(session) -> List[Dict]:
    findings = []

    # CloudTrail
    try:
        ct = session.client("cloudtrail")
        trails = ct.describe_trails()["trailList"]
        if not trails:
            findings.append({
                "cloud": "AWS", "category": "Logging",
                "issue": "No CloudTrail trails configured in this account",
                "resource": "cloudtrail",
                "severity": "Critical",
                "detail": "CloudTrail is essential for audit logging of all API activity in AWS.",
            })
        else:
            for trail in trails:
                status = ct.get_trail_status(Name=trail["TrailARN"])
                if not status.get("IsLogging"):
                    findings.append({
                        "cloud": "AWS", "category": "Logging",
                        "issue": f"CloudTrail '{trail['Name']}' is not actively logging",
                        "resource": f"cloudtrail:{trail['Name']}",
                        "severity": "Critical",
                        "detail": "An inactive trail provides no audit record of API activity.",
                    })
                if not trail.get("LogFileValidationEnabled"):
                    findings.append({
                        "cloud": "AWS", "category": "Logging",
                        "issue": f"CloudTrail '{trail['Name']}' does not have log file validation enabled",
                        "resource": f"cloudtrail:{trail['Name']}",
                        "severity": "Medium",
                        "detail": "Log validation detects tampering with CloudTrail log files.",
                    })
    except Exception as e:
        findings.append({"cloud": "AWS", "category": "Logging", "issue": f"CloudTrail check error: {e}",
                         "resource": "cloudtrail", "severity": "Info", "detail": str(e)})

    # Config service
    try:
        config = session.client("config")
        recorders = config.describe_configuration_recorders()["ConfigurationRecorders"]
        if not recorders:
            findings.append({
                "cloud": "AWS", "category": "Logging",
                "issue": "AWS Config recorder is not configured",
                "resource": "config",
                "severity": "Medium",
                "detail": "AWS Config tracks resource configuration changes for compliance.",
            })
    except Exception as e:
        findings.append({"cloud": "AWS", "category": "Logging", "issue": f"Config check error: {e}",
                         "resource": "config", "severity": "Info", "detail": str(e)})
    return findings


def check_gcp_logging(logging_client, project_id: str) -> List[Dict]:
    findings = []
    try:
        sinks = list(logging_client.list_sinks())
        if not sinks:
            findings.append({
                "cloud": "GCP", "category": "Logging",
                "issue": f"No log sinks configured for project '{project_id}'",
                "resource": f"project:{project_id}",
                "severity": "High",
                "detail": "Log sinks route audit logs to storage for long-term retention and analysis.",
            })
    except Exception as e:
        findings.append({"cloud": "GCP", "category": "Logging", "issue": f"Logging check error: {e}",
                         "resource": f"project:{project_id}", "severity": "Info", "detail": str(e)})
    return findings


def check_azure_logging(monitor_client, subscription_id: str) -> List[Dict]:
    findings = []
    try:
        profiles = list(monitor_client.log_profiles.list())
        if not profiles:
            findings.append({
                "cloud": "Azure", "category": "Logging",
                "issue": "No Activity Log profiles configured for this subscription",
                "resource": f"subscription:{subscription_id}",
                "severity": "High",
                "detail": "Activity Log profiles export audit events for long-term monitoring.",
            })
        for profile in profiles:
            if profile.retention_policy and profile.retention_policy.days < 90:
                findings.append({
                    "cloud": "Azure", "category": "Logging",
                    "issue": f"Log profile '{profile.name}' retains logs for only {profile.retention_policy.days} days (<90)",
                    "resource": f"azure:logprofile:{profile.name}",
                    "severity": "Medium",
                    "detail": "Short log retention limits forensic investigation capability.",
                })
    except Exception as e:
        findings.append({"cloud": "Azure", "category": "Logging", "issue": f"Logging check error: {e}",
                         "resource": f"subscription:{subscription_id}", "severity": "Info", "detail": str(e)})
    return findings
