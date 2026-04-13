"""
Celery tasks — run cloud scans asynchronously and save results to DB.
"""
from datetime import datetime
from backend.workers.celery_app import celery_app
from backend.core.config import settings
import logging

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=2, default_retry_delay=10)
def run_scan_task(self, scan_id: str, providers: list, org_name: str,
                  credential_id: str = None, use_mock: bool = False, user_id: str = None):
    """
    Core async scan task.
    1. Load credentials from DB
    2. Run cloud checks
    3. Map to compliance frameworks
    4. Generate AI report + PDF
    5. Upload PDF to S3
    6. Update scan record in DB
    """
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from backend.api.models.scan import Scan, ScanStatus
    from backend.api.models.credential import CloudCredential
    from backend.core.security import decrypt_credential

    # ── Sync DB session for Celery ──
    engine  = create_engine(settings.SYNC_DATABASE_URL)
    Session = sessionmaker(bind=engine)
    db      = Session()

    try:
        scan = db.query(Scan).filter(Scan.id == scan_id).first()
        if not scan:
            logger.error(f"Scan {scan_id} not found")
            return

        scan.status     = ScanStatus.RUNNING
        scan.started_at = datetime.utcnow()
        db.commit()

        all_findings = []

        if use_mock:
            # ── Load mock findings ──
            from scan_engine.mock_data import MOCK_FINDINGS
            all_findings = MOCK_FINDINGS
        else:
            # ── Load real credentials ──
            creds = None
            if credential_id:
                creds = db.query(CloudCredential).filter(
                    CloudCredential.id == credential_id,
                    CloudCredential.user_id == user_id
                ).first()

            # ── Run checks per provider ──
            for provider in providers:
                try:
                    if provider == "aws":
                        from scan_engine.connectors.aws import AWSConnector
                        from scan_engine.checks.iam import run_iam_checks
                        from scan_engine.checks.storage import run_storage_checks
                        from scan_engine.checks.network import run_network_checks
                        from scan_engine.checks.logging import run_logging_checks

                        aws_creds = {}
                        if creds and creds.aws_access_key_id:
                            aws_creds = {
                                "aws_access_key_id":     decrypt_credential(creds.aws_access_key_id),
                                "aws_secret_access_key": decrypt_credential(creds.aws_secret_access_key),
                                "region_name":           creds.aws_region or "ap-south-1",
                            }
                        session = AWSConnector(**aws_creds).get_session()
                        all_findings += run_iam_checks(session)
                        all_findings += run_storage_checks(session)
                        all_findings += run_network_checks(session)
                        all_findings += run_logging_checks(session)

                    elif provider == "gcp":
                        from scan_engine.connectors.gcp import GCPConnector
                        from scan_engine.checks.iam import run_gcp_iam_checks
                        from scan_engine.checks.storage import run_gcp_storage_checks

                        gcp_creds = {}
                        if creds and creds.gcp_service_account_json:
                            gcp_creds = {
                                "project_id":           creds.gcp_project_id,
                                "service_account_json": decrypt_credential(creds.gcp_service_account_json),
                            }
                        connector = GCPConnector(**gcp_creds)
                        all_findings += run_gcp_iam_checks(connector)
                        all_findings += run_gcp_storage_checks(connector)

                    elif provider == "azure":
                        from scan_engine.connectors.azure import AzureConnector
                        from scan_engine.checks.iam import run_azure_iam_checks
                        from scan_engine.checks.storage import run_azure_storage_checks

                        az_creds = {}
                        if creds and creds.azure_subscription_id:
                            az_creds = {
                                "subscription_id": decrypt_credential(creds.azure_subscription_id),
                                "tenant_id":       decrypt_credential(creds.azure_tenant_id),
                                "client_id":       decrypt_credential(creds.azure_client_id),
                                "client_secret":   decrypt_credential(creds.azure_client_secret),
                            }
                        connector = AzureConnector(**az_creds)
                        all_findings += run_azure_iam_checks(connector)
                        all_findings += run_azure_storage_checks(connector)

                except Exception as e:
                    logger.warning(f"Provider {provider} scan failed: {e}")
                    all_findings.append({
                        "cloud": provider.upper(), "category": "System",
                        "issue": f"{provider.upper()} scan error: {str(e)}",
                        "severity": "Info", "resource": "N/A", "detail": str(e),
                    })

        # ── Compliance mapping ──
        from scan_engine.compliance.mapping import map_all_findings, calculate_risk_score
        all_findings = map_all_findings(all_findings)
        risk_data    = calculate_risk_score(all_findings)

        # ── AI Report ──
        ai_report = {}
        try:
            from scan_engine.reporting.ai_summary import generate_ai_report
            ai_report = generate_ai_report(all_findings, risk_data)
        except Exception as e:
            logger.warning(f"AI report failed: {e}")

        # ── PDF Generation ──
        pdf_url = None
        try:
            import tempfile, boto3
            from scan_engine.reporting.pdf_generator import generate_pdf_report
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
                pdf_path = tmp.name
            generate_pdf_report(all_findings, risk_data, ai_report, pdf_path, org_name)

            # Upload to S3
            s3 = boto3.client("s3",
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.S3_REGION,
            )
            s3_key = f"reports/{user_id}/{scan_id}.pdf"
            s3.upload_file(pdf_path, settings.S3_BUCKET_NAME, s3_key,
                           ExtraArgs={"ContentType": "application/pdf"})
            pdf_url = s3.generate_presigned_url("get_object",
                Params={"Bucket": settings.S3_BUCKET_NAME, "Key": s3_key},
                ExpiresIn=86400)
        except Exception as e:
            logger.warning(f"PDF upload failed: {e}")

        # ── Update scan record ──
        breakdown = risk_data.get("breakdown", {})
        scan.status        = ScanStatus.COMPLETED
        scan.findings      = all_findings
        scan.risk_score    = risk_data.get("risk_score", 0)
        scan.compliance_pct= risk_data.get("compliance_pct", 0)
        scan.total_findings= risk_data.get("total_findings", 0)
        scan.critical_count= breakdown.get("Critical", 0)
        scan.high_count    = breakdown.get("High", 0)
        scan.medium_count  = breakdown.get("Medium", 0)
        scan.low_count     = breakdown.get("Low", 0)
        scan.ai_report     = ai_report
        scan.pdf_url       = pdf_url
        scan.completed_at  = datetime.utcnow()
        db.commit()

        # ── Send email notification ──
        send_report_email.delay(user_id=user_id, scan_id=scan_id, pdf_url=pdf_url)
        logger.info(f"Scan {scan_id} completed — {scan.total_findings} findings")

    except Exception as exc:
        scan.status        = ScanStatus.FAILED
        scan.error_message = str(exc)
        scan.completed_at  = datetime.utcnow()
        db.commit()
        logger.error(f"Scan {scan_id} failed: {exc}")
        raise self.retry(exc=exc)
    finally:
        db.close()


@celery_app.task
def send_report_email(user_id: str, scan_id: str, pdf_url: str = None):
    """Send scan completion email to user."""
    try:
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from backend.api.models.user import User
        from backend.api.models.scan import Scan
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart

        engine  = create_engine(settings.SYNC_DATABASE_URL)
        Session = sessionmaker(bind=engine)
        db      = Session()

        user = db.query(User).filter(User.id == user_id).first()
        scan = db.query(Scan).filter(Scan.id == scan_id).first()
        if not user or not scan or not settings.SMTP_USER:
            return

        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"CloudGRC-AI — Scan Complete: {scan.org_name}"
        msg["From"]    = settings.EMAILS_FROM
        msg["To"]      = user.email

        html = f"""
        <html><body style="font-family:Arial,sans-serif;background:#f7f9fc;padding:20px">
        <div style="max-width:600px;margin:0 auto;background:white;border-radius:8px;padding:30px">
        <h2 style="color:#1a2940">🛡️ CloudGRC-AI Scan Complete</h2>
        <p>Hi {user.full_name},</p>
        <p>Your scan for <strong>{scan.org_name}</strong> has completed.</p>
        <table style="width:100%;border-collapse:collapse;margin:20px 0">
          <tr style="background:#e8f4f7">
            <td style="padding:10px;font-weight:bold">Risk Score</td>
            <td style="padding:10px">{scan.risk_score}/100</td>
          </tr>
          <tr>
            <td style="padding:10px;font-weight:bold">Compliance</td>
            <td style="padding:10px">{scan.compliance_pct}%</td>
          </tr>
          <tr style="background:#e8f4f7">
            <td style="padding:10px;font-weight:bold">Total Findings</td>
            <td style="padding:10px">{scan.total_findings}</td>
          </tr>
          <tr>
            <td style="padding:10px;font-weight:bold;color:#ff003c">Critical</td>
            <td style="padding:10px">{scan.critical_count}</td>
          </tr>
        </table>
        {"<a href='" + pdf_url + "' style='background:#2a6b7c;color:white;padding:12px 24px;text-decoration:none;border-radius:4px'>Download PDF Report</a>" if pdf_url else ""}
        <p style="color:#888;font-size:12px;margin-top:30px">CloudGRC-AI — Automated Cloud Compliance & Risk Scanner</p>
        </div></body></html>
        """
        msg.attach(MIMEText(html, "html"))

        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.EMAILS_FROM, user.email, msg.as_string())

        db.close()
    except Exception as e:
        logger.warning(f"Email send failed: {e}")
