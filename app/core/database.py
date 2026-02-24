"""Async SQLAlchemy engine, session factory, and connection management for Supabase Postgres."""

from urllib.parse import urlparse

from loguru import logger
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy import text

from app.core.config import settings


# ── Engine ───────────────────────────────────────────────────
def _build_engine():
    """Build the async engine only if DATABASE_URL is configured."""
    if not settings.database_url:
        logger.warning("DATABASE_URL not set — database features disabled")
        return None

    engine = create_async_engine(
        settings.database_url,
        echo=settings.debug,          # log SQL in debug mode
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,           # verify connections before checkout
        pool_recycle=300,             # recycle connections every 5 min
    )

    parsed = urlparse(settings.database_url)
    logger.info(
        "Database engine created | host={} port={} db={} pool_size={} max_overflow={}",
        parsed.hostname,
        parsed.port,
        parsed.path.lstrip("/"),
        5,
        10,
    )
    return engine


async_engine = _build_engine()

AsyncSessionLocal = (
    async_sessionmaker(
        bind=async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    if async_engine
    else None
)


# ── Dependency ───────────────────────────────────────────────
async def get_db_session():
    """FastAPI dependency that yields an async DB session.

    Usage in a route:
        @router.get("/items")
        async def list_items(db: AsyncSession = Depends(get_db_session)):
            ...
    """
    if AsyncSessionLocal is None:
        raise RuntimeError(
            "Database is not configured. Set DATABASE_URL in your .env file."
        )

    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


# ── Lifecycle helpers (called from main.py lifespan) ─────────
async def verify_db_connection() -> bool:
    """Run a SELECT 1 probe and log the result. Returns True on success."""
    if async_engine is None:
        logger.warning("⚠️  Database not configured — skipping connection check")
        return False

    try:
        async with async_engine.connect() as conn:
            await conn.execute(text("SELECT 1"))

        parsed = urlparse(settings.database_url)
        logger.info(
            "✅ Database connected | host={} port={} db={}",
            parsed.hostname,
            parsed.port,
            parsed.path.lstrip("/"),
        )
        return True

    except Exception as exc:
        logger.error("❌ Database connection failed | error={}", str(exc))
        return False


async def close_db_connection() -> None:
    """Dispose the connection pool cleanly."""
    if async_engine is not None:
        await async_engine.dispose()
        logger.info("Database connection pool closed")
