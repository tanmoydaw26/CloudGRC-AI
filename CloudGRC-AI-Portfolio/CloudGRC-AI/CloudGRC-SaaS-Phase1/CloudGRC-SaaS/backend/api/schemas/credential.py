from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from backend.api.models.scan import CloudProvider


class CredentialCreate(BaseModel):
    provider: CloudProvider
    label: str
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    aws_region: Optional[str] = "ap-south-1"
    gcp_project_id: Optional[str] = None
    gcp_service_account_json: Optional[str] = None
    azure_subscription_id: Optional[str] = None
    azure_tenant_id: Optional[str] = None
    azure_client_id: Optional[str] = None
    azure_client_secret: Optional[str] = None

class CredentialOut(BaseModel):
    id: UUID
    provider: CloudProvider
    label: str
    class Config:
        from_attributes = True
