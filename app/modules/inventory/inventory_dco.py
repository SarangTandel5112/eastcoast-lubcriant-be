"""DCO for the inventory table — WRITE operations."""

from uuid import UUID
from typing import Optional

from pydantic import BaseModel


class InventoryDCO(BaseModel):
    variant_id: UUID
    warehouse_id: UUID
    stock_quantity: int
    reserved_quantity: Optional[int] = None


class InventoryUpdateDCO(BaseModel):
    variant_id: Optional[UUID] = None
    warehouse_id: Optional[UUID] = None
    stock_quantity: Optional[int] = None
    reserved_quantity: Optional[int] = None
