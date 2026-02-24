"""Controller layer for the `categories` module."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.categories import categories_service as service
from app.modules.categories.categories_dto import CategoryDTO
from app.modules.categories.categories_dco import CategoryDCO, CategoryUpdateDCO


async def create(session: AsyncSession, data: CategoryDCO) -> CategoryDTO:
    return await service.create(session, data)


async def get_by_id(session: AsyncSession, record_id: UUID) -> CategoryDTO | None:
    return await service.get_by_id(session, record_id)


async def list_all(session: AsyncSession) -> list[CategoryDTO]:
    return await service.list_all(session)


async def update(session: AsyncSession, record_id: UUID, data: CategoryUpdateDCO) -> CategoryDTO | None:
    return await service.update(session, record_id, data)


async def delete_record(session: AsyncSession, record_id: UUID) -> bool:
    return await service.delete_record(session, record_id)
