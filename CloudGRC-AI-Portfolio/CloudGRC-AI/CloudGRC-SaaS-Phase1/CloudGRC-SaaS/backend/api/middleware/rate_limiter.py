"""
Simple Redis-based rate limiter — 60 requests per minute per user.
"""
import time
from fastapi import HTTPException, Request
from backend.core.config import settings


async def rate_limit(request: Request):
    try:
        import redis as redis_client
        r = redis_client.from_url(settings.REDIS_URL)
        client_ip = request.client.host
        key = f"rate_limit:{client_ip}"
        current = r.incr(key)
        if current == 1:
            r.expire(key, 60)
        if current > 60:
            raise HTTPException(status_code=429, detail="Too many requests. Please wait.")
    except HTTPException:
        raise
    except Exception:
        pass  # Fail open if Redis is unavailable
