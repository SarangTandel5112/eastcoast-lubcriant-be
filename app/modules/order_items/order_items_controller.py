"""Controller layer for the `order_items` module."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.order_items import order_items_service as service
from app.modules.order_items.order_items_dto import OrderItemDTO
from app.modules.order_items.order_items_dco import OrderItemDCO, OrderItemUpdateDCO


async def create(session: AsyncSession, data: OrderItemDCO) -> OrderItemDTO:
    return await service.create(session, data)


async def get_by_id(session: AsyncSession, record_id: UUID) -> OrderItemDTO | None:
    return await service.get_by_id(session, record_id)


async def list_all(session: AsyncSession) -> list[OrderItemDTO]:
    return await service.list_all(session)


async def update(session: AsyncSession, record_id: UUID, data: OrderItemUpdateDCO) -> OrderItemDTO | None:
    return await service.update(session, record_id, data)


async def delete_record(session: AsyncSession, record_id: UUID) -> bool:
    return await service.delete_record(session, record_id)
