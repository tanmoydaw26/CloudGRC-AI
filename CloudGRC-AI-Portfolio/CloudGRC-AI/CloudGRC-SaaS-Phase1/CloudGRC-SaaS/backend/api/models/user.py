"""
User model — stores account info, plan, and scan quota.
"""
import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, Integer, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from backend.db.base import Base
import enum


class PlanType(str, enum.Enum):
    FREE     = "free"
    STARTER  = "starter"
    PRO      = "pro"
    ENTERPRISE = "enterprise"


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID]         = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str]            = mapped_column(String(255), unique=True, index=True, nullable=False)
    full_name: Mapped[str]        = mapped_column(String(255), nullable=False)
    hashed_password: Mapped[str]  = mapped_column(String(255), nullable=False)
    company: Mapped[str]          = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool]       = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool]     = mapped_column(Boolean, default=False)
    is_superuser: Mapped[bool]    = mapped_column(Boolean, default=False)
    plan: Mapped[PlanType]        = mapped_column(SAEnum(PlanType), default=PlanType.FREE)
    scans_used_this_month: Mapped[int] = mapped_column(Integer, default=0)
    razorpay_customer_id: Mapped[str]  = mapped_column(String(255), nullable=True)
    razorpay_subscription_id: Mapped[str] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime]  = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime]  = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    scans: Mapped[list["Scan"]]   = relationship("Scan", back_populates="user", cascade="all, delete-orphan")
    credentials: Mapped[list["CloudCredential"]] = relationship("CloudCredential", back_populates="user", cascade="all, delete-orphan")
