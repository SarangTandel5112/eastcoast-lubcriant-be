"""DTO for the ai_calls table — READ operations."""

from uuid import UUID
from datetime import datetime
from typing import Optional

from app.common.schemas.base import BaseSchema
from app.modules.ai_calls.ai_calls_entity import CallStatusEnum

class AiCallDTO(BaseSchema):

    id: UUID
    dealer_id: UUID
    call_status: CallStatusEnum
    provider_call_id: Optional[str] = None
    call_summary: Optional[str] = None
    transcript: Optional[str] = None
    call_duration_sec: Optional[int] = None
    created_at: Optional[datetime] = None
