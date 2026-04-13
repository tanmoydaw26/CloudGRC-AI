"""
Scan service — create scan records, check quota, trigger Celery tasks.
"""
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from fastapi import HTTPException
from backend.api.models.scan import Scan, ScanStatus
from backend.api.models.user import User, PlanType
from backend.api.models.credential import CloudCredential
from backend.api.schemas.scan import ScanCreate
from backend.core.config import settings


PLAN_LIMITS = {
    PlanType.FREE:       settings.PLAN_FREE_SCANS_PER_MONTH,
    PlanType.STARTER:    settings.PLAN_STARTER_SCANS_PER_MONTH,
    PlanType.PRO:        settings.PLAN_PRO_SCANS_PER_MONTH,
    PlanType.ENTERPRISE: 9999,
}


async def create_scan(data: ScanCreate, user: User, db: AsyncSession) -> Scan:
    # ── Quota check ──
    limit = PLAN_LIMITS.get(user.plan, 1)
    if user.scans_used_this_month >= limit:
        raise HTTPException(
            status_code=403,
            detail=f"Monthly scan limit reached ({limit} scans on {user.plan} plan). Please upgrade."
        )

    # ── Mock check for free plan ──
    if user.plan == PlanType.FREE and not data.use_mock:
        raise HTTPException(status_code=403, detail="Free plan supports demo mode only. Upgrade to scan real environments.")

    scan = Scan(
        user_id=user.id,
        org_name=data.org_name,
        providers=data.providers,
        status=ScanStatus.PENDING,
    )
    db.add(scan)
    await db.flush()
    await db.refresh(scan)

    # ── Increment quota ──
    user.scans_used_this_month += 1

    # ── Trigger async Celery task ──
    from backend.workers.tasks import run_scan_task
    task = run_scan_task.delay(
        scan_id=str(scan.id),
        providers=data.providers,
        org_name=data.org_name,
        credential_id=str(data.credential_id) if data.credential_id else None,
        use_mock=data.use_mock,
        user_id=str(user.id),
    )
    scan.celery_task_id = task.id
    return scan


async def get_user_scans(user_id: UUID, db: AsyncSession, skip: int = 0, limit: int = 20):
    result = await db.execute(
        select(Scan).where(Scan.user_id == user_id)
        .order_by(Scan.created_at.desc())
        .offset(skip).limit(limit)
    )
    return result.scalars().all()


async def get_scan_detail(scan_id: UUID, user_id: UUID, db: AsyncSession) -> Scan:
    result = await db.execute(
        select(Scan).where(Scan.id == scan_id, Scan.user_id == user_id)
    )
    scan = result.scalar_one_or_none()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    return scan
