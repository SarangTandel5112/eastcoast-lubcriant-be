"""Alembic async migration environment.

Reads DATABASE_URL from .env / environment, imports all entity models,
and runs migrations asynchronously using asyncpg.
"""

import asyncio
import importlib
import os
import pkgutil
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config
from dotenv import load_dotenv

# Load .env so DATABASE_URL is available
load_dotenv()

# Alembic Config object
config = context.config

# Override sqlalchemy.url from environment variable
database_url = os.getenv("DATABASE_URL", "")
if database_url:
    # Handle 'postgresql://' -> 'postgresql+asyncpg://' for alembic as well
    if database_url.startswith("postgresql://") and "+asyncpg" not in database_url:
        database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    config.set_main_option("sqlalchemy.url", database_url)

# Set up Python logging from alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

from app.common.base_entity import Base

def import_all_entities():
    """Recursively import canonical modules to register entities with Base."""
    import app.modules as modules
    from pathlib import Path

    base_path = Path(modules.__path__[0])
    
    # Exclude specifically identified duplicate/legacy folders
    EXCLUDED_DIRS = {"order", "product"}

    for path in base_path.iterdir():
        if path.is_dir() and path.name not in EXCLUDED_DIRS:
            # Look for any .py files in the module that might contain entities
            # Usually they end with _entity.py
            for file in path.glob("*_entity.py"):
                module_name = f"app.modules.{path.name}.{file.stem}"
                try:
                    importlib.import_module(module_name)
                except Exception as e:
                    print(f"Failed to import {module_name}: {e}")

# Trigger discovery
import_all_entities()

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection) -> None:
    """Helper to configure context and run within a connection."""
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run migrations in 'online' mode using an async engine."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Entry point for online migrations."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
