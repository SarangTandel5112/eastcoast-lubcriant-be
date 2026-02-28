from contextlib import asynccontextmanager
import time
from secrets import compare_digest

from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from loguru import logger

from app.core import settings, setup_logging, verify_db_connection, close_db_connection
from app.core.rate_limit import setup_rate_limiting
from app.api.v1.router import router as v1_router
from app.middleware import (
    add_request_context,
    add_exception_handlers,
    add_security_headers,
)

# HTTP Basic Auth for API documentation
security = HTTPBasic()


def verify_docs_credentials(credentials: HTTPBasicCredentials = Depends(security)) -> HTTPBasicCredentials:
    """
    Verify credentials for accessing API documentation.
    Used to protect Swagger UI and ReDoc in production.
    """
    correct_username = compare_digest(credentials.username, settings.docs_username)
    correct_password = compare_digest(credentials.password, settings.docs_password)

    if not (correct_username and correct_password):
        logger.warning(
            "Failed docs authentication attempt | username={}",
            credentials.username
        )
        raise HTTPException(
            status_code=401,
            detail="Invalid documentation credentials",
            headers={"WWW-Authenticate": "Basic"},
        )

    return credentials


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Startup ──────────────────────────────────────────
    setup_logging()
    logger.info("Starting {} ...", settings.app_name)

    # ── Database (Supabase Postgres) ──────────────────────
    db_connected = await verify_db_connection()

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

    # Store connection status for health check
    app.state.db_connected = db_connected

    yield

    # ── Shutdown ─────────────────────────────────────────
    await close_db_connection()
    logger.info("Shutting down...")


# In production, disable default docs and use custom protected routes
app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    docs_url="/docs" if settings.debug else None,  # Only expose in debug mode
    redoc_url="/redoc" if settings.debug else None,  # Only expose in debug mode
    lifespan=lifespan,
)

# ── Middleware (order matters!) ───────────────────────────────
# 1. Security headers (should be first to apply to all responses)
add_security_headers(app)

# 2. Request context (adds request ID for tracing)
add_request_context(app)

# 3. Rate limiting (protect against brute force and DDoS)
setup_rate_limiting(app)

# 4. CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],  # Explicit methods
    allow_headers=[
        "Content-Type",
        "Authorization",
        "Accept",
        "X-Request-ID",
    ],  # Only necessary headers
    expose_headers=["X-Request-ID"],  # Headers client can read
    max_age=3600,  # Cache preflight requests for 1 hour
)

# 5. Exception handlers (must be added after middleware)
add_exception_handlers(app)

# ── Routers ───────────────────────────────────────────────
app.include_router(v1_router)


# ── Protected Documentation Routes (Production) ───────────
if not settings.debug and settings.docs_password:
    @app.get("/docs", include_in_schema=False)
    async def get_documentation(credentials: HTTPBasicCredentials = Depends(verify_docs_credentials)):
        """
        Protected Swagger UI documentation.
        Requires HTTP Basic Auth in production.
        """
        return get_swagger_ui_html(
            openapi_url=app.openapi_url,
            title=f"{settings.app_name} - API Documentation",
            swagger_favicon_url="/favicon.ico"
        )

    @app.get("/redoc", include_in_schema=False)
    async def get_redoc_documentation(credentials: HTTPBasicCredentials = Depends(verify_docs_credentials)):
        """
        Protected ReDoc documentation.
        Requires HTTP Basic Auth in production.
        """
        return get_redoc_html(
            openapi_url=app.openapi_url,
            title=f"{settings.app_name} - API Documentation",
            redoc_favicon_url="/favicon.ico"
        )

    logger.info("API documentation protected with HTTP Basic Auth")


@app.get("/health", tags=["Health"])
async def health_check(request: Request):
    """Health check endpoint with enhanced status information."""
    from app.common.response import respond

    health_status = {
        "status": "ok",
        "appName": settings.app_name,
        "version": "1.0.0",
        "timestamp": time.time(),
        "services": {
            "database": getattr(app.state, "db_connected", False),
            "redis": settings.redis_url != "",
            "logging": True,
        }
    }

    return respond(
        data=health_status,
        message="System health information",
        request_id=getattr(request.state, "request_id", None)
    )
