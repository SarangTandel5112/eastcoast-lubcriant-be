"""Controller layer for the `attributes` module."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.attributes import attributes_service as service
from app.modules.attributes.attributes_dto import AttributeDTO
from app.modules.attributes.attributes_dco import AttributeDCO, AttributeUpdateDCO


async def create(session: AsyncSession, data: AttributeDCO) -> AttributeDTO:
    return await service.create(session, data)


async def get_by_id(session: AsyncSession, record_id: UUID) -> AttributeDTO | None:
    return await service.get_by_id(session, record_id)


async def list_all(session: AsyncSession) -> list[AttributeDTO]:
    return await service.list_all(session)


async def update(session: AsyncSession, record_id: UUID, data: AttributeUpdateDCO) -> AttributeDTO | None:
    return await service.update(session, record_id, data)


async def delete_record(session: AsyncSession, record_id: UUID) -> bool:
    return await service.delete_record(session, record_id)
