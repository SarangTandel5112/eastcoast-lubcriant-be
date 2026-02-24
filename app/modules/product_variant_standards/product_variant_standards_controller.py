"""Controller layer for the `product_variant_standards` module."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.product_variant_standards import product_variant_standards_service as service
from app.modules.product_variant_standards.product_variant_standards_dto import ProductVariantStandardDTO
from app.modules.product_variant_standards.product_variant_standards_dco import ProductVariantStandardDCO


async def create(session: AsyncSession, data: ProductVariantStandardDCO) -> ProductVariantStandardDTO:
    return await service.create(session, data)


async def list_all(session: AsyncSession) -> list[ProductVariantStandardDTO]:
    return await service.list_all(session)


async def delete_record(session: AsyncSession, **kwargs) -> bool:
    return await service.delete_record(session, **kwargs)
