"""
Scan model — one record per scan execution, with findings stored as JSONB.
"""
import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Integer, Float, Text, ForeignKey, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.db.base import Base
import enum


class ScanStatus(str, enum.Enum):
    PENDING   = "pending"
    RUNNING   = "running"
    COMPLETED = "completed"
    FAILED    = "failed"


class CloudProvider(str, enum.Enum):
    AWS   = "aws"
    GCP   = "gcp"
    AZURE = "azure"


class Scan(Base):
    __tablename__ = "scans"

    id: Mapped[uuid.UUID]         = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID]    = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    org_name: Mapped[str]         = mapped_column(String(255), nullable=False)
    providers: Mapped[list]       = mapped_column(JSONB, default=list)
    status: Mapped[ScanStatus]    = mapped_column(SAEnum(ScanStatus), default=ScanStatus.PENDING)
    findings: Mapped[list]        = mapped_column(JSONB, default=list)
    risk_score: Mapped[float]     = mapped_column(Float, nullable=True)
    compliance_pct: Mapped[float] = mapped_column(Float, nullable=True)
    total_findings: Mapped[int]   = mapped_column(Integer, default=0)
    critical_count: Mapped[int]   = mapped_column(Integer, default=0)
    high_count: Mapped[int]       = mapped_column(Integer, default=0)
    medium_count: Mapped[int]     = mapped_column(Integer, default=0)
    low_count: Mapped[int]        = mapped_column(Integer, default=0)
    ai_report: Mapped[dict]       = mapped_column(JSONB, nullable=True)
    pdf_url: Mapped[str]          = mapped_column(String(500), nullable=True)
    error_message: Mapped[str]    = mapped_column(Text, nullable=True)
    celery_task_id: Mapped[str]   = mapped_column(String(255), nullable=True)
    started_at: Mapped[datetime]  = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime]= mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime]  = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"]          = relationship("User", back_populates="scans")
