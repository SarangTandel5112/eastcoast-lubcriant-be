"""Service layer for the `applications` module."""

import uuid
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func

from app.modules.applications.applications_entity import Application
from app.modules.applications.applications_dto import ApplicationDTO
from app.modules.applications.applications_dco import ApplicationDCO, ApplicationUpdateDCO


async def create(session: AsyncSession, data: ApplicationDCO) -> ApplicationDTO:
    """Create a new Application record."""
    entity_obj = Application(**data.model_dump())
    session.add(entity_obj)
    await session.flush()
    await session.refresh(entity_obj)
    return ApplicationDTO.model_validate(entity_obj)


async def get_by_id(session: AsyncSession, record_id: UUID) -> ApplicationDTO | None:
    """Get a Application by ID."""
    stmt = select(Application).where(Application.id == record_id)
    result = await session.execute(stmt)
    entity_obj = result.scalar_one_or_none()
    return ApplicationDTO.model_validate(entity_obj) if entity_obj else None


async def list_all(session: AsyncSession) -> list[ApplicationDTO]:
    """List all Application records."""
    stmt = select(Application)
    result = await session.execute(stmt)
    entities = result.scalars().all()
    return [ApplicationDTO.model_validate(e) for e in entities]


async def update(session: AsyncSession, record_id: UUID, data: ApplicationUpdateDCO) -> ApplicationDTO | None:
    """Update a Application record."""
    stmt = select(Application).where(Application.id == record_id)
    result = await session.execute(stmt)
    entity_obj = result.scalar_one_or_none()
    if not entity_obj:
        return None
    updates = data.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(entity_obj, key, value)
    await session.flush()
    await session.refresh(entity_obj)
    return ApplicationDTO.model_validate(entity_obj)


async def delete_record(session: AsyncSession, record_id: UUID) -> bool:
    """Delete a Application record (hard delete)."""
    stmt = select(Application).where(Application.id == record_id)
    result = await session.execute(stmt)
    entity_obj = result.scalar_one_or_none()
    if not entity_obj:
        return False
    await session.delete(entity_obj)
    await session.flush()
    return True
