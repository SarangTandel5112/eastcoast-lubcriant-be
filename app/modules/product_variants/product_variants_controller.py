"""Controller layer for the `product_variants` module."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.product_variants import product_variants_service as service
from app.modules.product_variants.product_variants_dto import ProductVariantDTO
from app.modules.product_variants.product_variants_dco import ProductVariantDCO, ProductVariantUpdateDCO


async def create(session: AsyncSession, data: ProductVariantDCO) -> ProductVariantDTO:
    return await service.create(session, data)


async def get_by_id(session: AsyncSession, record_id: UUID) -> ProductVariantDTO | None:
    return await service.get_by_id(session, record_id)


async def list_all(session: AsyncSession) -> list[ProductVariantDTO]:
    return await service.list_all(session)


async def update(session: AsyncSession, record_id: UUID, data: ProductVariantUpdateDCO) -> ProductVariantDTO | None:
    return await service.update(session, record_id, data)


async def delete_record(session: AsyncSession, record_id: UUID) -> bool:
    return await service.delete_record(session, record_id)
