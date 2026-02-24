"""Service layer for the `inventory_movements` module."""

import uuid
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func

from app.modules.inventory_movements.inventory_movements_entity import InventoryMovement
from app.modules.inventory_movements.inventory_movements_dto import InventoryMovementDTO
from app.modules.inventory_movements.inventory_movements_dco import InventoryMovementDCO, InventoryMovementUpdateDCO


async def create(session: AsyncSession, data: InventoryMovementDCO) -> InventoryMovementDTO:
    """Create a new InventoryMovement record."""
    entity_obj = InventoryMovement(**data.model_dump())
    session.add(entity_obj)
    await session.flush()
    await session.refresh(entity_obj)
    return InventoryMovementDTO.model_validate(entity_obj)


async def get_by_id(session: AsyncSession, record_id: UUID) -> InventoryMovementDTO | None:
    """Get a InventoryMovement by ID."""
    stmt = select(InventoryMovement).where(InventoryMovement.id == record_id)
    result = await session.execute(stmt)
    entity_obj = result.scalar_one_or_none()
    return InventoryMovementDTO.model_validate(entity_obj) if entity_obj else None


async def list_all(session: AsyncSession) -> list[InventoryMovementDTO]:
    """List all InventoryMovement records."""
    stmt = select(InventoryMovement)
    result = await session.execute(stmt)
    entities = result.scalars().all()
    return [InventoryMovementDTO.model_validate(e) for e in entities]


async def update(session: AsyncSession, record_id: UUID, data: InventoryMovementUpdateDCO) -> InventoryMovementDTO | None:
    """Update a InventoryMovement record."""
    stmt = select(InventoryMovement).where(InventoryMovement.id == record_id)
    result = await session.execute(stmt)
    entity_obj = result.scalar_one_or_none()
    if not entity_obj:
        return None
    updates = data.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(entity_obj, key, value)
    await session.flush()
    await session.refresh(entity_obj)
    return InventoryMovementDTO.model_validate(entity_obj)


async def delete_record(session: AsyncSession, record_id: UUID) -> bool:
    """Delete a InventoryMovement record (hard delete)."""
    stmt = select(InventoryMovement).where(InventoryMovement.id == record_id)
    result = await session.execute(stmt)
    entity_obj = result.scalar_one_or_none()
    if not entity_obj:
        return False
    await session.delete(entity_obj)
    await session.flush()
    return True
