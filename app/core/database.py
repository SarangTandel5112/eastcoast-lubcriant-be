"""Async SQLAlchemy engine, session factory, and connection management for Supabase Postgres."""

import importlib
import os
from urllib.parse import urlparse
from pathlib import Path

from loguru import logger
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy import text

from app.core.config import settings
from app.common.base_entity import Base


# ── Engine ───────────────────────────────────────────────────
def _build_engine():
    """
    Build the async engine with enterprise-grade settings for Supabase (Postgres).
    Uses 'postgresql+asyncpg' for non-blocking I/O.
    """
    if not settings.database_url:
        logger.warning("DATABASE_URL not set — database features disabled")
        return None

    # Handle standard 'postgresql://' by converting to '+asyncpg'
    db_url = settings.database_url
    if db_url.startswith("postgresql://") and "+asyncpg" not in db_url:
        db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)

    parsed = urlparse(db_url)
    
    # SSL: Required for cloud databases (Supabase), optional for local
    is_local = parsed.hostname in ("localhost", "127.0.0.1", "db", "ecommerce_db") or (parsed.hostname and parsed.hostname.startswith("172."))
    
    connect_args = {
        "server_settings": {
            "application_name": settings.app_name
        }
    }
    
    if not is_local:
        connect_args["ssl"] = "require"

    engine = create_async_engine(
        db_url,
        echo=settings.debug,
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,
        pool_recycle=300,
        connect_args=connect_args,
    )

    logger.debug(
        "Database engine initialized | host={} port={} db={} ssl={}",
        parsed.hostname,
        parsed.port,
        parsed.path.lstrip("/"),
        "disabled (local)" if is_local else "require"
    )
    return engine


async_engine = _build_engine()


def get_session_factory():
    """Returns the sessionmaker if engine exists."""
    if not async_engine:
        return None
    return async_sessionmaker(
        bind=async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )


AsyncSessionLocal = get_session_factory()


# ── Automatic Migration System ───────────────────────────────

def _import_all_entities():
    """Recursively import canonical modules to register entities with Base."""
    import app.modules as modules
    base_path = Path(modules.__path__[0])
    
    EXCLUDED_DIRS = {"order", "product"}

    for path in base_path.iterdir():
        if path.is_dir() and path.name not in EXCLUDED_DIRS:
            for file in path.glob("*_entity.py"):
                module_name = f"app.modules.{path.name}.{file.stem}"
                try:
                    importlib.import_module(module_name)
                    logger.debug("Auto-discovered entity from module: {}", module_name)
                except Exception as e:
                    logger.error("Failed to auto-import {}: {}", module_name, e)


async def init_db_schema() -> None:
    """
    Automatically synchronize the database schema with the Python models.
    This replaces manual migration files with a robust code-managed solution.
    """
    if async_engine is None:
        return

    logger.info("Starting automatic database schema synchronization...")
    
    # 1. Discover all entities
    _import_all_entities()

    # 2. Synchronize (Create tables if not exist)
    try:
        async with async_engine.begin() as conn:
            # We use run_sync because metadata.create_all is a synchronous method 
            # that needs to run inside a greenlet in SQLAlchemy Async.
            await conn.run_sync(Base.metadata.create_all)
        
        logger.info("✅ Database schema is up-to-date (Automatic Sync Complete)")
    except Exception as exc:
        logger.error("❌ Failed to synchronize database schema: {}", exc)


# ── Dependency ───────────────────────────────────────────────
async def get_db_session():
    """FastAPI dependency that yields an async DB session."""
    if AsyncSessionLocal is None:
        raise RuntimeError(
            "Database is not configured. Set DATABASE_URL in your .env file."
        )

    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise


# ── Lifecycle helpers ─────────
async def verify_db_connection() -> bool:
    """Run a heartbeat check. Returns True on success."""
    if async_engine is None:
        logger.warning("⚠️  Database not configured — skipping connection check")
        return False

    try:
        async with async_engine.connect() as conn:
            result = await conn.execute(text("SELECT current_database()"))
            db_name = result.scalar()
            logger.info("✅ Database connection verified | connected_to={}", db_name)
        return True

    except Exception as exc:
        logger.error("❌ Database connection failed: {}", str(exc))
        return False


async def close_db_connection() -> None:
    """Dispose the connection pool cleanly."""
    if async_engine is not None:
        await async_engine.dispose()
        logger.info("Database connection pool closed")
