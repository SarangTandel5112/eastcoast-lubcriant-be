from contextlib import asynccontextmanager
import time

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.core import settings, setup_logging
from app.api.v1.router import router as v1_router
from app.middleware import (
    add_request_context,
    add_exception_handlers
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Startup ──────────────────────────────────────────
    setup_logging()
    logger.info("Starting {} ...", settings.app_name)

    # ── Redis cache (optional) ───────────────────────────
    if settings.redis_url:
        try:
            from redis import asyncio as aioredis
            from fastapi_cache import FastAPICache
            from fastapi_cache.backends.redis import RedisBackend

            redis = aioredis.from_url(settings.redis_url, encoding="utf-8", decode_responses=True)
            FastAPICache.init(RedisBackend(redis), prefix="ecom-cache")
            logger.info("Redis cache initialized")
        except Exception as e:
            logger.warning("Redis not available, caching disabled | error={}", str(e))
    else:
        logger.info("Redis URL not set, caching disabled")

    yield

    # ── Shutdown ─────────────────────────────────────────
    logger.info("Shutting down...")


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    docs_url="/docs",       # Swagger UI
    redoc_url="/redoc",     # ReDoc UI
    lifespan=lifespan,
)

# ── Middleware (order matters!) ───────────────────────────────
# 1. Request context (adds request ID for tracing)
add_request_context(app)

# 2. CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Exception handlers (must be added after middleware)
add_exception_handlers(app)

# ── Routers ───────────────────────────────────────────────
app.include_router(v1_router)


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint with enhanced status information."""
    health_status = {
        "status": "ok",
        "app": settings.app_name,
        "version": "1.0.0",
        "timestamp": time.time(),
        "services": {
            "redis": settings.redis_url != "",
            "logging": True
        }
    }
    
    return health_status
