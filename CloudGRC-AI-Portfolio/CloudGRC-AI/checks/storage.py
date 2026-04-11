"""
Storage Security Checks — AWS S3, GCP GCS, Azure Blob
Detects: public access, encryption disabled, versioning off.
"""
from typing import List, Dict


def check_aws_s3(session) -> List[Dict]:
    findings = []
    s3 = session.client("s3")
    try:
        buckets = s3.list_buckets().get("Buckets", [])
        for bucket in buckets:
            name = bucket["Name"]

            # Public access block
            try:
                pub = s3.get_public_access_block(Bucket=name)["PublicAccessBlockConfiguration"]
                if not all([
                    pub.get("BlockPublicAcls"), pub.get("IgnorePublicAcls"),
                    pub.get("BlockPublicPolicy"), pub.get("RestrictPublicBuckets")
                ]):
                    findings.append({
                        "cloud": "AWS", "category": "Storage",
                        "issue": f"S3 bucket '{name}' has public access not fully blocked",
                        "resource": f"s3:{name}",
                        "severity": "High",
                        "detail": "Publicly accessible buckets can expose sensitive data to the internet.",
                    })
            except s3.exceptions.NoSuchPublicAccessBlockConfiguration:
                findings.append({
                    "cloud": "AWS", "category": "Storage",
                    "issue": f"S3 bucket '{name}' has no public access block configured",
                    "resource": f"s3:{name}",
                    "severity": "Critical",
                    "detail": "No public access block means the bucket may be fully public.",
                })
            except Exception:
                pass

            # Encryption
            try:
                s3.get_bucket_encryption(Bucket=name)
            except Exception:
                findings.append({
                    "cloud": "AWS", "category": "Storage",
                    "issue": f"S3 bucket '{name}' does not have server-side encryption enabled",
                    "resource": f"s3:{name}",
                    "severity": "High",
                    "detail": "Unencrypted buckets risk data exposure if access controls fail.",
                })

            # Versioning
            try:
                ver = s3.get_bucket_versioning(Bucket=name)
                if ver.get("Status") != "Enabled":
                    findings.append({
                        "cloud": "AWS", "category": "Storage",
                        "issue": f"S3 bucket '{name}' does not have versioning enabled",
                        "resource": f"s3:{name}",
                        "severity": "Low",
                        "detail": "Versioning protects against accidental deletion and ransomware.",
                    })
            except Exception:
                pass
    except Exception as e:
        findings.append({"cloud": "AWS", "category": "Storage", "issue": f"S3 check error: {e}",
                         "resource": "s3", "severity": "Info", "detail": str(e)})
    return findings


def check_gcp_gcs(gcs_client, project_id: str) -> List[Dict]:
    findings = []
    try:
        buckets = gcs_client.list_buckets()
        for bucket in buckets:
            name = bucket.name
            # Public IAM
            try:
                policy = bucket.get_iam_policy()
                for binding in policy.bindings:
                    if "allUsers" in binding["members"] or "allAuthenticatedUsers" in binding["members"]:
                        findings.append({
                            "cloud": "GCP", "category": "Storage",
                            "issue": f"GCS bucket '{name}' is publicly accessible",
                            "resource": f"gcs:{name}",
                            "severity": "Critical",
                            "detail": "Public GCS buckets expose data to the entire internet.",
                        })
            except Exception:
                pass
            # Encryption — uniform bucket-level access
            if not bucket.uniform_bucket_level_access_enabled:
                findings.append({
                    "cloud": "GCP", "category": "Storage",
                    "issue": f"GCS bucket '{name}' does not have uniform bucket-level access",
                    "resource": f"gcs:{name}",
                    "severity": "Medium",
                    "detail": "Object-level ACLs can create inconsistent access control.",
                })
    except Exception as e:
        findings.append({"cloud": "GCP", "category": "Storage", "issue": f"GCS check error: {e}",
                         "resource": "gcs", "severity": "Info", "detail": str(e)})
    return findings


def check_azure_blob(storage_client) -> List[Dict]:
    findings = []
    try:
        accounts = list(storage_client.storage_accounts.list())
        for acct in accounts:
            name = acct.name
            rg = acct.id.split("/")[4]
            # Public blob access
            if acct.allow_blob_public_access:
                findings.append({
                    "cloud": "Azure", "category": "Storage",
                    "issue": f"Azure Storage account '{name}' allows public blob access",
                    "resource": f"azure:storage:{name}",
                    "severity": "High",
                    "detail": "Public blob access can expose storage containers to the internet.",
                })
            # Encryption — should always be on, check key type
            if acct.encryption and acct.encryption.key_source == "Microsoft.Storage":
                findings.append({
                    "cloud": "Azure", "category": "Storage",
                    "issue": f"Storage account '{name}' uses Microsoft-managed keys (not customer-managed)",
                    "resource": f"azure:storage:{name}",
                    "severity": "Low",
                    "detail": "For sensitive data, consider customer-managed keys (CMK) in Azure Key Vault.",
                })
            # HTTPS only
            if not acct.enable_https_traffic_only:
                findings.append({
                    "cloud": "Azure", "category": "Storage",
                    "issue": f"Storage account '{name}' allows HTTP traffic",
                    "resource": f"azure:storage:{name}",
                    "severity": "High",
                    "detail": "HTTP traffic can be intercepted. Enforce HTTPS-only transfers.",
                })
    except Exception as e:
        findings.append({"cloud": "Azure", "category": "Storage", "issue": f"Blob check error: {e}",
                         "resource": "azure:storage", "severity": "Info", "detail": str(e)})
    return findings
