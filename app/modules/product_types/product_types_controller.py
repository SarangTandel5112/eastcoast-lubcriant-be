"""Controller layer for the `product_types` module."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.product_types import product_types_service as service
from app.modules.product_types.product_types_dto import ProductTypeDTO
from app.modules.product_types.product_types_dco import ProductTypeDCO, ProductTypeUpdateDCO


async def create(session: AsyncSession, data: ProductTypeDCO) -> ProductTypeDTO:
    return await service.create(session, data)


async def get_by_id(session: AsyncSession, record_id: UUID) -> ProductTypeDTO | None:
    return await service.get_by_id(session, record_id)


async def list_all(session: AsyncSession) -> list[ProductTypeDTO]:
    return await service.list_all(session)


async def update(session: AsyncSession, record_id: UUID, data: ProductTypeUpdateDCO) -> ProductTypeDTO | None:
    return await service.update(session, record_id, data)


async def delete_record(session: AsyncSession, record_id: UUID) -> bool:
    return await service.delete_record(session, record_id)
