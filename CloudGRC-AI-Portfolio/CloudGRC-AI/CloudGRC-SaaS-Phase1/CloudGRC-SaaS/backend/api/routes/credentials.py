"""
Cloud credential routes — save, list, and delete encrypted credentials.
"""
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from backend.db.base import get_db
from backend.api.schemas.credential import CredentialCreate, CredentialOut
from backend.api.services.credential_service import save_credential, get_credentials, delete_credential
from backend.api.middleware.auth_middleware import get_authenticated_user
from backend.api.models.user import User

router = APIRouter(prefix="/credentials", tags=["Cloud Credentials"])


@router.post("", response_model=CredentialOut, status_code=status.HTTP_201_CREATED)
async def add_credential(
    data: CredentialCreate,
    current_user: User = Depends(get_authenticated_user),
    db: AsyncSession = Depends(get_db),
):
    """Save encrypted cloud credentials for a provider."""
    return await save_credential(data, current_user, db)


@router.get("", response_model=List[CredentialOut])
async def list_credentials(
    current_user: User = Depends(get_authenticated_user),
    db: AsyncSession = Depends(get_db),
):
    """List all saved credentials (labels only — secrets never returned)."""
    return await get_credentials(current_user.id, db)


@router.delete("/{credential_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_credential(
    credential_id: UUID,
    current_user: User = Depends(get_authenticated_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a saved credential."""
    await delete_credential(credential_id, current_user.id, db)
    return None
