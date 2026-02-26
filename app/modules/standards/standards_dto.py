"""DTO for the standards table — READ operations."""

from uuid import UUID
from datetime import datetime
from typing import Optional

from app.common.schemas.base import BaseSchema

from app.modules.standards.standards_entity import StandardTypeEnum

class StandardDTO(BaseSchema):

    id: UUID
    name: str
    standard_type: StandardTypeEnum
    created_at: Optional[datetime] = None
