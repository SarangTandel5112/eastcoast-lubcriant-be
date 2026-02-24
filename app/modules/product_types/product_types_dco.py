"""DCO for the product_types table — WRITE operations."""

from typing import Optional

from pydantic import BaseModel


class ProductTypeDCO(BaseModel):
    name: str


class ProductTypeUpdateDCO(BaseModel):
    name: Optional[str] = None
