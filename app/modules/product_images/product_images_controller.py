"""Controller layer for the `product_images` module."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.product_images import product_images_service as service
from app.modules.product_images.product_images_dto import ProductImageDTO
from app.modules.product_images.product_images_dco import ProductImageDCO, ProductImageUpdateDCO


async def create(session: AsyncSession, data: ProductImageDCO) -> ProductImageDTO:
    return await service.create(session, data)


async def get_by_id(session: AsyncSession, record_id: UUID) -> ProductImageDTO | None:
    return await service.get_by_id(session, record_id)


async def list_all(session: AsyncSession) -> list[ProductImageDTO]:
    return await service.list_all(session)


async def update(session: AsyncSession, record_id: UUID, data: ProductImageUpdateDCO) -> ProductImageDTO | None:
    return await service.update(session, record_id, data)


async def delete_record(session: AsyncSession, record_id: UUID) -> bool:
    return await service.delete_record(session, record_id)
