"""Service layer for the `users` module."""

import uuid
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func

from app.modules.users.users_entity import User
from app.modules.users.users_dto import UserDTO
from app.modules.users.users_dco import UserDCO, UserUpdateDCO


async def create(session: AsyncSession, data: UserDCO) -> UserDTO:
    """Create a new User record."""
    entity_obj = User(**data.model_dump())
    session.add(entity_obj)
    await session.flush()
    await session.refresh(entity_obj)
    return UserDTO.model_validate(entity_obj)


async def get_by_id(session: AsyncSession, record_id: UUID) -> UserDTO | None:
    """Get a User by ID."""
    stmt = select(User).where(User.id == record_id, User.deleted_at.is_(None))
    result = await session.execute(stmt)
    entity_obj = result.scalar_one_or_none()
    return UserDTO.model_validate(entity_obj) if entity_obj else None


async def list_all(session: AsyncSession) -> list[UserDTO]:
    """List all User records."""
    stmt = select(User).where(User.deleted_at.is_(None))
    result = await session.execute(stmt)
    entities = result.scalars().all()
    return [UserDTO.model_validate(e) for e in entities]


async def update(session: AsyncSession, record_id: UUID, data: UserUpdateDCO) -> UserDTO | None:
    """Update a User record."""
    stmt = select(User).where(User.id == record_id, User.deleted_at.is_(None))
    result = await session.execute(stmt)
    entity_obj = result.scalar_one_or_none()
    if not entity_obj:
        return None
    updates = data.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(entity_obj, key, value)
    await session.flush()
    await session.refresh(entity_obj)
    return UserDTO.model_validate(entity_obj)


async def delete_record(session: AsyncSession, record_id: UUID) -> bool:
    """Delete a User record (hard delete)."""
    stmt = select(User).where(User.id == record_id)
    result = await session.execute(stmt)
    entity_obj = result.scalar_one_or_none()
    if not entity_obj:
        return False
    await session.delete(entity_obj)
    await session.flush()
    return True

async def soft_delete_user(session: AsyncSession, record_id: UUID) -> bool:
    """Soft-delete a User by setting deleted_at."""
    stmt = select(User).where(User.id == record_id, User.deleted_at.is_(None))
    result = await session.execute(stmt)
    entity_obj = result.scalar_one_or_none()
    if not entity_obj:
        return False
    entity_obj.deleted_at = func.now()
    await session.flush()
    return True
