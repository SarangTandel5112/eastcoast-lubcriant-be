"""Controller layer for the `ai_calls` module."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.ai_calls import ai_calls_service as service
from app.modules.ai_calls.ai_calls_dto import AiCallDTO
from app.modules.ai_calls.ai_calls_dco import AiCallDCO, AiCallUpdateDCO


async def create(session: AsyncSession, data: AiCallDCO) -> AiCallDTO:
    return await service.create(session, data)


async def get_by_id(session: AsyncSession, record_id: UUID) -> AiCallDTO | None:
    return await service.get_by_id(session, record_id)


async def list_all(session: AsyncSession) -> list[AiCallDTO]:
    return await service.list_all(session)


async def update(session: AsyncSession, record_id: UUID, data: AiCallUpdateDCO) -> AiCallDTO | None:
    return await service.update(session, record_id, data)


async def delete_record(session: AsyncSession, record_id: UUID) -> bool:
    return await service.delete_record(session, record_id)
