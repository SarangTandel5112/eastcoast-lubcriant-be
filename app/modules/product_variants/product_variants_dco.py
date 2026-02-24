"""DCO for the product_variants table — WRITE operations."""

from uuid import UUID
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel


class ProductVariantDCO(BaseModel):
    product_id: UUID
    sku: str
    price: Decimal
    currency: str = "CAD"
    moq: int = 1
    barcode: Optional[str] = None
    pack_size: Optional[str] = None
    weight_kg: Optional[Decimal] = None
    is_active: bool = True


class ProductVariantUpdateDCO(BaseModel):
    product_id: Optional[UUID] = None
    sku: Optional[str] = None
    price: Optional[Decimal] = None
    currency: Optional[str] = None
    moq: Optional[int] = None
    barcode: Optional[str] = None
    pack_size: Optional[str] = None
    weight_kg: Optional[Decimal] = None
    is_active: Optional[bool] = None
