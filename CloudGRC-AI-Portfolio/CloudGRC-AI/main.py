"""
CloudGRC-AI — Main Orchestrator
Runs all security checks across selected cloud providers,
maps findings to compliance frameworks, scores risk,
generates AI narrative, and exports PDF + JSON reports.

Usage:
    python main.py --providers aws gcp azure --output ./reports
    python main.py --providers aws --mock       # Run with mock/demo data
"""
import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table as RichTable
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import box

load_dotenv()
console = Console()

SEVERITY_ORDER = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3, "Info": 4}


def run_aws_checks() -> list:
    from connectors.aws import get_aws_session
    from checks.iam import check_aws_iam
    from checks.storage import check_aws_s3
    from checks.network import check_aws_network
    from checks.logging import check_aws_logging

    findings = []
    try:
        session = get_aws_session()
        findings += check_aws_iam(session)
        findings += check_aws_s3(session)
        findings += check_aws_network(session)
        findings += check_aws_logging(session)
    except Exception as e:
        console.print(f"[red][AWS] Scan error: {e}[/red]")
    return findings


def run_gcp_checks() -> list:
    from connectors.gcp import get_gcp_credentials, get_gcs_client, get_logging_client
    from checks.iam import check_gcp_iam
    from checks.storage import check_gcp_gcs
    from checks.network import check_gcp_firewall
    from checks.logging import check_gcp_logging

    findings = []
    try:
        creds, project_id = get_gcp_credentials()
        findings += check_gcp_iam(creds, project_id)
        findings += check_gcp_gcs(get_gcs_client(), project_id)
        findings += check_gcp_firewall(creds, project_id)
        findings += check_gcp_logging(get_logging_client(), project_id)
    except Exception as e:
        console.print(f"[red][GCP] Scan error: {e}[/red]")
    return findings


def run_azure_checks() -> list:
    from connectors.azure import get_azure_credential, get_subscription_id
    from connectors.azure import get_storage_client, get_network_client, get_monitor_client
    from checks.iam import check_azure_iam
    from checks.storage import check_azure_blob
    from checks.network import check_azure_nsg
    from checks.logging import check_azure_logging

    findings = []
    try:
        cred = get_azure_credential()
        sub_id = get_subscription_id()
        findings += check_azure_iam(cred, sub_id)
        findings += check_azure_blob(get_storage_client())
        findings += check_azure_nsg(get_network_client())
        findings += check_azure_logging(get_monitor_client(), sub_id)
    except Exception as e:
        console.print(f"[red][Azure] Scan error: {e}[/red]")
    return findings


def load_mock_findings() -> list:
    """Return sample findings for demo/testing without real cloud credentials."""
    return [
        {"cloud": "AWS", "category": "IAM", "issue": "Root account does not have MFA enabled",
         "resource": "root-account", "severity": "Critical",
         "detail": "AWS root account MFA is not enabled."},
        {"cloud": "AWS", "category": "IAM", "issue": "IAM user 'admin' has no MFA enabled",
         "resource": "iam:user:admin", "severity": "High",
         "detail": "MFA missing for admin user."},
        {"cloud": "AWS", "category": "Storage", "issue": "S3 bucket 'prod-backups' has no public access block",
         "resource": "s3:prod-backups", "severity": "Critical",
         "detail": "Bucket may be fully public."},
        {"cloud": "AWS", "category": "Storage", "issue": "S3 bucket 'logs-archive' encryption not enabled",
         "resource": "s3:logs-archive", "severity": "High",
         "detail": "Server-side encryption not configured."},
        {"cloud": "AWS", "category": "Network", "issue": "SG 'web-sg' allows inbound SSH (port 22) from 0.0.0.0/0",
         "resource": "ec2:sg:sg-001", "severity": "Critical",
         "detail": "SSH exposed to internet."},
        {"cloud": "AWS", "category": "Network", "issue": "VPC 'vpc-main' does not have Flow Logs enabled",
         "resource": "ec2:vpc:vpc-001", "severity": "Medium",
         "detail": "No network traffic visibility."},
        {"cloud": "AWS", "category": "Logging", "issue": "CloudTrail 'main-trail' is not actively logging",
         "resource": "cloudtrail:main-trail", "severity": "Critical",
         "detail": "No audit log of API activity."},
        {"cloud": "GCP", "category": "IAM", "issue": "Overly permissive role 'roles/owner' assigned to service account",
         "resource": "project:demo-project", "severity": "High",
         "detail": "Owner role grants near-full access."},
        {"cloud": "GCP", "category": "Storage", "issue": "GCS bucket 'public-assets' is publicly accessible",
         "resource": "gcs:public-assets", "severity": "Critical",
         "detail": "Bucket exposed to internet."},
        {"cloud": "GCP", "category": "Network", "issue": "Firewall rule 'allow-all-ingress' allows inbound from 0.0.0.0/0",
         "resource": "gcp:firewall:allow-all-ingress", "severity": "High",
         "detail": "All ports open to internet."},
        {"cloud": "Azure", "category": "IAM", "issue": "Owner role assigned to principal 'abc-123'",
         "resource": "subscription:sub-001", "severity": "High",
         "detail": "Owner scope at subscription level."},
        {"cloud": "Azure", "category": "Storage", "issue": "Storage account 'prodstore' allows public blob access",
         "resource": "azure:storage:prodstore", "severity": "High",
         "detail": "Blob containers may be public."},
        {"cloud": "Azure", "category": "Network", "issue": "NSG 'web-nsg' rule allows inbound from Any on port 3389",
         "resource": "azure:nsg:web-nsg", "severity": "Critical",
         "detail": "RDP exposed to internet."},
        {"cloud": "Azure", "category": "Logging", "issue": "Log profile retains logs for only 30 days",
         "resource": "azure:logprofile:default", "severity": "Medium",
         "detail": "Short retention limits forensic capability."},
    ]


def print_findings_table(findings: list):
    table = RichTable(title="CloudGRC-AI Scan Results", box=box.ROUNDED,
                      show_header=True, header_style="bold cyan")
    table.add_column("#",        style="dim", width=4)
    table.add_column("Cloud",    width=7)
    table.add_column("Category", width=10)
    table.add_column("Severity", width=10)
    table.add_column("Issue",    width=55)
    table.add_column("Resource", width=28)

    sev_style = {"Critical": "bold red", "High": "red", "Medium": "yellow",
                 "Low": "green", "Info": "dim"}

    for i, f in enumerate(findings, 1):
        sev = f.get("severity", "Info")
        table.add_row(
            str(i),
            f.get("cloud", ""),
            f.get("category", ""),
            f"[{sev_style.get(sev, 'white')}]{sev}[/{sev_style.get(sev, 'white')}]",
            f.get("issue", ""),
            f.get("resource", ""),
        )
    console.print(table)


def main():
    parser = argparse.ArgumentParser(description="CloudGRC-AI — Cloud Compliance Scanner")
    parser.add_argument("--providers", nargs="+", choices=["aws", "gcp", "azure"],
                        default=["aws"], help="Cloud providers to scan")
    parser.add_argument("--output", default="./reports", help="Output directory for reports")
    parser.add_argument("--org", default="Organisation", help="Organisation name for report")
    parser.add_argument("--mock", action="store_true", help="Use mock data for testing")
    parser.add_argument("--no-pdf", action="store_true", help="Skip PDF generation")
    args = parser.parse_args()

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    console.print("[bold cyan]\n╔══════════════════════════════════════════╗[/bold cyan]")
    console.print("[bold cyan]║        CloudGRC-AI Security Scanner       ║[/bold cyan]")
    console.print("[bold cyan]╚══════════════════════════════════════════╝[/bold cyan]\n")

    all_findings = []

    if args.mock:
        console.print("[yellow]Running in MOCK mode — using sample findings...[/yellow]\n")
        all_findings = load_mock_findings()
    else:
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
            if "aws" in args.providers:
                t = progress.add_task("[cyan]Scanning AWS...", total=None)
                all_findings += run_aws_checks()
                progress.remove_task(t)
            if "gcp" in args.providers:
                t = progress.add_task("[cyan]Scanning GCP...", total=None)
                all_findings += run_gcp_checks()
                progress.remove_task(t)
            if "azure" in args.providers:
                t = progress.add_task("[cyan]Scanning Azure...", total=None)
                all_findings += run_azure_checks()
                progress.remove_task(t)

    # Compliance mapping
    from compliance.mapping import map_all_findings, calculate_risk_score
    all_findings = map_all_findings(all_findings)
    all_findings.sort(key=lambda x: SEVERITY_ORDER.get(x.get("severity", "Info"), 99))
    risk_data = calculate_risk_score(all_findings)

    # Print results
    print_findings_table(all_findings)
    console.print(f"\n[bold]Risk Score:[/bold] [red]{risk_data['risk_score']}/100[/red]")
    console.print(f"[bold]Compliance:[/bold] [green]{risk_data['compliance_pct']}%[/green]")
    console.print(f"[bold]Breakdown:[/bold] {risk_data['breakdown']}\n")

    # AI Report
    from reporting.ai_summary import generate_ai_report
    console.print("[cyan]Generating AI audit narrative...[/cyan]")
    ai_report = generate_ai_report(all_findings, risk_data)

    # JSON export
    json_path = output_dir / f"cloudgrc_report_{timestamp}.json"
    with open(json_path, "w") as f:
        json.dump({
            "scan_timestamp": timestamp,
            "risk_summary": risk_data,
            "ai_report": ai_report,
            "findings": all_findings,
        }, f, indent=2, default=str)
    console.print(f"[green]JSON report saved: {json_path}[/green]")

    # PDF export
    if not args.no_pdf:
        from reporting.pdf_generator import generate_pdf_report
        pdf_path = str(output_dir / f"cloudgrc_report_{timestamp}.pdf")
        generate_pdf_report(all_findings, risk_data, ai_report, pdf_path, args.org)
        console.print(f"[green]PDF report saved: {pdf_path}[/green]")

    # CSV export
    import csv
    csv_path = output_dir / f"cloudgrc_findings_{timestamp}.csv"
    if all_findings:
        with open(csv_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=all_findings[0].keys())
            writer.writeheader()
            writer.writerows(all_findings)
        console.print(f"[green]CSV export saved: {csv_path}[/green]")

    console.print("\n[bold cyan]Scan complete.[/bold cyan]\n")


if __name__ == "__main__":
    main()
