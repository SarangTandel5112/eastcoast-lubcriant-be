"""DCO for the standards table — WRITE operations."""

from typing import Optional

from pydantic import BaseModel

from app.modules.standards.standards_entity import StandardTypeEnum


class StandardDCO(BaseModel):
    name: str
    standard_type: StandardTypeEnum


class StandardUpdateDCO(BaseModel):
    name: Optional[str] = None
    standard_type: Optional[StandardTypeEnum] = None
