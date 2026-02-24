"""DCO for the warehouses table — WRITE operations."""

from typing import Optional

from pydantic import BaseModel


class WarehouseDCO(BaseModel):
    name: str
    code: str


class WarehouseUpdateDCO(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
