"""Service layer for the `orders` module."""

import uuid
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func

from app.modules.orders.orders_entity import Order
from app.modules.orders.orders_dto import OrderDTO
from app.modules.orders.orders_dco import OrderDCO, OrderUpdateDCO


async def create(session: AsyncSession, data: OrderDCO) -> OrderDTO:
    """Create a new Order record."""
    entity_obj = Order(**data.model_dump())
    session.add(entity_obj)
    await session.flush()
    await session.refresh(entity_obj)
    return OrderDTO.model_validate(entity_obj)


async def get_by_id(session: AsyncSession, record_id: UUID) -> OrderDTO | None:
    """Get a Order by ID."""
    stmt = select(Order).where(Order.id == record_id)
    result = await session.execute(stmt)
    entity_obj = result.scalar_one_or_none()
    return OrderDTO.model_validate(entity_obj) if entity_obj else None


async def list_all(session: AsyncSession) -> list[OrderDTO]:
    """List all Order records."""
    stmt = select(Order)
    result = await session.execute(stmt)
    entities = result.scalars().all()
    return [OrderDTO.model_validate(e) for e in entities]


async def update(session: AsyncSession, record_id: UUID, data: OrderUpdateDCO) -> OrderDTO | None:
    """Update a Order record."""
    stmt = select(Order).where(Order.id == record_id)
    result = await session.execute(stmt)
    entity_obj = result.scalar_one_or_none()
    if not entity_obj:
        return None
    updates = data.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(entity_obj, key, value)
    await session.flush()
    await session.refresh(entity_obj)
    return OrderDTO.model_validate(entity_obj)


async def delete_record(session: AsyncSession, record_id: UUID) -> bool:
    """Delete a Order record (hard delete)."""
    stmt = select(Order).where(Order.id == record_id)
    result = await session.execute(stmt)
    entity_obj = result.scalar_one_or_none()
    if not entity_obj:
        return False
    await session.delete(entity_obj)
    await session.flush()
    return True
