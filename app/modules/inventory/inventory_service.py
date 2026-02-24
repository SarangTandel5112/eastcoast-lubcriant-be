"""Service layer for the `inventory` module."""

import uuid
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func

from app.modules.inventory.inventory_entity import Inventory
from app.modules.inventory.inventory_dto import InventoryDTO
from app.modules.inventory.inventory_dco import InventoryDCO, InventoryUpdateDCO


async def create(session: AsyncSession, data: InventoryDCO) -> InventoryDTO:
    """Create a new Inventory record."""
    entity_obj = Inventory(**data.model_dump())
    session.add(entity_obj)
    await session.flush()
    await session.refresh(entity_obj)
    return InventoryDTO.model_validate(entity_obj)


async def get_by_id(session: AsyncSession, record_id: UUID) -> InventoryDTO | None:
    """Get a Inventory by ID."""
    stmt = select(Inventory).where(Inventory.id == record_id)
    result = await session.execute(stmt)
    entity_obj = result.scalar_one_or_none()
    return InventoryDTO.model_validate(entity_obj) if entity_obj else None


async def list_all(session: AsyncSession) -> list[InventoryDTO]:
    """List all Inventory records."""
    stmt = select(Inventory)
    result = await session.execute(stmt)
    entities = result.scalars().all()
    return [InventoryDTO.model_validate(e) for e in entities]


async def update(session: AsyncSession, record_id: UUID, data: InventoryUpdateDCO) -> InventoryDTO | None:
    """Update a Inventory record."""
    stmt = select(Inventory).where(Inventory.id == record_id)
    result = await session.execute(stmt)
    entity_obj = result.scalar_one_or_none()
    if not entity_obj:
        return None
    updates = data.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(entity_obj, key, value)
    await session.flush()
    await session.refresh(entity_obj)
    return InventoryDTO.model_validate(entity_obj)


async def delete_record(session: AsyncSession, record_id: UUID) -> bool:
    """Delete a Inventory record (hard delete)."""
    stmt = select(Inventory).where(Inventory.id == record_id)
    result = await session.execute(stmt)
    entity_obj = result.scalar_one_or_none()
    if not entity_obj:
        return False
    await session.delete(entity_obj)
    await session.flush()
    return True
