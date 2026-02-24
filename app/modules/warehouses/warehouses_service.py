"""Service layer for the `warehouses` module."""

import uuid
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func

from app.modules.warehouses.warehouses_entity import Warehouse
from app.modules.warehouses.warehouses_dto import WarehouseDTO
from app.modules.warehouses.warehouses_dco import WarehouseDCO, WarehouseUpdateDCO


async def create(session: AsyncSession, data: WarehouseDCO) -> WarehouseDTO:
    """Create a new Warehouse record."""
    entity_obj = Warehouse(**data.model_dump())
    session.add(entity_obj)
    await session.flush()
    await session.refresh(entity_obj)
    return WarehouseDTO.model_validate(entity_obj)


async def get_by_id(session: AsyncSession, record_id: UUID) -> WarehouseDTO | None:
    """Get a Warehouse by ID."""
    stmt = select(Warehouse).where(Warehouse.id == record_id)
    result = await session.execute(stmt)
    entity_obj = result.scalar_one_or_none()
    return WarehouseDTO.model_validate(entity_obj) if entity_obj else None


async def list_all(session: AsyncSession) -> list[WarehouseDTO]:
    """List all Warehouse records."""
    stmt = select(Warehouse)
    result = await session.execute(stmt)
    entities = result.scalars().all()
    return [WarehouseDTO.model_validate(e) for e in entities]


async def update(session: AsyncSession, record_id: UUID, data: WarehouseUpdateDCO) -> WarehouseDTO | None:
    """Update a Warehouse record."""
    stmt = select(Warehouse).where(Warehouse.id == record_id)
    result = await session.execute(stmt)
    entity_obj = result.scalar_one_or_none()
    if not entity_obj:
        return None
    updates = data.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(entity_obj, key, value)
    await session.flush()
    await session.refresh(entity_obj)
    return WarehouseDTO.model_validate(entity_obj)


async def delete_record(session: AsyncSession, record_id: UUID) -> bool:
    """Delete a Warehouse record (hard delete)."""
    stmt = select(Warehouse).where(Warehouse.id == record_id)
    result = await session.execute(stmt)
    entity_obj = result.scalar_one_or_none()
    if not entity_obj:
        return False
    await session.delete(entity_obj)
    await session.flush()
    return True
