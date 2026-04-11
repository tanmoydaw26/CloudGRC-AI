"""
Network Security Checks — AWS, GCP, Azure
Detects: open 0.0.0.0/0 ports, unrestricted firewall rules, missing flow logs.
"""
from typing import List, Dict

CRITICAL_PORTS = {22: "SSH", 3389: "RDP", 3306: "MySQL", 5432: "PostgreSQL",
                  6379: "Redis", 27017: "MongoDB", 443: "HTTPS", 80: "HTTP"}


def check_aws_network(session) -> List[Dict]:
    findings = []
    ec2 = session.client("ec2")
    try:
        sgs = ec2.describe_security_groups()["SecurityGroups"]
        for sg in sgs:
            sg_id = sg["GroupId"]
            sg_name = sg.get("GroupName", sg_id)
            for perm in sg.get("IpPermissions", []):
                from_port = perm.get("FromPort", 0)
                to_port = perm.get("ToPort", 65535)
                for ip_range in perm.get("IpRanges", []):
                    if ip_range.get("CidrIp") == "0.0.0.0/0":
                        port_label = CRITICAL_PORTS.get(from_port, str(from_port))
                        sev = "Critical" if from_port in (22, 3389) else "High"
                        findings.append({
                            "cloud": "AWS", "category": "Network",
                            "issue": f"SG '{sg_name}' allows inbound {port_label} (port {from_port}) from 0.0.0.0/0",
                            "resource": f"ec2:sg:{sg_id}",
                            "severity": sev,
                            "detail": f"Port {from_port} open to the entire internet is a primary attack vector.",
                        })
                for ipv6_range in perm.get("Ipv6Ranges", []):
                    if ipv6_range.get("CidrIpv6") == "::/0":
                        findings.append({
                            "cloud": "AWS", "category": "Network",
                            "issue": f"SG '{sg_name}' allows inbound from ::/0 (all IPv6)",
                            "resource": f"ec2:sg:{sg_id}",
                            "severity": "High",
                            "detail": "Unrestricted IPv6 inbound access detected.",
                        })
    except Exception as e:
        findings.append({"cloud": "AWS", "category": "Network", "issue": f"SG check error: {e}",
                         "resource": "ec2:sg", "severity": "Info", "detail": str(e)})

    # VPC Flow Logs
    try:
        vpcs = ec2.describe_vpcs()["Vpcs"]
        flow_logs = ec2.describe_flow_logs()["FlowLogs"]
        logged_vpcs = {fl["ResourceId"] for fl in flow_logs}
        for vpc in vpcs:
            if vpc["VpcId"] not in logged_vpcs:
                findings.append({
                    "cloud": "AWS", "category": "Network",
                    "issue": f"VPC '{vpc['VpcId']}' does not have Flow Logs enabled",
                    "resource": f"ec2:vpc:{vpc['VpcId']}",
                    "severity": "Medium",
                    "detail": "VPC Flow Logs are essential for network traffic visibility and incident response.",
                })
    except Exception as e:
        findings.append({"cloud": "AWS", "category": "Network", "issue": f"Flow log check error: {e}",
                         "resource": "ec2:vpc", "severity": "Info", "detail": str(e)})
    return findings


def check_gcp_firewall(credentials, project_id: str) -> List[Dict]:
    findings = []
    try:
        from googleapiclient import discovery
        compute = discovery.build("compute", "v1", credentials=credentials)
        rules = compute.firewalls().list(project=project_id).execute().get("items", [])
        for rule in rules:
            if rule.get("direction") == "INGRESS" and not rule.get("disabled", False):
                src_ranges = rule.get("sourceRanges", [])
                if "0.0.0.0/0" in src_ranges:
                    for allowed in rule.get("allowed", []):
                        ports = allowed.get("ports", ["all"])
                        findings.append({
                            "cloud": "GCP", "category": "Network",
                            "issue": f"Firewall rule '{rule['name']}' allows inbound from 0.0.0.0/0 on ports {ports}",
                            "resource": f"gcp:firewall:{rule['name']}",
                            "severity": "High",
                            "detail": "Open firewall rules expose GCP resources to internet-wide attack traffic.",
                        })
    except Exception as e:
        findings.append({"cloud": "GCP", "category": "Network", "issue": f"Firewall check error: {e}",
                         "resource": "gcp:firewall", "severity": "Info", "detail": str(e)})
    return findings


def check_azure_nsg(network_client) -> List[Dict]:
    findings = []
    try:
        nsgs = list(network_client.network_security_groups.list_all())
        for nsg in nsgs:
            for rule in (nsg.security_rules or []):
                if (rule.access == "Allow" and rule.direction == "Inbound" and
                        rule.source_address_prefix in ("*", "0.0.0.0/0", "Internet", "Any")):
                    dest_port = rule.destination_port_range or "*"
                    sev = "Critical" if dest_port in ("22", "3389") else "High"
                    findings.append({
                        "cloud": "Azure", "category": "Network",
                        "issue": f"NSG '{nsg.name}' rule '{rule.name}' allows inbound from Any on port {dest_port}",
                        "resource": f"azure:nsg:{nsg.name}",
                        "severity": sev,
                        "detail": "Unrestricted inbound NSG rules expose Azure resources to the internet.",
                    })
    except Exception as e:
        findings.append({"cloud": "Azure", "category": "Network", "issue": f"NSG check error: {e}",
                         "resource": "azure:nsg", "severity": "Info", "detail": str(e)})
    return findings
