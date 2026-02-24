"""Routes for the `inventory_movements` module."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.response import respond
from app.core import get_db_session
from app.modules.inventory_movements import inventory_movements_controller as controller
from app.modules.inventory_movements.inventory_movements_dco import InventoryMovementDCO, InventoryMovementUpdateDCO

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_inventory_movement(
    body: InventoryMovementDCO,
    db: AsyncSession = Depends(get_db_session),
):
    record = await controller.create(db, body)
    return respond(data=record, message="InventoryMovement created", status_code=201)


@router.get("/")
async def list_inventory_movements(
    db: AsyncSession = Depends(get_db_session),
):
    records = await controller.list_all(db)
    return respond(data=records, message="InventoryMovement records fetched")


@router.get("/{record_id}")
async def get_inventory_movement(
    record_id: UUID,
    db: AsyncSession = Depends(get_db_session),
):
    record = await controller.get_by_id(db, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="InventoryMovement not found")
    return respond(data=record, message="InventoryMovement fetched")


@router.patch("/{record_id}")
async def update_inventory_movement(
    record_id: UUID,
    body: InventoryMovementUpdateDCO,
    db: AsyncSession = Depends(get_db_session),
):
    record = await controller.update(db, record_id, body)
    if not record:
        raise HTTPException(status_code=404, detail="InventoryMovement not found")
    return respond(data=record, message="InventoryMovement updated")


@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_inventory_movement(
    record_id: UUID,
    db: AsyncSession = Depends(get_db_session),
):
    deleted = await controller.delete_record(db, record_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="InventoryMovement not found")
