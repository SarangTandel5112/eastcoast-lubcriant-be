"""Controller layer for the `inventory_movements` module."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.inventory_movements import inventory_movements_service as service
from app.modules.inventory_movements.inventory_movements_dto import InventoryMovementDTO
from app.modules.inventory_movements.inventory_movements_dco import InventoryMovementDCO, InventoryMovementUpdateDCO


async def create(session: AsyncSession, data: InventoryMovementDCO) -> InventoryMovementDTO:
    return await service.create(session, data)


async def get_by_id(session: AsyncSession, record_id: UUID) -> InventoryMovementDTO | None:
    return await service.get_by_id(session, record_id)


async def list_all(session: AsyncSession) -> list[InventoryMovementDTO]:
    return await service.list_all(session)


async def update(session: AsyncSession, record_id: UUID, data: InventoryMovementUpdateDCO) -> InventoryMovementDTO | None:
    return await service.update(session, record_id, data)


async def delete_record(session: AsyncSession, record_id: UUID) -> bool:
    return await service.delete_record(session, record_id)
