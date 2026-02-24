"""Controller layer for the `product_variant_attributes` module."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.product_variant_attributes import product_variant_attributes_service as service
from app.modules.product_variant_attributes.product_variant_attributes_dto import ProductVariantAttributeDTO
from app.modules.product_variant_attributes.product_variant_attributes_dco import ProductVariantAttributeDCO


async def create(session: AsyncSession, data: ProductVariantAttributeDCO) -> ProductVariantAttributeDTO:
    return await service.create(session, data)


async def list_all(session: AsyncSession) -> list[ProductVariantAttributeDTO]:
    return await service.list_all(session)


async def delete_record(session: AsyncSession, **kwargs) -> bool:
    return await service.delete_record(session, **kwargs)
