"""
Dashboard routes — aggregated stats for the user dashboard.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from backend.db.base import get_db
from backend.api.models.scan import Scan, ScanStatus
from backend.api.middleware.auth_middleware import get_authenticated_user
from backend.api.models.user import User

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/stats")
async def get_dashboard_stats(
    current_user: User = Depends(get_authenticated_user),
    db: AsyncSession = Depends(get_db),
):
    """Return summary stats for the authenticated user dashboard."""
    result = await db.execute(
        select(
            func.count(Scan.id).label("total_scans"),
            func.avg(Scan.risk_score).label("avg_risk_score"),
            func.avg(Scan.compliance_pct).label("avg_compliance"),
            func.sum(Scan.total_findings).label("total_findings"),
            func.sum(Scan.critical_count).label("total_critical"),
            func.sum(Scan.high_count).label("total_high"),
        ).where(Scan.user_id == current_user.id)
    )
    row = result.one()

    # Last 5 scans
    recent_result = await db.execute(
        select(Scan).where(Scan.user_id == current_user.id)
        .order_by(Scan.created_at.desc()).limit(5)
    )
    recent_scans = recent_result.scalars().all()

    return {
        "user": {
            "name":  current_user.full_name,
            "plan":  current_user.plan,
            "scans_used":  current_user.scans_used_this_month,
        },
        "totals": {
            "total_scans":    row.total_scans or 0,
            "avg_risk_score": round(row.avg_risk_score or 0, 1),
            "avg_compliance": round(row.avg_compliance or 0, 1),
            "total_findings": row.total_findings or 0,
            "total_critical": row.total_critical or 0,
            "total_high":     row.total_high or 0,
        },
        "recent_scans": [
            {
                "id":           str(s.id),
                "org_name":     s.org_name,
                "providers":    s.providers,
                "status":       s.status,
                "risk_score":   s.risk_score,
                "compliance_pct": s.compliance_pct,
                "created_at":   s.created_at.isoformat(),
            }
            for s in recent_scans
        ],
    }
