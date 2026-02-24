"""Service layer for the `products` module."""

import uuid
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func

from app.modules.products.products_entity import Product
from app.modules.products.products_dto import ProductDTO
from app.modules.products.products_dco import ProductDCO, ProductUpdateDCO


async def create(session: AsyncSession, data: ProductDCO) -> ProductDTO:
    """Create a new Product record."""
    entity_obj = Product(**data.model_dump())
    session.add(entity_obj)
    await session.flush()
    await session.refresh(entity_obj)
    return ProductDTO.model_validate(entity_obj)


async def get_by_id(session: AsyncSession, record_id: UUID) -> ProductDTO | None:
    """Get a Product by ID."""
    stmt = select(Product).where(Product.id == record_id, Product.deleted_at.is_(None))
    result = await session.execute(stmt)
    entity_obj = result.scalar_one_or_none()
    return ProductDTO.model_validate(entity_obj) if entity_obj else None


async def list_all(session: AsyncSession) -> list[ProductDTO]:
    """List all Product records."""
    stmt = select(Product).where(Product.deleted_at.is_(None))
    result = await session.execute(stmt)
    entities = result.scalars().all()
    return [ProductDTO.model_validate(e) for e in entities]


async def update(session: AsyncSession, record_id: UUID, data: ProductUpdateDCO) -> ProductDTO | None:
    """Update a Product record."""
    stmt = select(Product).where(Product.id == record_id, Product.deleted_at.is_(None))
    result = await session.execute(stmt)
    entity_obj = result.scalar_one_or_none()
    if not entity_obj:
        return None
    updates = data.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(entity_obj, key, value)
    await session.flush()
    await session.refresh(entity_obj)
    return ProductDTO.model_validate(entity_obj)


async def delete_record(session: AsyncSession, record_id: UUID) -> bool:
    """Delete a Product record (hard delete)."""
    stmt = select(Product).where(Product.id == record_id)
    result = await session.execute(stmt)
    entity_obj = result.scalar_one_or_none()
    if not entity_obj:
        return False
    await session.delete(entity_obj)
    await session.flush()
    return True

async def soft_delete_product(session: AsyncSession, record_id: UUID) -> bool:
    """Soft-delete a Product by setting deleted_at."""
    stmt = select(Product).where(Product.id == record_id, Product.deleted_at.is_(None))
    result = await session.execute(stmt)
    entity_obj = result.scalar_one_or_none()
    if not entity_obj:
        return False
    entity_obj.deleted_at = func.now()
    await session.flush()
    return True
