"""Routes for the `order_items` module."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.response import respond
from app.core import get_db_session
from app.modules.order_items import order_items_controller as controller
from app.modules.order_items.order_items_dco import OrderItemDCO, OrderItemUpdateDCO

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_order_item(
    body: OrderItemDCO,
    db: AsyncSession = Depends(get_db_session),
):
    record = await controller.create(db, body)
    return respond(data=record, message="OrderItem created", status_code=201)


@router.get("/")
async def list_order_items(
    db: AsyncSession = Depends(get_db_session),
):
    records = await controller.list_all(db)
    return respond(data=records, message="OrderItem records fetched")


@router.get("/{record_id}")
async def get_order_item(
    record_id: UUID,
    db: AsyncSession = Depends(get_db_session),
):
    record = await controller.get_by_id(db, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="OrderItem not found")
    return respond(data=record, message="OrderItem fetched")


@router.patch("/{record_id}")
async def update_order_item(
    record_id: UUID,
    body: OrderItemUpdateDCO,
    db: AsyncSession = Depends(get_db_session),
):
    record = await controller.update(db, record_id, body)
    if not record:
        raise HTTPException(status_code=404, detail="OrderItem not found")
    return respond(data=record, message="OrderItem updated")


@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_order_item(
    record_id: UUID,
    db: AsyncSession = Depends(get_db_session),
):
    deleted = await controller.delete_record(db, record_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="OrderItem not found")
