"""DTO for the product_variants table — READ operations."""

from uuid import UUID
from datetime import datetime
from decimal import Decimal
from typing import Optional

from app.common.schemas.base import BaseSchema

class ProductVariantDTO(BaseSchema):

    id: UUID
    product_id: UUID
    sku: str
    price: Decimal
    currency: str
    moq: int
    barcode: Optional[str] = None
    pack_size: Optional[str] = None
    weight_kg: Optional[Decimal] = None
    is_active: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
