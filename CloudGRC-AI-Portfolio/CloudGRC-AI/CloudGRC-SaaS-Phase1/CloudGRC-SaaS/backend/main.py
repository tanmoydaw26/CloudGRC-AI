"""
CloudGRC-AI SaaS — FastAPI Application Entry Point
Run with: uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import time

from backend.core.config import settings
from backend.api.routes import auth, scans, credentials, billing, dashboard

# ── Logging ──
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)

# ── App Init ──
app = FastAPI(
    title="CloudGRC-AI API",
    description="Automated Cloud Compliance & Risk Scanner — REST API",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# ── CORS ──
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Request Timing Middleware ──
@app.middleware("http")
async def add_process_time(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    response.headers["X-Process-Time"] = str(round(time.time() - start, 4))
    return response

# ── Global Exception Handler ──
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})

# ── Sentry (Production) ──
if settings.SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.fastapi import FastApiIntegration
    sentry_sdk.init(dsn=settings.SENTRY_DSN, integrations=[FastApiIntegration()])

# ── Routers ──
PREFIX = settings.API_V1_PREFIX
app.include_router(auth.router,        prefix=PREFIX)
app.include_router(credentials.router, prefix=PREFIX)
app.include_router(scans.router,       prefix=PREFIX)
app.include_router(billing.router,     prefix=PREFIX)
app.include_router(dashboard.router,   prefix=PREFIX)

# ── Health Check ──
@app.get("/health", tags=["System"])
async def health():
    return {"status": "ok", "app": settings.APP_NAME, "version": "2.0.0", "env": settings.APP_ENV}

@app.get("/", tags=["System"])
async def root():
    return {"message": "CloudGRC-AI API is running", "docs": "/api/docs"}

# ── DB Init on Startup ──
@app.on_event("startup")
async def startup():
    logger.info(f"Starting {settings.APP_NAME} in {settings.APP_ENV} mode")
    from backend.db.base import engine, Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables verified")

@app.on_event("shutdown")
async def shutdown():
    logger.info("Shutting down CloudGRC-AI API")
