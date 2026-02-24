"""Auth model layer — async database operations for the `users` table."""

from typing import Optional
import uuid

from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.auth_dco import UserDCO
from app.modules.auth.auth_entity import UserEntity


# ── Entity ↔ DCO helpers ─────────────────────────────────────

def _entity_to_dco(entity: UserEntity) -> UserDCO:
    """Convert a SQLAlchemy entity to a domain object."""
    return UserDCO(
        id=str(entity.id),
        name=entity.name,
        email=entity.email,
        password=entity.password,
        role=entity.role,
        created_at=entity.created_at.isoformat() if entity.created_at else "",
    )


def _dco_to_entity(dco: UserDCO) -> UserEntity:
    """Convert a domain object to a new SQLAlchemy entity for INSERT."""
    return UserEntity(
        name=dco.name,
        email=dco.email,
        password=dco.password,
        role=dco.role,
    )


# ── CRUD operations ──────────────────────────────────────────

async def create_user(session: AsyncSession, dco: UserDCO) -> UserDCO:
    """Insert a new user row and return the hydrated DCO."""
    entity = _dco_to_entity(dco)
    session.add(entity)
    await session.flush()           # populate id + created_at from DB
    await session.refresh(entity)

    logger.debug("User row inserted | id={}", entity.id)
    return _entity_to_dco(entity)


async def find_user_by_email(session: AsyncSession, email: str) -> Optional[UserDCO]:
    """Lookup a user by email. Returns None if not found."""
    result = await session.execute(
        select(UserEntity).where(UserEntity.email == email)
    )
    entity = result.scalar_one_or_none()
    return _entity_to_dco(entity) if entity else None


async def find_user_by_id(session: AsyncSession, user_id: str) -> Optional[UserDCO]:
    """Lookup a user by UUID. Returns None if not found."""
    try:
        uid = uuid.UUID(user_id)
    except ValueError:
        return None

    result = await session.execute(
        select(UserEntity).where(UserEntity.id == uid)
    )
    entity = result.scalar_one_or_none()
    return _entity_to_dco(entity) if entity else None
