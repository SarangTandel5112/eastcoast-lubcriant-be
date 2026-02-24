"""Service layer for the `product_types` module."""

import uuid
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func

from app.modules.product_types.product_types_entity import ProductType
from app.modules.product_types.product_types_dto import ProductTypeDTO
from app.modules.product_types.product_types_dco import ProductTypeDCO, ProductTypeUpdateDCO


async def create(session: AsyncSession, data: ProductTypeDCO) -> ProductTypeDTO:
    """Create a new ProductType record."""
    entity_obj = ProductType(**data.model_dump())
    session.add(entity_obj)
    await session.flush()
    await session.refresh(entity_obj)
    return ProductTypeDTO.model_validate(entity_obj)


async def get_by_id(session: AsyncSession, record_id: UUID) -> ProductTypeDTO | None:
    """Get a ProductType by ID."""
    stmt = select(ProductType).where(ProductType.id == record_id, ProductType.deleted_at.is_(None))
    result = await session.execute(stmt)
    entity_obj = result.scalar_one_or_none()
    return ProductTypeDTO.model_validate(entity_obj) if entity_obj else None


async def list_all(session: AsyncSession) -> list[ProductTypeDTO]:
    """List all ProductType records."""
    stmt = select(ProductType).where(ProductType.deleted_at.is_(None))
    result = await session.execute(stmt)
    entities = result.scalars().all()
    return [ProductTypeDTO.model_validate(e) for e in entities]


async def update(session: AsyncSession, record_id: UUID, data: ProductTypeUpdateDCO) -> ProductTypeDTO | None:
    """Update a ProductType record."""
    stmt = select(ProductType).where(ProductType.id == record_id, ProductType.deleted_at.is_(None))
    result = await session.execute(stmt)
    entity_obj = result.scalar_one_or_none()
    if not entity_obj:
        return None
    updates = data.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(entity_obj, key, value)
    await session.flush()
    await session.refresh(entity_obj)
    return ProductTypeDTO.model_validate(entity_obj)


async def delete_record(session: AsyncSession, record_id: UUID) -> bool:
    """Delete a ProductType record (hard delete)."""
    stmt = select(ProductType).where(ProductType.id == record_id)
    result = await session.execute(stmt)
    entity_obj = result.scalar_one_or_none()
    if not entity_obj:
        return False
    await session.delete(entity_obj)
    await session.flush()
    return True

async def soft_delete_product_type(session: AsyncSession, record_id: UUID) -> bool:
    """Soft-delete a ProductType by setting deleted_at."""
    stmt = select(ProductType).where(ProductType.id == record_id, ProductType.deleted_at.is_(None))
    result = await session.execute(stmt)
    entity_obj = result.scalar_one_or_none()
    if not entity_obj:
        return False
    entity_obj.deleted_at = func.now()
    await session.flush()
    return True
