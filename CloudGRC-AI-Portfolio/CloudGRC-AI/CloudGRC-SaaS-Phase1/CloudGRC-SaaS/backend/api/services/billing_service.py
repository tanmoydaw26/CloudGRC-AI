"""
Billing service — Razorpay order creation and payment verification.
"""
import hmac, hashlib
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from backend.api.models.user import User, PlanType
from backend.core.config import settings

PLAN_PRICING = {
    "starter":    {"amount": 99900,  "currency": "INR", "plan": PlanType.STARTER},
    "pro":        {"amount": 299900, "currency": "INR", "plan": PlanType.PRO},
    "enterprise": {"amount": 999900, "currency": "INR", "plan": PlanType.ENTERPRISE},
}


def get_razorpay_client():
    try:
        import razorpay
        return razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    except Exception:
        raise HTTPException(status_code=503, detail="Billing service unavailable")


async def create_order(plan: str, user: User) -> dict:
    if plan not in PLAN_PRICING:
        raise HTTPException(status_code=400, detail=f"Invalid plan: {plan}")
    pricing = PLAN_PRICING[plan]
    client  = get_razorpay_client()
    order   = client.order.create({
        "amount":   pricing["amount"],
        "currency": pricing["currency"],
        "notes":    {"user_id": str(user.id), "plan": plan, "email": user.email},
    })
    return {
        "order_id":   order["id"],
        "amount":     pricing["amount"],
        "currency":   pricing["currency"],
        "key_id":     settings.RAZORPAY_KEY_ID,
        "plan":       plan,
        "user_name":  user.full_name,
        "user_email": user.email,
    }


async def verify_and_upgrade(data, user: User, db: AsyncSession) -> dict:
    """Verify Razorpay signature and upgrade user plan."""
    expected = hmac.new(
        settings.RAZORPAY_KEY_SECRET.encode(),
        f"{data.razorpay_order_id}|{data.razorpay_payment_id}".encode(),
        hashlib.sha256
    ).hexdigest()

    if expected != data.razorpay_signature:
        raise HTTPException(status_code=400, detail="Payment verification failed")

    plan_type = PLAN_PRICING[data.plan]["plan"]
    user.plan = plan_type
    user.scans_used_this_month = 0
    user.razorpay_subscription_id = data.razorpay_payment_id
    await db.flush()
    return {"status": "success", "plan": plan_type, "message": f"Upgraded to {data.plan} plan successfully"}
