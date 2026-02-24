"""Service layer for the `variant_images` module."""

import uuid
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func

from app.modules.variant_images.variant_images_entity import VariantImage
from app.modules.variant_images.variant_images_dto import VariantImageDTO
from app.modules.variant_images.variant_images_dco import VariantImageDCO, VariantImageUpdateDCO


async def create(session: AsyncSession, data: VariantImageDCO) -> VariantImageDTO:
    """Create a new VariantImage record."""
    entity_obj = VariantImage(**data.model_dump())
    session.add(entity_obj)
    await session.flush()
    await session.refresh(entity_obj)
    return VariantImageDTO.model_validate(entity_obj)


async def get_by_id(session: AsyncSession, record_id: UUID) -> VariantImageDTO | None:
    """Get a VariantImage by ID."""
    stmt = select(VariantImage).where(VariantImage.id == record_id)
    result = await session.execute(stmt)
    entity_obj = result.scalar_one_or_none()
    return VariantImageDTO.model_validate(entity_obj) if entity_obj else None


async def list_all(session: AsyncSession) -> list[VariantImageDTO]:
    """List all VariantImage records."""
    stmt = select(VariantImage)
    result = await session.execute(stmt)
    entities = result.scalars().all()
    return [VariantImageDTO.model_validate(e) for e in entities]


async def update(session: AsyncSession, record_id: UUID, data: VariantImageUpdateDCO) -> VariantImageDTO | None:
    """Update a VariantImage record."""
    stmt = select(VariantImage).where(VariantImage.id == record_id)
    result = await session.execute(stmt)
    entity_obj = result.scalar_one_or_none()
    if not entity_obj:
        return None
    updates = data.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(entity_obj, key, value)
    await session.flush()
    await session.refresh(entity_obj)
    return VariantImageDTO.model_validate(entity_obj)


async def delete_record(session: AsyncSession, record_id: UUID) -> bool:
    """Delete a VariantImage record (hard delete)."""
    stmt = select(VariantImage).where(VariantImage.id == record_id)
    result = await session.execute(stmt)
    entity_obj = result.scalar_one_or_none()
    if not entity_obj:
        return False
    await session.delete(entity_obj)
    await session.flush()
    return True
