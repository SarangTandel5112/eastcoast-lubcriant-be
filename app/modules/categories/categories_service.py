"""Service layer for the `categories` module."""

import uuid
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func

from app.modules.categories.categories_entity import Category
from app.modules.categories.categories_dto import CategoryDTO
from app.modules.categories.categories_dco import CategoryDCO, CategoryUpdateDCO


async def create(session: AsyncSession, data: CategoryDCO) -> CategoryDTO:
    """Create a new Category record."""
    entity_obj = Category(**data.model_dump())
    session.add(entity_obj)
    await session.flush()
    await session.refresh(entity_obj)
    return CategoryDTO.model_validate(entity_obj)


async def get_by_id(session: AsyncSession, record_id: UUID) -> CategoryDTO | None:
    """Get a Category by ID."""
    stmt = select(Category).where(Category.id == record_id, Category.deleted_at.is_(None))
    result = await session.execute(stmt)
    entity_obj = result.scalar_one_or_none()
    return CategoryDTO.model_validate(entity_obj) if entity_obj else None


async def list_all(session: AsyncSession) -> list[CategoryDTO]:
    """List all Category records."""
    stmt = select(Category).where(Category.deleted_at.is_(None))
    result = await session.execute(stmt)
    entities = result.scalars().all()
    return [CategoryDTO.model_validate(e) for e in entities]


async def update(session: AsyncSession, record_id: UUID, data: CategoryUpdateDCO) -> CategoryDTO | None:
    """Update a Category record."""
    stmt = select(Category).where(Category.id == record_id, Category.deleted_at.is_(None))
    result = await session.execute(stmt)
    entity_obj = result.scalar_one_or_none()
    if not entity_obj:
        return None
    updates = data.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(entity_obj, key, value)
    await session.flush()
    await session.refresh(entity_obj)
    return CategoryDTO.model_validate(entity_obj)


async def delete_record(session: AsyncSession, record_id: UUID) -> bool:
    """Delete a Category record (hard delete)."""
    stmt = select(Category).where(Category.id == record_id)
    result = await session.execute(stmt)
    entity_obj = result.scalar_one_or_none()
    if not entity_obj:
        return False
    await session.delete(entity_obj)
    await session.flush()
    return True

async def soft_delete_categories(session: AsyncSession, record_id: UUID) -> bool:
    """Soft-delete a Category by setting deleted_at."""
    stmt = select(Category).where(Category.id == record_id, Category.deleted_at.is_(None))
    result = await session.execute(stmt)
    entity_obj = result.scalar_one_or_none()
    if not entity_obj:
        return False
    entity_obj.deleted_at = func.now()
    await session.flush()
    return True
