"""Controller layer for the `payments` module."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.payments import payments_service as service
from app.modules.payments.payments_dto import PaymentDTO
from app.modules.payments.payments_dco import PaymentDCO, PaymentUpdateDCO


async def create(session: AsyncSession, data: PaymentDCO) -> PaymentDTO:
    return await service.create(session, data)


async def get_by_id(session: AsyncSession, record_id: UUID) -> PaymentDTO | None:
    return await service.get_by_id(session, record_id)


async def list_all(session: AsyncSession) -> list[PaymentDTO]:
    return await service.list_all(session)


async def update(session: AsyncSession, record_id: UUID, data: PaymentUpdateDCO) -> PaymentDTO | None:
    return await service.update(session, record_id, data)


async def delete_record(session: AsyncSession, record_id: UUID) -> bool:
    return await service.delete_record(session, record_id)
