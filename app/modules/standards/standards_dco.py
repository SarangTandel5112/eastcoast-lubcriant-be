"""DCO for the standards table — WRITE operations."""

from typing import Optional

from app.common.schemas.base import BaseSchema

from app.modules.standards.standards_entity import StandardTypeEnum

class StandardDCO(BaseSchema):
    name: str
    standard_type: StandardTypeEnum

class StandardUpdateDCO(BaseSchema):
    name: Optional[str] = None
    standard_type: Optional[StandardTypeEnum] = None
