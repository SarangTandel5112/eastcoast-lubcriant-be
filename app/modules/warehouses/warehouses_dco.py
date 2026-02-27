"""DCO for the warehouses table — WRITE operations."""

from typing import Optional

from app.common.schemas.base import BaseSchema

class WarehouseDCO(BaseSchema):
    name: str
    code: str

class WarehouseUpdateDCO(BaseSchema):
    name: Optional[str] = None
    code: Optional[str] = None
