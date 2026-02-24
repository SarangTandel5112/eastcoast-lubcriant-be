"""Controller layer for the `invoices` module."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.invoices import invoices_service as service
from app.modules.invoices.invoices_dto import InvoiceDTO
from app.modules.invoices.invoices_dco import InvoiceDCO, InvoiceUpdateDCO


async def create(session: AsyncSession, data: InvoiceDCO) -> InvoiceDTO:
    return await service.create(session, data)


async def get_by_id(session: AsyncSession, record_id: UUID) -> InvoiceDTO | None:
    return await service.get_by_id(session, record_id)


async def list_all(session: AsyncSession) -> list[InvoiceDTO]:
    return await service.list_all(session)


async def update(session: AsyncSession, record_id: UUID, data: InvoiceUpdateDCO) -> InvoiceDTO | None:
    return await service.update(session, record_id, data)


async def delete_record(session: AsyncSession, record_id: UUID) -> bool:
    return await service.delete_record(session, record_id)
