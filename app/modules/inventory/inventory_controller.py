"""Controller layer for the `inventory` module."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.inventory import inventory_service as service
from app.modules.inventory.inventory_dto import InventoryDTO
from app.modules.inventory.inventory_dco import InventoryDCO, InventoryUpdateDCO


async def create(session: AsyncSession, data: InventoryDCO) -> InventoryDTO:
    return await service.create(session, data)


async def get_by_id(session: AsyncSession, record_id: UUID) -> InventoryDTO | None:
    return await service.get_by_id(session, record_id)


async def list_all(session: AsyncSession) -> list[InventoryDTO]:
    return await service.list_all(session)


async def update(session: AsyncSession, record_id: UUID, data: InventoryUpdateDCO) -> InventoryDTO | None:
    return await service.update(session, record_id, data)


async def delete_record(session: AsyncSession, record_id: UUID) -> bool:
    return await service.delete_record(session, record_id)
