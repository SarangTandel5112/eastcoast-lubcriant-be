"""Service layer for the `product_applications` module."""

import uuid
from uuid import UUID

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func

from app.modules.product_applications.product_applications_entity import ProductApplication
from app.modules.product_applications.product_applications_dto import ProductApplicationDTO
from app.modules.product_applications.product_applications_dco import ProductApplicationDCO


async def create(session: AsyncSession, data: ProductApplicationDCO) -> ProductApplicationDTO:
    """Create a new ProductApplication record."""
    entity_obj = ProductApplication(**data.model_dump())
    session.add(entity_obj)
    await session.flush()
    await session.refresh(entity_obj)
    return ProductApplicationDTO.model_validate(entity_obj)


async def list_all(session: AsyncSession) -> list[ProductApplicationDTO]:
    """List all ProductApplication records."""
    stmt = select(ProductApplication)
    result = await session.execute(stmt)
    entities = result.scalars().all()
    return [ProductApplicationDTO.model_validate(e) for e in entities]


async def delete_record(session: AsyncSession, **kwargs) -> bool:
    """Delete a ProductApplication record by composite key."""
    stmt = delete(ProductApplication).filter_by(**kwargs)
    result = await session.execute(stmt)
    await session.flush()
    return result.rowcount > 0
