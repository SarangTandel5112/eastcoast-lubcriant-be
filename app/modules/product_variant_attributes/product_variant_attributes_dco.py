"""DCO for the product_variant_attributes junction table — WRITE operations."""

from uuid import UUID
from typing import Optional

from pydantic import BaseModel


class ProductVariantAttributeDCO(BaseModel):
    variant_id: UUID
    attribute_id: UUID
    value: str


class ProductVariantAttributeUpdateDCO(BaseModel):
    variant_id: Optional[UUID] = None
    attribute_id: Optional[UUID] = None
    value: Optional[str] = None
