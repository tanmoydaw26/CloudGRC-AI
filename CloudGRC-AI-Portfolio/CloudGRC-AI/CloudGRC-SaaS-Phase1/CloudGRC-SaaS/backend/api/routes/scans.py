"""
Scan routes — trigger scans, list history, get detail, download report.
"""
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from backend.db.base import get_db
from backend.api.schemas.scan import ScanCreate, ScanOut, ScanDetail
from backend.api.services.scan_service import create_scan, get_user_scans, get_scan_detail
from backend.api.middleware.auth_middleware import get_authenticated_user
from backend.api.models.user import User

router = APIRouter(prefix="/scans", tags=["Scans"])


@router.post("", response_model=ScanOut, status_code=201)
async def trigger_scan(
    data: ScanCreate,
    current_user: User = Depends(get_authenticated_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Trigger a new cloud security scan.
    - Free plan: mock mode only, 1 scan/month
    - Starter: 1 real cloud, 10 scans/month
    - Pro: all clouds, unlimited scans
    """
    return await create_scan(data, current_user, db)


@router.get("", response_model=List[ScanOut])
async def list_scans(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_authenticated_user),
    db: AsyncSession = Depends(get_db),
):
    """List all scans for the current user, newest first."""
    return await get_user_scans(current_user.id, db, skip, limit)


@router.get("/{scan_id}", response_model=ScanDetail)
async def get_scan(
    scan_id: UUID,
    current_user: User = Depends(get_authenticated_user),
    db: AsyncSession = Depends(get_db),
):
    """Get full scan detail including all findings and AI report."""
    return await get_scan_detail(scan_id, current_user.id, db)


@router.get("/{scan_id}/download")
async def download_report(
    scan_id: UUID,
    current_user: User = Depends(get_authenticated_user),
    db: AsyncSession = Depends(get_db),
):
    """Redirect to the signed S3 PDF download URL."""
    scan = await get_scan_detail(scan_id, current_user.id, db)
    if not scan.pdf_url:
        raise HTTPException(status_code=404, detail="PDF report not yet available")
    return RedirectResponse(url=scan.pdf_url)


@router.delete("/{scan_id}", status_code=204)
async def delete_scan(
    scan_id: UUID,
    current_user: User = Depends(get_authenticated_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a scan record and its associated report."""
    from sqlalchemy import select, delete
    from backend.api.models.scan import Scan
    result = await db.execute(
        select(Scan).where(Scan.id == scan_id, Scan.user_id == current_user.id)
    )
    scan = result.scalar_one_or_none()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    await db.delete(scan)
    return None
