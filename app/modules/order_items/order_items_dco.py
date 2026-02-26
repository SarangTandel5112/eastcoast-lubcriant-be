"""DCO for the order_items table — WRITE operations."""

from uuid import UUID
from decimal import Decimal
from typing import Optional

from app.common.schemas.base import BaseSchema

class OrderItemDCO(BaseSchema):
    order_id: UUID
    variant_id: UUID
    quantity: int
    unit_price: Decimal

class OrderItemUpdateDCO(BaseSchema):
    order_id: Optional[UUID] = None
    variant_id: Optional[UUID] = None
    quantity: Optional[int] = None
    unit_price: Optional[Decimal] = None
