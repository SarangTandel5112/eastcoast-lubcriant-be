"""Controller layer for the `products` module."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.products import products_service as service
from app.modules.products.products_dto import ProductDTO
from app.modules.products.products_dco import ProductDCO, ProductUpdateDCO


async def create(session: AsyncSession, data: ProductDCO) -> ProductDTO:
    return await service.create(session, data)


async def get_by_id(session: AsyncSession, record_id: UUID) -> ProductDTO | None:
    return await service.get_by_id(session, record_id)


async def list_all(session: AsyncSession) -> list[ProductDTO]:
    return await service.list_all(session)


async def update(session: AsyncSession, record_id: UUID, data: ProductUpdateDCO) -> ProductDTO | None:
    return await service.update(session, record_id, data)


async def delete_record(session: AsyncSession, record_id: UUID) -> bool:
    return await service.delete_record(session, record_id)
