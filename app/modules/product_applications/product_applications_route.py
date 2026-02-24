"""Routes for the `product_applications` module."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.response import respond
from app.core import get_db_session
from app.modules.product_applications import product_applications_controller as controller
from app.modules.product_applications.product_applications_dco import ProductApplicationDCO

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_product_applications(
    body: ProductApplicationDCO,
    db: AsyncSession = Depends(get_db_session),
):
    record = await controller.create(db, body)
    return respond(data=record, message="ProductApplication created", status_code=201)


@router.get("/")
async def list_product_applications(
    db: AsyncSession = Depends(get_db_session),
):
    records = await controller.list_all(db)
    return respond(data=records, message="ProductApplication records fetched")
