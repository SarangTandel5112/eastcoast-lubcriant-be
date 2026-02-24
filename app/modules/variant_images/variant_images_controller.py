"""Controller layer for the `variant_images` module."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.variant_images import variant_images_service as service
from app.modules.variant_images.variant_images_dto import VariantImageDTO
from app.modules.variant_images.variant_images_dco import VariantImageDCO, VariantImageUpdateDCO


async def create(session: AsyncSession, data: VariantImageDCO) -> VariantImageDTO:
    return await service.create(session, data)


async def get_by_id(session: AsyncSession, record_id: UUID) -> VariantImageDTO | None:
    return await service.get_by_id(session, record_id)


async def list_all(session: AsyncSession) -> list[VariantImageDTO]:
    return await service.list_all(session)


async def update(session: AsyncSession, record_id: UUID, data: VariantImageUpdateDCO) -> VariantImageDTO | None:
    return await service.update(session, record_id, data)


async def delete_record(session: AsyncSession, record_id: UUID) -> bool:
    return await service.delete_record(session, record_id)
