"""DTO for the attributes table — READ operations."""

from uuid import UUID
from datetime import datetime
from typing import Optional

from app.common.schemas.base import BaseSchema
from app.modules.attributes.attributes_entity import DataTypeEnum

class AttributeDTO(BaseSchema):

    id: UUID
    name: str
    data_type: DataTypeEnum
    unit: Optional[str] = None
    created_at: Optional[datetime] = None
