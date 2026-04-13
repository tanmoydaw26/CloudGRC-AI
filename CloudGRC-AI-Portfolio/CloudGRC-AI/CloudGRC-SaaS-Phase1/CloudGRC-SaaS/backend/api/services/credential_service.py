"""
Credential service — store and retrieve encrypted cloud credentials.
"""
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException
from backend.api.models.credential import CloudCredential
from backend.api.models.user import User
from backend.api.schemas.credential import CredentialCreate
from backend.core.security import encrypt_credential, decrypt_credential


async def save_credential(data: CredentialCreate, user: User, db: AsyncSession) -> CloudCredential:
    cred = CloudCredential(user_id=user.id, provider=data.provider, label=data.label)

    # Encrypt all sensitive fields before storing
    if data.aws_access_key_id:
        cred.aws_access_key_id     = encrypt_credential(data.aws_access_key_id)
        cred.aws_secret_access_key = encrypt_credential(data.aws_secret_access_key)
        cred.aws_region            = data.aws_region
    if data.gcp_project_id:
        cred.gcp_project_id            = data.gcp_project_id
        cred.gcp_service_account_json  = encrypt_credential(data.gcp_service_account_json)
    if data.azure_subscription_id:
        cred.azure_subscription_id = encrypt_credential(data.azure_subscription_id)
        cred.azure_tenant_id       = encrypt_credential(data.azure_tenant_id)
        cred.azure_client_id       = encrypt_credential(data.azure_client_id)
        cred.azure_client_secret   = encrypt_credential(data.azure_client_secret)

    db.add(cred)
    await db.flush()
    await db.refresh(cred)
    return cred


async def get_credentials(user_id: UUID, db: AsyncSession):
    result = await db.execute(select(CloudCredential).where(CloudCredential.user_id == user_id))
    return result.scalars().all()


async def delete_credential(cred_id: UUID, user_id: UUID, db: AsyncSession):
    result = await db.execute(
        select(CloudCredential).where(CloudCredential.id == cred_id, CloudCredential.user_id == user_id)
    )
    cred = result.scalar_one_or_none()
    if not cred:
        raise HTTPException(status_code=404, detail="Credential not found")
    await db.delete(cred)
