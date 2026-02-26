"""DCO for the ai_calls table — WRITE operations."""

from uuid import UUID
from typing import Optional

from app.common.schemas.base import BaseSchema
from app.modules.ai_calls.ai_calls_entity import CallStatusEnum

class AiCallDCO(BaseSchema):
    dealer_id: UUID
    call_status: CallStatusEnum
    provider_call_id: Optional[str] = None
    call_summary: Optional[str] = None
    transcript: Optional[str] = None
    call_duration_sec: Optional[int] = None

class AiCallUpdateDCO(BaseSchema):
    call_status: Optional[CallStatusEnum] = None
    provider_call_id: Optional[str] = None
    call_summary: Optional[str] = None
    transcript: Optional[str] = None
    call_duration_sec: Optional[int] = None
