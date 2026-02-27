"""DCO for the inventory table — WRITE operations."""

from uuid import UUID
from typing import Optional

from app.common.schemas.base import BaseSchema

class InventoryDCO(BaseSchema):
    variant_id: UUID
    warehouse_id: UUID
    stock_quantity: int
    reserved_quantity: Optional[int] = None

class InventoryUpdateDCO(BaseSchema):
    variant_id: Optional[UUID] = None
    warehouse_id: Optional[UUID] = None
    stock_quantity: Optional[int] = None
    reserved_quantity: Optional[int] = None
