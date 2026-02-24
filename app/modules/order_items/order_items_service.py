"""Service layer for the `order_items` module."""

import uuid
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func

from app.modules.order_items.order_items_entity import OrderItem
from app.modules.order_items.order_items_dto import OrderItemDTO
from app.modules.order_items.order_items_dco import OrderItemDCO, OrderItemUpdateDCO


async def create(session: AsyncSession, data: OrderItemDCO) -> OrderItemDTO:
    """Create a new OrderItem record."""
    entity_obj = OrderItem(**data.model_dump())
    session.add(entity_obj)
    await session.flush()
    await session.refresh(entity_obj)
    return OrderItemDTO.model_validate(entity_obj)


async def get_by_id(session: AsyncSession, record_id: UUID) -> OrderItemDTO | None:
    """Get a OrderItem by ID."""
    stmt = select(OrderItem).where(OrderItem.id == record_id)
    result = await session.execute(stmt)
    entity_obj = result.scalar_one_or_none()
    return OrderItemDTO.model_validate(entity_obj) if entity_obj else None


async def list_all(session: AsyncSession) -> list[OrderItemDTO]:
    """List all OrderItem records."""
    stmt = select(OrderItem)
    result = await session.execute(stmt)
    entities = result.scalars().all()
    return [OrderItemDTO.model_validate(e) for e in entities]


async def update(session: AsyncSession, record_id: UUID, data: OrderItemUpdateDCO) -> OrderItemDTO | None:
    """Update a OrderItem record."""
    stmt = select(OrderItem).where(OrderItem.id == record_id)
    result = await session.execute(stmt)
    entity_obj = result.scalar_one_or_none()
    if not entity_obj:
        return None
    updates = data.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(entity_obj, key, value)
    await session.flush()
    await session.refresh(entity_obj)
    return OrderItemDTO.model_validate(entity_obj)


async def delete_record(session: AsyncSession, record_id: UUID) -> bool:
    """Delete a OrderItem record (hard delete)."""
    stmt = select(OrderItem).where(OrderItem.id == record_id)
    result = await session.execute(stmt)
    entity_obj = result.scalar_one_or_none()
    if not entity_obj:
        return False
    await session.delete(entity_obj)
    await session.flush()
    return True
