"""Service layer for the `dealer_addresses` module."""

import uuid
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func

from app.modules.dealer_addresses.dealer_addresses_entity import DealerAddress
from app.modules.dealer_addresses.dealer_addresses_dto import DealerAddressDTO
from app.modules.dealer_addresses.dealer_addresses_dco import DealerAddressDCO, DealerAddressUpdateDCO


async def create(session: AsyncSession, data: DealerAddressDCO) -> DealerAddressDTO:
    """Create a new DealerAddress record."""
    entity_obj = DealerAddress(**data.model_dump())
    session.add(entity_obj)
    await session.flush()
    await session.refresh(entity_obj)
    return DealerAddressDTO.model_validate(entity_obj)


async def get_by_id(session: AsyncSession, record_id: UUID) -> DealerAddressDTO | None:
    """Get a DealerAddress by ID."""
    stmt = select(DealerAddress).where(DealerAddress.id == record_id, DealerAddress.deleted_at.is_(None))
    result = await session.execute(stmt)
    entity_obj = result.scalar_one_or_none()
    return DealerAddressDTO.model_validate(entity_obj) if entity_obj else None


async def list_all(session: AsyncSession) -> list[DealerAddressDTO]:
    """List all DealerAddress records."""
    stmt = select(DealerAddress).where(DealerAddress.deleted_at.is_(None))
    result = await session.execute(stmt)
    entities = result.scalars().all()
    return [DealerAddressDTO.model_validate(e) for e in entities]


async def update(session: AsyncSession, record_id: UUID, data: DealerAddressUpdateDCO) -> DealerAddressDTO | None:
    """Update a DealerAddress record."""
    stmt = select(DealerAddress).where(DealerAddress.id == record_id, DealerAddress.deleted_at.is_(None))
    result = await session.execute(stmt)
    entity_obj = result.scalar_one_or_none()
    if not entity_obj:
        return None
    updates = data.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(entity_obj, key, value)
    await session.flush()
    await session.refresh(entity_obj)
    return DealerAddressDTO.model_validate(entity_obj)


async def delete_record(session: AsyncSession, record_id: UUID) -> bool:
    """Delete a DealerAddress record (hard delete)."""
    stmt = select(DealerAddress).where(DealerAddress.id == record_id)
    result = await session.execute(stmt)
    entity_obj = result.scalar_one_or_none()
    if not entity_obj:
        return False
    await session.delete(entity_obj)
    await session.flush()
    return True

async def soft_delete_dealer_addresses(session: AsyncSession, record_id: UUID) -> bool:
    """Soft-delete a DealerAddress by setting deleted_at."""
    stmt = select(DealerAddress).where(DealerAddress.id == record_id, DealerAddress.deleted_at.is_(None))
    result = await session.execute(stmt)
    entity_obj = result.scalar_one_or_none()
    if not entity_obj:
        return False
    entity_obj.deleted_at = func.now()
    await session.flush()
    return True
