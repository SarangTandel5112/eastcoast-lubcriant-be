"""Service layer for the `standards` module."""

import uuid
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func

from app.modules.standards.standards_entity import Standard
from app.modules.standards.standards_dto import StandardDTO
from app.modules.standards.standards_dco import StandardDCO, StandardUpdateDCO


async def create(session: AsyncSession, data: StandardDCO) -> StandardDTO:
    """Create a new Standard record."""
    entity_obj = Standard(**data.model_dump())
    session.add(entity_obj)
    await session.flush()
    await session.refresh(entity_obj)
    return StandardDTO.model_validate(entity_obj)


async def get_by_id(session: AsyncSession, record_id: UUID) -> StandardDTO | None:
    """Get a Standard by ID."""
    stmt = select(Standard).where(Standard.id == record_id)
    result = await session.execute(stmt)
    entity_obj = result.scalar_one_or_none()
    return StandardDTO.model_validate(entity_obj) if entity_obj else None


async def list_all(session: AsyncSession) -> list[StandardDTO]:
    """List all Standard records."""
    stmt = select(Standard)
    result = await session.execute(stmt)
    entities = result.scalars().all()
    return [StandardDTO.model_validate(e) for e in entities]


async def update(session: AsyncSession, record_id: UUID, data: StandardUpdateDCO) -> StandardDTO | None:
    """Update a Standard record."""
    stmt = select(Standard).where(Standard.id == record_id)
    result = await session.execute(stmt)
    entity_obj = result.scalar_one_or_none()
    if not entity_obj:
        return None
    updates = data.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(entity_obj, key, value)
    await session.flush()
    await session.refresh(entity_obj)
    return StandardDTO.model_validate(entity_obj)


async def delete_record(session: AsyncSession, record_id: UUID) -> bool:
    """Delete a Standard record (hard delete)."""
    stmt = select(Standard).where(Standard.id == record_id)
    result = await session.execute(stmt)
    entity_obj = result.scalar_one_or_none()
    if not entity_obj:
        return False
    await session.delete(entity_obj)
    await session.flush()
    return True
