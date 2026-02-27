"""DCO for the product_types table — WRITE operations."""

from typing import Optional

from app.common.schemas.base import BaseSchema

class ProductTypeDCO(BaseSchema):
    name: str

class ProductTypeUpdateDCO(BaseSchema):
    name: Optional[str] = None
