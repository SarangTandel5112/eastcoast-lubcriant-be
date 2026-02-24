"""Service layer for the `product_variants` module."""

import uuid
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func

from app.modules.product_variants.product_variants_entity import ProductVariant
from app.modules.product_variants.product_variants_dto import ProductVariantDTO
from app.modules.product_variants.product_variants_dco import ProductVariantDCO, ProductVariantUpdateDCO


async def create(session: AsyncSession, data: ProductVariantDCO) -> ProductVariantDTO:
    """Create a new ProductVariant record."""
    entity_obj = ProductVariant(**data.model_dump())
    session.add(entity_obj)
    await session.flush()
    await session.refresh(entity_obj)
    return ProductVariantDTO.model_validate(entity_obj)


async def get_by_id(session: AsyncSession, record_id: UUID) -> ProductVariantDTO | None:
    """Get a ProductVariant by ID."""
    stmt = select(ProductVariant).where(ProductVariant.id == record_id, ProductVariant.deleted_at.is_(None))
    result = await session.execute(stmt)
    entity_obj = result.scalar_one_or_none()
    return ProductVariantDTO.model_validate(entity_obj) if entity_obj else None


async def list_all(session: AsyncSession) -> list[ProductVariantDTO]:
    """List all ProductVariant records."""
    stmt = select(ProductVariant).where(ProductVariant.deleted_at.is_(None))
    result = await session.execute(stmt)
    entities = result.scalars().all()
    return [ProductVariantDTO.model_validate(e) for e in entities]


async def update(session: AsyncSession, record_id: UUID, data: ProductVariantUpdateDCO) -> ProductVariantDTO | None:
    """Update a ProductVariant record."""
    stmt = select(ProductVariant).where(ProductVariant.id == record_id, ProductVariant.deleted_at.is_(None))
    result = await session.execute(stmt)
    entity_obj = result.scalar_one_or_none()
    if not entity_obj:
        return None
    updates = data.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(entity_obj, key, value)
    await session.flush()
    await session.refresh(entity_obj)
    return ProductVariantDTO.model_validate(entity_obj)


async def delete_record(session: AsyncSession, record_id: UUID) -> bool:
    """Delete a ProductVariant record (hard delete)."""
    stmt = select(ProductVariant).where(ProductVariant.id == record_id)
    result = await session.execute(stmt)
    entity_obj = result.scalar_one_or_none()
    if not entity_obj:
        return False
    await session.delete(entity_obj)
    await session.flush()
    return True

async def soft_delete_product_variant(session: AsyncSession, record_id: UUID) -> bool:
    """Soft-delete a ProductVariant by setting deleted_at."""
    stmt = select(ProductVariant).where(ProductVariant.id == record_id, ProductVariant.deleted_at.is_(None))
    result = await session.execute(stmt)
    entity_obj = result.scalar_one_or_none()
    if not entity_obj:
        return False
    entity_obj.deleted_at = func.now()
    await session.flush()
    return True
