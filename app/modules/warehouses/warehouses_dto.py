"""DTO for the warehouses table — READ operations."""

from uuid import UUID
from datetime import datetime
from typing import Optional

from app.common.schemas.base import BaseSchema

class WarehouseDTO(BaseSchema):

    id: UUID
    name: str
    code: str
    created_at: Optional[datetime] = None
