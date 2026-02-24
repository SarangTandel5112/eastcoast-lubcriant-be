"""Routes for the `attributes` module."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.response import respond
from app.core import get_db_session
from app.modules.attributes import attributes_controller as controller
from app.modules.attributes.attributes_dco import AttributeDTO, AttributeUpdateDCO

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_attribute(
    body: AttributeDTO,
    db: AsyncSession = Depends(get_db_session),
):
    record = await controller.create(db, body)
    return respond(data=record, message="Attribute created", status_code=201)


@router.get("/")
async def list_attributes(
    db: AsyncSession = Depends(get_db_session),
):
    records = await controller.list_all(db)
    return respond(data=records, message="Attribute records fetched")


@router.get("/{record_id}")
async def get_attribute(
    record_id: UUID,
    db: AsyncSession = Depends(get_db_session),
):
    record = await controller.get_by_id(db, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Attribute not found")
    return respond(data=record, message="Attribute fetched")


@router.patch("/{record_id}")
async def update_attribute(
    record_id: UUID,
    body: AttributeUpdateDCO,
    db: AsyncSession = Depends(get_db_session),
):
    record = await controller.update(db, record_id, body)
    if not record:
        raise HTTPException(status_code=404, detail="Attribute not found")
    return respond(data=record, message="Attribute updated")


@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_attribute(
    record_id: UUID,
    db: AsyncSession = Depends(get_db_session),
):
    deleted = await controller.delete_record(db, record_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Attribute not found")
