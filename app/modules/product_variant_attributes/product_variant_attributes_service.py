"""Service layer for the `product_variant_attributes` module."""

import uuid
from uuid import UUID

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func

from app.modules.product_variant_attributes.product_variant_attributes_entity import ProductVariantAttribute
from app.modules.product_variant_attributes.product_variant_attributes_dto import ProductVariantAttributeDTO
from app.modules.product_variant_attributes.product_variant_attributes_dco import ProductVariantAttributeDCO


async def create(session: AsyncSession, data: ProductVariantAttributeDCO) -> ProductVariantAttributeDTO:
    """Create a new ProductVariantAttribute record."""
    entity_obj = ProductVariantAttribute(**data.model_dump())
    session.add(entity_obj)
    await session.flush()
    await session.refresh(entity_obj)
    return ProductVariantAttributeDTO.model_validate(entity_obj)


async def list_all(session: AsyncSession) -> list[ProductVariantAttributeDTO]:
    """List all ProductVariantAttribute records."""
    stmt = select(ProductVariantAttribute)
    result = await session.execute(stmt)
    entities = result.scalars().all()
    return [ProductVariantAttributeDTO.model_validate(e) for e in entities]


async def delete_record(session: AsyncSession, **kwargs) -> bool:
    """Delete a ProductVariantAttribute record by composite key."""
    stmt = delete(ProductVariantAttribute).filter_by(**kwargs)
    result = await session.execute(stmt)
    await session.flush()
    return result.rowcount > 0
