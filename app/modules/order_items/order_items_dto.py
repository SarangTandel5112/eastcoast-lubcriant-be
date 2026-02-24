"""DTO for the order_items table — READ operations."""

from uuid import UUID
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict


class OrderItemDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    order_id: UUID
    variant_id: UUID
    quantity: int
    unit_price: Decimal
    total_price: Decimal
    sku_snapshot: Optional[str] = None
    name_snapshot: Optional[str] = None
