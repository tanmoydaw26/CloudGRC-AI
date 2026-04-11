"""
IAM Security Checks — AWS, GCP, Azure
Detects: overly permissive roles, MFA disabled, root usage, wildcard policies.
"""
from datetime import datetime, timezone
from typing import List, Dict


# ─────────────────────────── AWS IAM ───────────────────────────

def check_aws_iam(session) -> List[Dict]:
    findings = []
    iam = session.client("iam")

    # 1. Root account last used
    try:
        summary = iam.get_account_summary()["SummaryMap"]
        if summary.get("AccountMFAEnabled", 0) == 0:
            findings.append({
                "cloud": "AWS", "category": "IAM",
                "issue": "Root account does not have MFA enabled",
                "resource": "root-account",
                "severity": "Critical",
                "detail": "The AWS root account has no MFA device. Immediate action required.",
            })
    except Exception as e:
        findings.append({"cloud": "AWS", "category": "IAM", "issue": f"Root check error: {e}",
                         "resource": "root-account", "severity": "Info", "detail": str(e)})

    # 2. IAM users without MFA
    try:
        paginator = iam.get_paginator("list_users")
        for page in paginator.paginate():
            for user in page["Users"]:
                uname = user["UserName"]
                mfa = iam.list_mfa_devices(UserName=uname)["MFADevices"]
                if not mfa:
                    findings.append({
                        "cloud": "AWS", "category": "IAM",
                        "issue": f"IAM user '{uname}' has no MFA enabled",
                        "resource": f"iam:user:{uname}",
                        "severity": "High",
                        "detail": "Users without MFA are vulnerable to credential theft attacks.",
                    })
    except Exception as e:
        findings.append({"cloud": "AWS", "category": "IAM", "issue": f"MFA check error: {e}",
                         "resource": "iam:users", "severity": "Info", "detail": str(e)})

    # 3. Policies with wildcard (*) actions
    try:
        paginator = iam.get_paginator("list_policies")
        for page in paginator.paginate(Scope="Local"):
            for policy in page["Policies"]:
                pv = iam.get_policy_version(
                    PolicyArn=policy["Arn"],
                    VersionId=policy["DefaultVersionId"]
                )["PolicyVersion"]["Document"]
                stmts = pv.get("Statement", [])
                if isinstance(stmts, dict):
                    stmts = [stmts]
                for stmt in stmts:
                    action = stmt.get("Action", "")
                    effect = stmt.get("Effect", "")
                    if effect == "Allow" and ("*" in action or action == "*"):
                        findings.append({
                            "cloud": "AWS", "category": "IAM",
                            "issue": f"Policy '{policy['PolicyName']}' allows wildcard (*) actions",
                            "resource": policy["Arn"],
                            "severity": "High",
                            "detail": "Wildcard Allow policies violate least-privilege principles.",
                        })
    except Exception as e:
        findings.append({"cloud": "AWS", "category": "IAM", "issue": f"Policy wildcard check error: {e}",
                         "resource": "iam:policies", "severity": "Info", "detail": str(e)})

    # 4. Access keys older than 90 days
    try:
        paginator = iam.get_paginator("list_users")
        for page in paginator.paginate():
            for user in page["Users"]:
                uname = user["UserName"]
                keys = iam.list_access_keys(UserName=uname)["AccessKeyMetadata"]
                for key in keys:
                    if key["Status"] == "Active":
                        age = (datetime.now(timezone.utc) - key["CreateDate"]).days
                        if age > 90:
                            findings.append({
                                "cloud": "AWS", "category": "IAM",
                                "issue": f"Access key for '{uname}' is {age} days old (>90 days)",
                                "resource": f"iam:user:{uname}:key:{key['AccessKeyId']}",
                                "severity": "Medium",
                                "detail": "Stale access keys increase the risk of undetected credential compromise.",
                            })
    except Exception as e:
        findings.append({"cloud": "AWS", "category": "IAM", "issue": f"Key age check error: {e}",
                         "resource": "iam:keys", "severity": "Info", "detail": str(e)})

    return findings


# ─────────────────────────── GCP IAM ───────────────────────────

def check_gcp_iam(credentials, project_id: str) -> List[Dict]:
    findings = []
    try:
        from googleapiclient import discovery
        crm = discovery.build("cloudresourcemanager", "v1", credentials=credentials)
        policy = crm.projects().getIamPolicy(resource=project_id, body={}).execute()
        bindings = policy.get("bindings", [])
        for binding in bindings:
            role = binding.get("role", "")
            members = binding.get("members", [])
            # Overly permissive roles
            if role in ("roles/owner", "roles/editor"):
                for member in members:
                    if "allUsers" in member or "allAuthenticatedUsers" in member:
                        findings.append({
                            "cloud": "GCP", "category": "IAM",
                            "issue": f"Role '{role}' granted to '{member}' (public access)",
                            "resource": f"project:{project_id}",
                            "severity": "Critical",
                            "detail": "Public IAM bindings expose your project to any internet user.",
                        })
                    else:
                        findings.append({
                            "cloud": "GCP", "category": "IAM",
                            "issue": f"Overly permissive role '{role}' assigned to '{member}'",
                            "resource": f"project:{project_id}",
                            "severity": "High",
                            "detail": "Owner/Editor roles grant near-full access. Use granular roles.",
                        })
    except Exception as e:
        findings.append({"cloud": "GCP", "category": "IAM", "issue": f"IAM check error: {e}",
                         "resource": f"project:{project_id}", "severity": "Info", "detail": str(e)})
    return findings


# ─────────────────────────── AZURE IAM ───────────────────────────

def check_azure_iam(credential, subscription_id: str) -> List[Dict]:
    findings = []
    try:
        from azure.mgmt.authorization import AuthorizationManagementClient
        auth_client = AuthorizationManagementClient(credential, subscription_id)
        scope = f"/subscriptions/{subscription_id}"
        assignments = auth_client.role_assignments.list_for_scope(scope)
        owner_role_id = "8e3af657-a8ff-443c-a75c-2fe8c4bcb635"
        for assignment in assignments:
            role_def_id = assignment.role_definition_id.split("/")[-1]
            if role_def_id == owner_role_id:
                findings.append({
                    "cloud": "Azure", "category": "IAM",
                    "issue": f"Owner role assigned to principal '{assignment.principal_id}'",
                    "resource": f"subscription:{subscription_id}",
                    "severity": "High",
                    "detail": "Owner role at subscription scope grants full control. Review necessity.",
                })
    except Exception as e:
        findings.append({"cloud": "Azure", "category": "IAM", "issue": f"IAM check error: {e}",
                         "resource": f"subscription:{subscription_id}", "severity": "Info", "detail": str(e)})
    return findings
