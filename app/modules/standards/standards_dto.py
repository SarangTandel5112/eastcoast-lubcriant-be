"""DTO for the standards table — READ operations."""

from uuid import UUID
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.modules.standards.standards_entity import StandardTypeEnum


class StandardDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    standard_type: StandardTypeEnum
    created_at: Optional[datetime] = None
