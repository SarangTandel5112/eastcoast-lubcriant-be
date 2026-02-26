"""DCO for the product_variant_standards junction table — WRITE operations."""

from uuid import UUID
from typing import Optional

from app.common.schemas.base import BaseSchema

class ProductVariantStandardDCO(BaseSchema):
    variant_id: UUID
    standard_id: UUID

class ProductVariantStandardUpdateDCO(BaseSchema):
    variant_id: Optional[UUID] = None
    standard_id: Optional[UUID] = None
