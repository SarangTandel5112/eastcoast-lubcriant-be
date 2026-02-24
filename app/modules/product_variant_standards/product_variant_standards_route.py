"""Routes for the `product_variant_standards` module."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.response import respond
from app.core import get_db_session
from app.modules.product_variant_standards import product_variant_standards_controller as controller
from app.modules.product_variant_standards.product_variant_standards_dco import ProductVariantStandardDCO

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_product_variant_standards(
    body: ProductVariantStandardDCO,
    db: AsyncSession = Depends(get_db_session),
):
    record = await controller.create(db, body)
    return respond(data=record, message="ProductVariantStandard created", status_code=201)


@router.get("/")
async def list_product_variant_standards(
    db: AsyncSession = Depends(get_db_session),
):
    records = await controller.list_all(db)
    return respond(data=records, message="ProductVariantStandard records fetched")
