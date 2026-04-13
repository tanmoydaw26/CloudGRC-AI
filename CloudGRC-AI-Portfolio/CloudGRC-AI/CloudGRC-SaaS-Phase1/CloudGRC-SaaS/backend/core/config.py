"""
Application configuration using Pydantic Settings.
All values loaded from environment variables / .env file.
"""
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl, validator
from typing import List, Optional
from functools import lru_cache


class Settings(BaseSettings):
    # ── App ──
    APP_NAME: str = "CloudGRC-AI"
    APP_ENV: str = "development"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"

    # ── Security ──
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ── Database ──
    DATABASE_URL: str
    SYNC_DATABASE_URL: str

    # ── Redis / Celery ──
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"

    # ── AWS S3 ──
    S3_BUCKET_NAME: str = "cloudgrc-reports"
    S3_REGION: str = "ap-south-1"
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None

    # ── OpenAI ──
    OPENAI_API_KEY: Optional[str] = None

    # ── Razorpay ──
    RAZORPAY_KEY_ID: Optional[str] = None
    RAZORPAY_KEY_SECRET: Optional[str] = None

    # ── Email ──
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM: str = "noreply@cloudgrc.ai"

    # ── Frontend ──
    FRONTEND_URL: str = "http://localhost:3000"
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8501"]

    # ── Sentry ──
    SENTRY_DSN: Optional[str] = None

    # ── Plans ──
    PLAN_FREE_SCANS_PER_MONTH: int = 1
    PLAN_STARTER_SCANS_PER_MONTH: int = 10
    PLAN_PRO_SCANS_PER_MONTH: int = 999

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
