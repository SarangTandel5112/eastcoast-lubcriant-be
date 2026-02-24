"""DTO for the ai_calls table — READ operations."""

from uuid import UUID
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.modules.ai_calls.ai_calls_entity import CallStatusEnum


class AiCallDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    dealer_id: UUID
    call_status: CallStatusEnum
    provider_call_id: Optional[str] = None
    call_summary: Optional[str] = None
    transcript: Optional[str] = None
    call_duration_sec: Optional[int] = None
    created_at: Optional[datetime] = None
