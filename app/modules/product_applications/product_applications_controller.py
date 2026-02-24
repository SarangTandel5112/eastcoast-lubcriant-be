"""Controller layer for the `product_applications` module."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.product_applications import product_applications_service as service
from app.modules.product_applications.product_applications_dto import ProductApplicationDTO
from app.modules.product_applications.product_applications_dco import ProductApplicationDCO


async def create(session: AsyncSession, data: ProductApplicationDCO) -> ProductApplicationDTO:
    return await service.create(session, data)


async def list_all(session: AsyncSession) -> list[ProductApplicationDTO]:
    return await service.list_all(session)


async def delete_record(session: AsyncSession, **kwargs) -> bool:
    return await service.delete_record(session, **kwargs)
