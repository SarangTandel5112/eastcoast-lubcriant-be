"""DTO for the inventory table — READ operations."""

from uuid import UUID
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class InventoryDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    variant_id: UUID
    warehouse_id: UUID
    stock_quantity: int
    reserved_quantity: Optional[int] = None
    updated_at: Optional[datetime] = None
