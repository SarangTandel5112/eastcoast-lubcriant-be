"""Service layer for the `brands` module."""

import uuid
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func

from app.modules.brands.brands_entity import Brand
from app.modules.brands.brands_dto import BrandDTO
from app.modules.brands.brands_dco import BrandDCO, BrandUpdateDCO


async def create(session: AsyncSession, data: BrandDCO) -> BrandDTO:
    """Create a new Brand record."""
    entity_obj = Brand(**data.model_dump())
    session.add(entity_obj)
    await session.flush()
    await session.refresh(entity_obj)
    return BrandDTO.model_validate(entity_obj)


async def get_by_id(session: AsyncSession, record_id: UUID) -> BrandDTO | None:
    """Get a Brand by ID."""
    stmt = select(Brand).where(Brand.id == record_id, Brand.deleted_at.is_(None))
    result = await session.execute(stmt)
    entity_obj = result.scalar_one_or_none()
    return BrandDTO.model_validate(entity_obj) if entity_obj else None


async def list_all(session: AsyncSession) -> list[BrandDTO]:
    """List all Brand records."""
    stmt = select(Brand).where(Brand.deleted_at.is_(None))
    result = await session.execute(stmt)
    entities = result.scalars().all()
    return [BrandDTO.model_validate(e) for e in entities]


async def update(session: AsyncSession, record_id: UUID, data: BrandUpdateDCO) -> BrandDTO | None:
    """Update a Brand record."""
    stmt = select(Brand).where(Brand.id == record_id, Brand.deleted_at.is_(None))
    result = await session.execute(stmt)
    entity_obj = result.scalar_one_or_none()
    if not entity_obj:
        return None
    updates = data.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(entity_obj, key, value)
    await session.flush()
    await session.refresh(entity_obj)
    return BrandDTO.model_validate(entity_obj)


async def delete_record(session: AsyncSession, record_id: UUID) -> bool:
    """Delete a Brand record (hard delete)."""
    stmt = select(Brand).where(Brand.id == record_id)
    result = await session.execute(stmt)
    entity_obj = result.scalar_one_or_none()
    if not entity_obj:
        return False
    await session.delete(entity_obj)
    await session.flush()
    return True

async def soft_delete_brand(session: AsyncSession, record_id: UUID) -> bool:
    """Soft-delete a Brand by setting deleted_at."""
    stmt = select(Brand).where(Brand.id == record_id, Brand.deleted_at.is_(None))
    result = await session.execute(stmt)
    entity_obj = result.scalar_one_or_none()
    if not entity_obj:
        return False
    entity_obj.deleted_at = func.now()
    await session.flush()
    return True
