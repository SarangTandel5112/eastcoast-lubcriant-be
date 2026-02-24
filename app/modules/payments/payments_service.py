"""Service layer for the `payments` module."""

import uuid
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func

from app.modules.payments.payments_entity import Payment
from app.modules.payments.payments_dto import PaymentDTO
from app.modules.payments.payments_dco import PaymentDCO, PaymentUpdateDCO


async def create(session: AsyncSession, data: PaymentDCO) -> PaymentDTO:
    """Create a new Payment record."""
    entity_obj = Payment(**data.model_dump())
    session.add(entity_obj)
    await session.flush()
    await session.refresh(entity_obj)
    return PaymentDTO.model_validate(entity_obj)


async def get_by_id(session: AsyncSession, record_id: UUID) -> PaymentDTO | None:
    """Get a Payment by ID."""
    stmt = select(Payment).where(Payment.id == record_id)
    result = await session.execute(stmt)
    entity_obj = result.scalar_one_or_none()
    return PaymentDTO.model_validate(entity_obj) if entity_obj else None


async def list_all(session: AsyncSession) -> list[PaymentDTO]:
    """List all Payment records."""
    stmt = select(Payment)
    result = await session.execute(stmt)
    entities = result.scalars().all()
    return [PaymentDTO.model_validate(e) for e in entities]


async def update(session: AsyncSession, record_id: UUID, data: PaymentUpdateDCO) -> PaymentDTO | None:
    """Update a Payment record."""
    stmt = select(Payment).where(Payment.id == record_id)
    result = await session.execute(stmt)
    entity_obj = result.scalar_one_or_none()
    if not entity_obj:
        return None
    updates = data.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(entity_obj, key, value)
    await session.flush()
    await session.refresh(entity_obj)
    return PaymentDTO.model_validate(entity_obj)


async def delete_record(session: AsyncSession, record_id: UUID) -> bool:
    """Delete a Payment record (hard delete)."""
    stmt = select(Payment).where(Payment.id == record_id)
    result = await session.execute(stmt)
    entity_obj = result.scalar_one_or_none()
    if not entity_obj:
        return False
    await session.delete(entity_obj)
    await session.flush()
    return True
