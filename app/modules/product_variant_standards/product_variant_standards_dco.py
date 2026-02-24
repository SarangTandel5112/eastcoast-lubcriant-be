"""DCO for the product_variant_standards junction table — WRITE operations."""

from uuid import UUID
from typing import Optional

from pydantic import BaseModel


class ProductVariantStandardDCO(BaseModel):
    variant_id: UUID
    standard_id: UUID


class ProductVariantStandardUpdateDCO(BaseModel):
    variant_id: Optional[UUID] = None
    standard_id: Optional[UUID] = None
