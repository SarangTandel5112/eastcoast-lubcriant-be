"""Service layer for the `product_variant_standards` module."""

import uuid
from uuid import UUID

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func

from app.modules.product_variant_standards.product_variant_standards_entity import ProductVariantStandard
from app.modules.product_variant_standards.product_variant_standards_dto import ProductVariantStandardDTO
from app.modules.product_variant_standards.product_variant_standards_dco import ProductVariantStandardDCO


async def create(session: AsyncSession, data: ProductVariantStandardDCO) -> ProductVariantStandardDTO:
    """Create a new ProductVariantStandard record."""
    entity_obj = ProductVariantStandard(**data.model_dump())
    session.add(entity_obj)
    await session.flush()
    await session.refresh(entity_obj)
    return ProductVariantStandardDTO.model_validate(entity_obj)


async def list_all(session: AsyncSession) -> list[ProductVariantStandardDTO]:
    """List all ProductVariantStandard records."""
    stmt = select(ProductVariantStandard)
    result = await session.execute(stmt)
    entities = result.scalars().all()
    return [ProductVariantStandardDTO.model_validate(e) for e in entities]


async def delete_record(session: AsyncSession, **kwargs) -> bool:
    """Delete a ProductVariantStandard record by composite key."""
    stmt = delete(ProductVariantStandard).filter_by(**kwargs)
    result = await session.execute(stmt)
    await session.flush()
    return result.rowcount > 0
