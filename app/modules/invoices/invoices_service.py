"""Service layer for the `invoices` module."""

import uuid
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func

from app.modules.invoices.invoices_entity import Invoice
from app.modules.invoices.invoices_dto import InvoiceDTO
from app.modules.invoices.invoices_dco import InvoiceDCO, InvoiceUpdateDCO


async def create(session: AsyncSession, data: InvoiceDCO) -> InvoiceDTO:
    """Create a new Invoice record."""
    entity_obj = Invoice(**data.model_dump())
    session.add(entity_obj)
    await session.flush()
    await session.refresh(entity_obj)
    return InvoiceDTO.model_validate(entity_obj)


async def get_by_id(session: AsyncSession, record_id: UUID) -> InvoiceDTO | None:
    """Get a Invoice by ID."""
    stmt = select(Invoice).where(Invoice.id == record_id)
    result = await session.execute(stmt)
    entity_obj = result.scalar_one_or_none()
    return InvoiceDTO.model_validate(entity_obj) if entity_obj else None


async def list_all(session: AsyncSession) -> list[InvoiceDTO]:
    """List all Invoice records."""
    stmt = select(Invoice)
    result = await session.execute(stmt)
    entities = result.scalars().all()
    return [InvoiceDTO.model_validate(e) for e in entities]


async def update(session: AsyncSession, record_id: UUID, data: InvoiceUpdateDCO) -> InvoiceDTO | None:
    """Update a Invoice record."""
    stmt = select(Invoice).where(Invoice.id == record_id)
    result = await session.execute(stmt)
    entity_obj = result.scalar_one_or_none()
    if not entity_obj:
        return None
    updates = data.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(entity_obj, key, value)
    await session.flush()
    await session.refresh(entity_obj)
    return InvoiceDTO.model_validate(entity_obj)


async def delete_record(session: AsyncSession, record_id: UUID) -> bool:
    """Delete a Invoice record (hard delete)."""
    stmt = select(Invoice).where(Invoice.id == record_id)
    result = await session.execute(stmt)
    entity_obj = result.scalar_one_or_none()
    if not entity_obj:
        return False
    await session.delete(entity_obj)
    await session.flush()
    return True
