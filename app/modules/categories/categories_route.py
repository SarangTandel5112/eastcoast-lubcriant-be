"""Routes for the `categories` module."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.response import respond
from app.core import get_db_session
from app.modules.categories import categories_controller as controller
from app.modules.categories.categories_dco import CategoryDCO, CategoryUpdateDCO

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_categorie(
    body: CategoryDCO,
    db: AsyncSession = Depends(get_db_session),
):
    record = await controller.create(db, body)
    return respond(data=record, message="Category created", status_code=201)


@router.get("/")
async def list_categories(
    db: AsyncSession = Depends(get_db_session),
):
    records = await controller.list_all(db)
    return respond(data=records, message="Category records fetched")


@router.get("/{record_id}")
async def get_categorie(
    record_id: UUID,
    db: AsyncSession = Depends(get_db_session),
):
    record = await controller.get_by_id(db, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Category not found")
    return respond(data=record, message="Category fetched")


@router.patch("/{record_id}")
async def update_categorie(
    record_id: UUID,
    body: CategoryUpdateDCO,
    db: AsyncSession = Depends(get_db_session),
):
    record = await controller.update(db, record_id, body)
    if not record:
        raise HTTPException(status_code=404, detail="Category not found")
    return respond(data=record, message="Category updated")


@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_categorie(
    record_id: UUID,
    db: AsyncSession = Depends(get_db_session),
):
    deleted = await controller.delete_record(db, record_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Category not found")
