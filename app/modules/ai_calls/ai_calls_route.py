"""Routes for the `ai_calls` module."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.response import respond
from app.core import get_db_session
from app.modules.ai_calls import ai_calls_controller as controller
from app.modules.ai_calls.ai_calls_dco import AiCallDCO, AiCallUpdateDCO

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_ai_call(
    body: AiCallDCO,
    db: AsyncSession = Depends(get_db_session),
):
    record = await controller.create(db, body)
    return respond(data=record, message="AiCall created", status_code=201)


@router.get("/")
async def list_ai_calls(
    db: AsyncSession = Depends(get_db_session),
):
    records = await controller.list_all(db)
    return respond(data=records, message="AiCall records fetched")


@router.get("/{record_id}")
async def get_ai_call(
    record_id: UUID,
    db: AsyncSession = Depends(get_db_session),
):
    record = await controller.get_by_id(db, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="AiCall not found")
    return respond(data=record, message="AiCall fetched")


@router.patch("/{record_id}")
async def update_ai_call(
    record_id: UUID,
    body: AiCallUpdateDCO,
    db: AsyncSession = Depends(get_db_session),
):
    record = await controller.update(db, record_id, body)
    if not record:
        raise HTTPException(status_code=404, detail="AiCall not found")
    return respond(data=record, message="AiCall updated")


@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ai_call(
    record_id: UUID,
    db: AsyncSession = Depends(get_db_session),
):
    deleted = await controller.delete_record(db, record_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="AiCall not found")
