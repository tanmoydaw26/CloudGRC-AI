"""
Billing routes — Razorpay order creation, payment verification, plan status.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from backend.db.base import get_db
from backend.api.schemas.billing import CreateOrderRequest, VerifyPaymentRequest, BillingStatusOut
from backend.api.services.billing_service import create_order, verify_and_upgrade, PLAN_PRICING
from backend.api.middleware.auth_middleware import get_authenticated_user
from backend.api.models.user import User
from backend.core.config import settings

router = APIRouter(prefix="/billing", tags=["Billing"])

PLAN_LIMITS = {
    "free": settings.PLAN_FREE_SCANS_PER_MONTH,
    "starter": settings.PLAN_STARTER_SCANS_PER_MONTH,
    "pro": settings.PLAN_PRO_SCANS_PER_MONTH,
    "enterprise": 9999,
}


@router.get("/plans")
async def get_plans():
    """Return all available plans with pricing."""
    return {
        "plans": [
            {"id": "free",       "name": "Free",       "price_inr": 0,    "scans_per_month": 1,   "features": ["1 cloud", "Mock mode only", "JSON export"]},
            {"id": "starter",    "name": "Starter",    "price_inr": 999,  "scans_per_month": 10,  "features": ["1 cloud", "10 scans/month", "PDF reports", "Email alerts"]},
            {"id": "pro",        "name": "Pro",         "price_inr": 2999, "scans_per_month": 999, "features": ["All 3 clouds", "Unlimited scans", "AI reports", "API access", "Priority support"]},
            {"id": "enterprise", "name": "Enterprise",  "price_inr": None, "scans_per_month": 9999,"features": ["White-label", "Custom frameworks", "SSO", "Dedicated support", "SLA"]},
        ]
    }


@router.post("/order")
async def create_payment_order(
    data: CreateOrderRequest,
    current_user: User = Depends(get_authenticated_user),
):
    """Create a Razorpay order for plan upgrade."""
    return await create_order(data.plan, current_user)


@router.post("/verify")
async def verify_payment(
    data: VerifyPaymentRequest,
    current_user: User = Depends(get_authenticated_user),
    db: AsyncSession = Depends(get_db),
):
    """Verify Razorpay payment signature and upgrade plan."""
    return await verify_and_upgrade(data, current_user, db)


@router.get("/status", response_model=BillingStatusOut)
async def billing_status(current_user: User = Depends(get_authenticated_user)):
    """Get current plan, usage, and limits."""
    plan_key = current_user.plan.value
    return BillingStatusOut(
        plan=plan_key,
        scans_used=current_user.scans_used_this_month,
        scans_limit=PLAN_LIMITS.get(plan_key, 1),
        subscription_id=current_user.razorpay_subscription_id,
    )
