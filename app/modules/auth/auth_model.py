"""Auth model layer — async database operations for the `users` table."""

from typing import Optional
import uuid
from datetime import datetime, timezone

from loguru import logger
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.auth_dco import UserDCO
from app.modules.auth.auth_entity import UserEntity


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)

def _entity_to_dco(entity: UserEntity) -> UserDCO:
    """Convert a SQLAlchemy entity to a domain object."""
    return UserDCO(
        id=str(entity.id),
        role=entity.role,
        business_name=entity.business_name,
        email=entity.email,
        password_hash=entity.password_hash,
        province=entity.province,
        contact_name=entity.contact_name,
        phone=entity.phone,
        is_active=entity.is_active,
        last_login_at=entity.last_login_at.isoformat() if entity.last_login_at else None,
        created_at=entity.created_at.isoformat() if entity.created_at else "",
        updated_at=entity.updated_at.isoformat() if entity.updated_at else "",
        deleted_at=entity.deleted_at.isoformat() if entity.deleted_at else None,
        current_refresh_jti=entity.current_refresh_jti,
    )

def _dco_to_entity(dco: UserDCO) -> UserEntity:
    """Convert a domain object to a new SQLAlchemy entity for INSERT."""
    return UserEntity(
        role=dco.role,
        business_name=dco.business_name,
        email=dco.email,
        password_hash=dco.password_hash,
        province=dco.province,
        contact_name=dco.contact_name,
        phone=dco.phone,
        is_active=dco.is_active,
    )

async def create_user(session: AsyncSession, dco: UserDCO) -> UserDCO:
    """Insert a new user row and return the hydrated DCO."""
    entity = _dco_to_entity(dco)
    session.add(entity)
    await session.flush()           # populate id + created_at from DB
    await session.refresh(entity)

    logger.debug("User row inserted | id={}", entity.id)
    return _entity_to_dco(entity)

async def find_user_by_email(session: AsyncSession, email: str, include_deleted: bool = False) -> Optional[UserDCO]:
    """Lookup a user by email. Returns None if not found."""
    stmt = select(UserEntity).where(UserEntity.email == email)
    if not include_deleted:
        stmt = stmt.where(UserEntity.deleted_at.is_(None))
        
    result = await session.execute(stmt)
    entity = result.scalar_one_or_none()
    return _entity_to_dco(entity) if entity else None

async def find_user_by_id(session: AsyncSession, user_id: str, include_deleted: bool = False) -> Optional[UserDCO]:
    """Lookup a user by UUID. Returns None if not found."""
    try:
        uid = uuid.UUID(user_id)
    except ValueError:
        return None

    stmt = select(UserEntity).where(UserEntity.id == uid)
    if not include_deleted:
        stmt = stmt.where(UserEntity.deleted_at.is_(None))

    result = await session.execute(stmt)
    entity = result.scalar_one_or_none()
    return _entity_to_dco(entity) if entity else None

async def find_users_by_phone(session: AsyncSession, phone: str, include_deleted: bool = False) -> list[UserDCO]:
    stmt = select(UserEntity).where(UserEntity.phone == phone)
    if not include_deleted:
        stmt = stmt.where(UserEntity.deleted_at.is_(None))
        
    result = await session.execute(stmt)
    entities = result.scalars().all()
    return [_entity_to_dco(e) for e in entities]

async def list_users(session: AsyncSession, role: str | None = None, is_active: bool | None = None) -> list[UserDCO]:
    stmt = select(UserEntity).where(UserEntity.deleted_at.is_(None))
    
    if role is not None:
        stmt = stmt.where(UserEntity.role == role)
    if is_active is not None:
        stmt = stmt.where(UserEntity.is_active == is_active)
        
    stmt = stmt.order_by(UserEntity.created_at.desc())
        
    result = await session.execute(stmt)
    entities = result.scalars().all()
    return [_entity_to_dco(e) for e in entities]

async def update_user(session: AsyncSession, user_id: str, updates: dict) -> Optional[UserDCO]:
    try:
        uid = uuid.UUID(user_id)
    except ValueError:
        return None

    stmt = select(UserEntity).where(UserEntity.id == uid, UserEntity.deleted_at.is_(None))
    result = await session.execute(stmt)
    entity = result.scalar_one_or_none()
    if not entity:
        return None

    updates.pop("email", None) # prevent email change
    
    for key, value in updates.items():
        if hasattr(entity, key):
            setattr(entity, key, value)

    await session.flush()
    await session.refresh(entity)
    return _entity_to_dco(entity)

async def set_last_login(session: AsyncSession, user_id: str) -> Optional[UserDCO]:
    return await update_user(session, user_id, {"last_login_at": _utc_now()})

async def set_current_refresh_jti(session: AsyncSession, user_id: str, refresh_jti: str | None) -> Optional[UserDCO]:
    return await update_user(session, user_id, {"current_refresh_jti": refresh_jti})

async def soft_delete_user(session: AsyncSession, user_id: str) -> bool:
    try:
        uid = uuid.UUID(user_id)
    except ValueError:
        return False

    stmt = select(UserEntity).where(UserEntity.id == uid, UserEntity.deleted_at.is_(None))
    result = await session.execute(stmt)
    entity = result.scalar_one_or_none()
    
    if not entity:
        return False

    entity.deleted_at = _utc_now()
    entity.is_active = False
    entity.current_refresh_jti = None
    
    await session.flush()
    return True
