"""Routes for the `product_types` module."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.response import respond
from app.core import get_db_session
from app.modules.product_types import product_types_controller as controller
from app.modules.product_types.product_types_dco import ProductTypeDCO, ProductTypeUpdateDCO

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_product_type(
    body: ProductTypeDCO,
    db: AsyncSession = Depends(get_db_session),
):
    record = await controller.create(db, body)
    return respond(data=record, message="ProductType created", status_code=201)


@router.get("/")
async def list_product_types(
    db: AsyncSession = Depends(get_db_session),
):
    records = await controller.list_all(db)
    return respond(data=records, message="ProductType records fetched")


@router.get("/{record_id}")
async def get_product_type(
    record_id: UUID,
    db: AsyncSession = Depends(get_db_session),
):
    record = await controller.get_by_id(db, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="ProductType not found")
    return respond(data=record, message="ProductType fetched")


@router.patch("/{record_id}")
async def update_product_type(
    record_id: UUID,
    body: ProductTypeUpdateDCO,
    db: AsyncSession = Depends(get_db_session),
):
    record = await controller.update(db, record_id, body)
    if not record:
        raise HTTPException(status_code=404, detail="ProductType not found")
    return respond(data=record, message="ProductType updated")


@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product_type(
    record_id: UUID,
    db: AsyncSession = Depends(get_db_session),
):
    deleted = await controller.delete_record(db, record_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="ProductType not found")
