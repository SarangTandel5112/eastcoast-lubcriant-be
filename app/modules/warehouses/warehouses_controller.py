"""Controller layer for the `warehouses` module."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.warehouses import warehouses_service as service
from app.modules.warehouses.warehouses_dto import WarehouseDTO
from app.modules.warehouses.warehouses_dco import WarehouseDCO, WarehouseUpdateDCO


async def create(session: AsyncSession, data: WarehouseDCO) -> WarehouseDTO:
    return await service.create(session, data)


async def get_by_id(session: AsyncSession, record_id: UUID) -> WarehouseDTO | None:
    return await service.get_by_id(session, record_id)


async def list_all(session: AsyncSession) -> list[WarehouseDTO]:
    return await service.list_all(session)


async def update(session: AsyncSession, record_id: UUID, data: WarehouseUpdateDCO) -> WarehouseDTO | None:
    return await service.update(session, record_id, data)


async def delete_record(session: AsyncSession, record_id: UUID) -> bool:
    return await service.delete_record(session, record_id)
