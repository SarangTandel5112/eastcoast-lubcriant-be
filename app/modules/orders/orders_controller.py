"""Controller layer for the `orders` module."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.orders import orders_service as service
from app.modules.orders.orders_dto import OrderDTO
from app.modules.orders.orders_dco import OrderDCO, OrderUpdateDCO


async def create(session: AsyncSession, data: OrderDCO) -> OrderDTO:
    return await service.create(session, data)


async def get_by_id(session: AsyncSession, record_id: UUID) -> OrderDTO | None:
    return await service.get_by_id(session, record_id)


async def list_all(session: AsyncSession) -> list[OrderDTO]:
    return await service.list_all(session)


async def update(session: AsyncSession, record_id: UUID, data: OrderUpdateDCO) -> OrderDTO | None:
    return await service.update(session, record_id, data)


async def delete_record(session: AsyncSession, record_id: UUID) -> bool:
    return await service.delete_record(session, record_id)
