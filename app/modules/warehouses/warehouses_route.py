"""Routes for the `warehouses` module."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.response import respond
from app.core import get_db_session
from app.modules.warehouses import warehouses_controller as controller
from app.modules.warehouses.warehouses_dco import WarehouseDCO, WarehouseUpdateDCO

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_warehouse(
    body: WarehouseDCO,
    db: AsyncSession = Depends(get_db_session),
):
    record = await controller.create(db, body)
    return respond(data=record, message="Warehouse created", status_code=201)


@router.get("/")
async def list_warehouses(
    db: AsyncSession = Depends(get_db_session),
):
    records = await controller.list_all(db)
    return respond(data=records, message="Warehouse records fetched")


@router.get("/{record_id}")
async def get_warehouse(
    record_id: UUID,
    db: AsyncSession = Depends(get_db_session),
):
    record = await controller.get_by_id(db, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    return respond(data=record, message="Warehouse fetched")


@router.patch("/{record_id}")
async def update_warehouse(
    record_id: UUID,
    body: WarehouseUpdateDCO,
    db: AsyncSession = Depends(get_db_session),
):
    record = await controller.update(db, record_id, body)
    if not record:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    return respond(data=record, message="Warehouse updated")


@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_warehouse(
    record_id: UUID,
    db: AsyncSession = Depends(get_db_session),
):
    deleted = await controller.delete_record(db, record_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Warehouse not found")
