"""Service layer for the `attributes` module."""

import uuid
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func

from app.modules.attributes.attributes_entity import Attribute
from app.modules.attributes.attributes_dto import AttributeDTO
from app.modules.attributes.attributes_dco import AttributeDCO, AttributeUpdateDCO


async def create(session: AsyncSession, data: AttributeDCO) -> AttributeDTO:
    """Create a new Attribute record."""
    entity_obj = Attribute(**data.model_dump())
    session.add(entity_obj)
    await session.flush()
    await session.refresh(entity_obj)
    return AttributeDTO.model_validate(entity_obj)


async def get_by_id(session: AsyncSession, record_id: UUID) -> AttributeDTO | None:
    """Get a Attribute by ID."""
    stmt = select(Attribute).where(Attribute.id == record_id)
    result = await session.execute(stmt)
    entity_obj = result.scalar_one_or_none()
    return AttributeDTO.model_validate(entity_obj) if entity_obj else None


async def list_all(session: AsyncSession) -> list[AttributeDTO]:
    """List all Attribute records."""
    stmt = select(Attribute)
    result = await session.execute(stmt)
    entities = result.scalars().all()
    return [AttributeDTO.model_validate(e) for e in entities]


async def update(session: AsyncSession, record_id: UUID, data: AttributeUpdateDCO) -> AttributeDTO | None:
    """Update a Attribute record."""
    stmt = select(Attribute).where(Attribute.id == record_id)
    result = await session.execute(stmt)
    entity_obj = result.scalar_one_or_none()
    if not entity_obj:
        return None
    updates = data.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(entity_obj, key, value)
    await session.flush()
    await session.refresh(entity_obj)
    return AttributeDTO.model_validate(entity_obj)


async def delete_record(session: AsyncSession, record_id: UUID) -> bool:
    """Delete a Attribute record (hard delete)."""
    stmt = select(Attribute).where(Attribute.id == record_id)
    result = await session.execute(stmt)
    entity_obj = result.scalar_one_or_none()
    if not entity_obj:
        return False
    await session.delete(entity_obj)
    await session.flush()
    return True
