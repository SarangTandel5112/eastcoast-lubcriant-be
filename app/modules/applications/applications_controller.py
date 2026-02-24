"""Controller layer for the `applications` module."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.applications import applications_service as service
from app.modules.applications.applications_dto import ApplicationDTO
from app.modules.applications.applications_dco import ApplicationDCO, ApplicationUpdateDCO


async def create(session: AsyncSession, data: ApplicationDCO) -> ApplicationDTO:
    return await service.create(session, data)


async def get_by_id(session: AsyncSession, record_id: UUID) -> ApplicationDTO | None:
    return await service.get_by_id(session, record_id)


async def list_all(session: AsyncSession) -> list[ApplicationDTO]:
    return await service.list_all(session)


async def update(session: AsyncSession, record_id: UUID, data: ApplicationUpdateDCO) -> ApplicationDTO | None:
    return await service.update(session, record_id, data)


async def delete_record(session: AsyncSession, record_id: UUID) -> bool:
    return await service.delete_record(session, record_id)
