"""
CloudCredential model — encrypted cloud credentials per user per provider.
"""
import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, Enum as SAEnum, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.db.base import Base
from backend.api.models.scan import CloudProvider


class CloudCredential(Base):
    __tablename__ = "cloud_credentials"

    id: Mapped[uuid.UUID]       = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID]  = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    provider: Mapped[CloudProvider] = mapped_column(SAEnum(CloudProvider), nullable=False)
    label: Mapped[str]          = mapped_column(String(255), nullable=False)

    # Encrypted credential fields
    aws_access_key_id: Mapped[str]     = mapped_column(Text, nullable=True)
    aws_secret_access_key: Mapped[str] = mapped_column(Text, nullable=True)
    aws_region: Mapped[str]            = mapped_column(String(50), nullable=True)
    gcp_project_id: Mapped[str]        = mapped_column(String(255), nullable=True)
    gcp_service_account_json: Mapped[str] = mapped_column(Text, nullable=True)
    azure_subscription_id: Mapped[str] = mapped_column(Text, nullable=True)
    azure_tenant_id: Mapped[str]       = mapped_column(Text, nullable=True)
    azure_client_id: Mapped[str]       = mapped_column(Text, nullable=True)
    azure_client_secret: Mapped[str]   = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user: Mapped["User"] = relationship("User", back_populates="credentials")
