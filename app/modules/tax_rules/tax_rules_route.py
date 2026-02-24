"""Routes for the `tax_rules` module."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.response import respond
from app.core import get_db_session
from app.modules.tax_rules import tax_rules_controller as controller
from app.modules.tax_rules.tax_rules_dco import TaxRuleDCO, TaxRuleUpdateDCO

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_tax_rule(
    body: TaxRuleDCO,
    db: AsyncSession = Depends(get_db_session),
):
    record = await controller.create(db, body)
    return respond(data=record, message="TaxRule created", status_code=201)


@router.get("/")
async def list_tax_rules(
    db: AsyncSession = Depends(get_db_session),
):
    records = await controller.list_all(db)
    return respond(data=records, message="TaxRule records fetched")


@router.get("/{record_id}")
async def get_tax_rule(
    record_id: UUID,
    db: AsyncSession = Depends(get_db_session),
):
    record = await controller.get_by_id(db, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="TaxRule not found")
    return respond(data=record, message="TaxRule fetched")


@router.patch("/{record_id}")
async def update_tax_rule(
    record_id: UUID,
    body: TaxRuleUpdateDCO,
    db: AsyncSession = Depends(get_db_session),
):
    record = await controller.update(db, record_id, body)
    if not record:
        raise HTTPException(status_code=404, detail="TaxRule not found")
    return respond(data=record, message="TaxRule updated")


@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tax_rule(
    record_id: UUID,
    db: AsyncSession = Depends(get_db_session),
):
    deleted = await controller.delete_record(db, record_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="TaxRule not found")
