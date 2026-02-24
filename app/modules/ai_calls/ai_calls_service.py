"""Service layer for the `ai_calls` module."""

import uuid
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func

from app.modules.ai_calls.ai_calls_entity import AiCall
from app.modules.ai_calls.ai_calls_dto import AiCallDTO
from app.modules.ai_calls.ai_calls_dco import AiCallDCO, AiCallUpdateDCO


async def create(session: AsyncSession, data: AiCallDCO) -> AiCallDTO:
    """Create a new AiCall record."""
    entity_obj = AiCall(**data.model_dump())
    session.add(entity_obj)
    await session.flush()
    await session.refresh(entity_obj)
    return AiCallDTO.model_validate(entity_obj)


async def get_by_id(session: AsyncSession, record_id: UUID) -> AiCallDTO | None:
    """Get a AiCall by ID."""
    stmt = select(AiCall).where(AiCall.id == record_id)
    result = await session.execute(stmt)
    entity_obj = result.scalar_one_or_none()
    return AiCallDTO.model_validate(entity_obj) if entity_obj else None


async def list_all(session: AsyncSession) -> list[AiCallDTO]:
    """List all AiCall records."""
    stmt = select(AiCall)
    result = await session.execute(stmt)
    entities = result.scalars().all()
    return [AiCallDTO.model_validate(e) for e in entities]


async def update(session: AsyncSession, record_id: UUID, data: AiCallUpdateDCO) -> AiCallDTO | None:
    """Update a AiCall record."""
    stmt = select(AiCall).where(AiCall.id == record_id)
    result = await session.execute(stmt)
    entity_obj = result.scalar_one_or_none()
    if not entity_obj:
        return None
    updates = data.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(entity_obj, key, value)
    await session.flush()
    await session.refresh(entity_obj)
    return AiCallDTO.model_validate(entity_obj)


async def delete_record(session: AsyncSession, record_id: UUID) -> bool:
    """Delete a AiCall record (hard delete)."""
    stmt = select(AiCall).where(AiCall.id == record_id)
    result = await session.execute(stmt)
    entity_obj = result.scalar_one_or_none()
    if not entity_obj:
        return False
    await session.delete(entity_obj)
    await session.flush()
    return True
