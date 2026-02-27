"""DCO for the applications table — WRITE operations."""

from typing import Optional

from app.common.schemas.base import BaseSchema

class ApplicationDCO(BaseSchema):
    name: str

class ApplicationUpdateDCO(BaseSchema):
    name: Optional[str] = None
