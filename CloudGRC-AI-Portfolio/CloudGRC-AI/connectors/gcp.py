"""
GCP Connector — authenticates via a service account JSON key file.
Uses google-cloud SDK for IAM, GCS, and Logging checks.
"""
import os
from dotenv import load_dotenv

load_dotenv()

def get_gcp_credentials():
    """Return GCP credentials and project ID from environment."""
    cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    project_id = os.getenv("GCP_PROJECT_ID")
    if not cred_path or not project_id:
        raise RuntimeError("[GCP] Set GOOGLE_APPLICATION_CREDENTIALS and GCP_PROJECT_ID env vars.")
    try:
        from google.oauth2 import service_account
        credentials = service_account.Credentials.from_service_account_file(
            cred_path,
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )
        print(f"[GCP] Authenticated for project: {project_id}")
        return credentials, project_id
    except Exception as e:
        raise RuntimeError(f"[GCP] Auth failed: {e}")

def get_gcs_client():
    from google.cloud import storage
    creds, project = get_gcp_credentials()
    return storage.Client(credentials=creds, project=project)

def get_iam_service():
    from googleapiclient import discovery
    creds, _ = get_gcp_credentials()
    return discovery.build("iam", "v1", credentials=creds)

def get_logging_client():
    from google.cloud import logging as gcp_logging
    creds, project = get_gcp_credentials()
    return gcp_logging.Client(credentials=creds, project=project)
