"""Routes for the `invoices` module."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.response import respond
from app.core import get_db_session
from app.modules.invoices import invoices_controller as controller
from app.modules.invoices.invoices_dco import InvoiceDCO, InvoiceUpdateDCO

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_invoice(
    body: InvoiceDCO,
    db: AsyncSession = Depends(get_db_session),
):
    record = await controller.create(db, body)
    return respond(data=record, message="Invoice created", status_code=201)


@router.get("/")
async def list_invoices(
    db: AsyncSession = Depends(get_db_session),
):
    records = await controller.list_all(db)
    return respond(data=records, message="Invoice records fetched")


@router.get("/{record_id}")
async def get_invoice(
    record_id: UUID,
    db: AsyncSession = Depends(get_db_session),
):
    record = await controller.get_by_id(db, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return respond(data=record, message="Invoice fetched")


@router.patch("/{record_id}")
async def update_invoice(
    record_id: UUID,
    body: InvoiceUpdateDCO,
    db: AsyncSession = Depends(get_db_session),
):
    record = await controller.update(db, record_id, body)
    if not record:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return respond(data=record, message="Invoice updated")


@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_invoice(
    record_id: UUID,
    db: AsyncSession = Depends(get_db_session),
):
    deleted = await controller.delete_record(db, record_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Invoice not found")
