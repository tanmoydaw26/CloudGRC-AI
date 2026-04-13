from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from backend.api.models.scan import ScanStatus


class ScanCreate(BaseModel):
    org_name: str
    providers: List[str]
    credential_id: Optional[UUID] = None
    use_mock: bool = False

class ScanOut(BaseModel):
    id: UUID
    org_name: str
    providers: List[str]
    status: ScanStatus
    risk_score: Optional[float]
    compliance_pct: Optional[float]
    total_findings: int
    critical_count: int
    high_count: int
    pdf_url: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime]
    class Config:
        from_attributes = True

class ScanDetail(ScanOut):
    findings: List[dict]
    ai_report: Optional[dict]
    error_message: Optional[str]
