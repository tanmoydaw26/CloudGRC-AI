from pydantic import BaseModel
from typing import Optional


class CreateOrderRequest(BaseModel):
    plan: str  # starter | pro | enterprise

class VerifyPaymentRequest(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str
    plan: str

class BillingStatusOut(BaseModel):
    plan: str
    scans_used: int
    scans_limit: int
    subscription_id: Optional[str]
