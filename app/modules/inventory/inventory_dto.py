"""DTO for the inventory table — READ operations."""

from uuid import UUID
from datetime import datetime
from typing import Optional

from app.common.schemas.base import BaseSchema

class InventoryDTO(BaseSchema):

    id: UUID
    variant_id: UUID
    warehouse_id: UUID
    stock_quantity: int
    reserved_quantity: Optional[int] = None
    updated_at: Optional[datetime] = None
