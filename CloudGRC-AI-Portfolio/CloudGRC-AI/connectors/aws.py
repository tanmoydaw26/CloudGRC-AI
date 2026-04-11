"""
AWS Connector — authenticates via environment variables or AWS config profiles.
Uses boto3 to establish sessions for IAM, S3, EC2, CloudTrail checks.
"""
import boto3
import os
from botocore.exceptions import NoCredentialsError, ClientError
from dotenv import load_dotenv

load_dotenv()

def get_aws_session(profile_name: str = None) -> boto3.Session:
    """Return an authenticated boto3 session."""
    try:
        if profile_name:
            session = boto3.Session(profile_name=profile_name)
        else:
            session = boto3.Session(
                aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
                region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-1")
            )
        # Validate credentials
        sts = session.client("sts")
        identity = sts.get_caller_identity()
        print(f"[AWS] Authenticated as: {identity.get('Arn')}")
        return session
    except NoCredentialsError:
        raise RuntimeError("[AWS] No credentials found. Set AWS env vars or configure a profile.")
    except ClientError as e:
        raise RuntimeError(f"[AWS] Auth failed: {e}")

def get_client(service: str, session: boto3.Session = None):
    """Return a boto3 client for the given service."""
    s = session or get_aws_session()
    return s.client(service)
