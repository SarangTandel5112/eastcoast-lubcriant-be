"""Service layer for the `product_images` module."""

import uuid
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func

from app.modules.product_images.product_images_entity import ProductImage
from app.modules.product_images.product_images_dto import ProductImageDTO
from app.modules.product_images.product_images_dco import ProductImageDCO, ProductImageUpdateDCO


async def create(session: AsyncSession, data: ProductImageDCO) -> ProductImageDTO:
    """Create a new ProductImage record."""
    entity_obj = ProductImage(**data.model_dump())
    session.add(entity_obj)
    await session.flush()
    await session.refresh(entity_obj)
    return ProductImageDTO.model_validate(entity_obj)


async def get_by_id(session: AsyncSession, record_id: UUID) -> ProductImageDTO | None:
    """Get a ProductImage by ID."""
    stmt = select(ProductImage).where(ProductImage.id == record_id)
    result = await session.execute(stmt)
    entity_obj = result.scalar_one_or_none()
    return ProductImageDTO.model_validate(entity_obj) if entity_obj else None


async def list_all(session: AsyncSession) -> list[ProductImageDTO]:
    """List all ProductImage records."""
    stmt = select(ProductImage)
    result = await session.execute(stmt)
    entities = result.scalars().all()
    return [ProductImageDTO.model_validate(e) for e in entities]


async def update(session: AsyncSession, record_id: UUID, data: ProductImageUpdateDCO) -> ProductImageDTO | None:
    """Update a ProductImage record."""
    stmt = select(ProductImage).where(ProductImage.id == record_id)
    result = await session.execute(stmt)
    entity_obj = result.scalar_one_or_none()
    if not entity_obj:
        return None
    updates = data.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(entity_obj, key, value)
    await session.flush()
    await session.refresh(entity_obj)
    return ProductImageDTO.model_validate(entity_obj)


async def delete_record(session: AsyncSession, record_id: UUID) -> bool:
    """Delete a ProductImage record (hard delete)."""
    stmt = select(ProductImage).where(ProductImage.id == record_id)
    result = await session.execute(stmt)
    entity_obj = result.scalar_one_or_none()
    if not entity_obj:
        return False
    await session.delete(entity_obj)
    await session.flush()
    return True
