"""DCO for the product_variant_attributes junction table — WRITE operations."""

from uuid import UUID
from typing import Optional

from app.common.schemas.base import BaseSchema

class ProductVariantAttributeDCO(BaseSchema):
    variant_id: UUID
    attribute_id: UUID
    value: str

class ProductVariantAttributeUpdateDCO(BaseSchema):
    variant_id: Optional[UUID] = None
    attribute_id: Optional[UUID] = None
    value: Optional[str] = None
