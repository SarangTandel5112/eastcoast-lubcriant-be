"""Routes for the `inventory` module."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.response import respond
from app.core import get_db_session
from app.modules.inventory import inventory_controller as controller
from app.modules.inventory.inventory_dco import InventoryDCO, InventoryUpdateDCO

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_inventory(
    body: InventoryDCO,
    db: AsyncSession = Depends(get_db_session),
):
    record = await controller.create(db, body)
    return respond(data=record, message="Inventory created", status_code=201)


@router.get("/")
async def list_inventory(
    db: AsyncSession = Depends(get_db_session),
):
    records = await controller.list_all(db)
    return respond(data=records, message="Inventory records fetched")


@router.get("/{record_id}")
async def get_inventory(
    record_id: UUID,
    db: AsyncSession = Depends(get_db_session),
):
    record = await controller.get_by_id(db, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Inventory not found")
    return respond(data=record, message="Inventory fetched")


@router.patch("/{record_id}")
async def update_inventory(
    record_id: UUID,
    body: InventoryUpdateDCO,
    db: AsyncSession = Depends(get_db_session),
):
    record = await controller.update(db, record_id, body)
    if not record:
        raise HTTPException(status_code=404, detail="Inventory not found")
    return respond(data=record, message="Inventory updated")


@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_inventory(
    record_id: UUID,
    db: AsyncSession = Depends(get_db_session),
):
    deleted = await controller.delete_record(db, record_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Inventory not found")
