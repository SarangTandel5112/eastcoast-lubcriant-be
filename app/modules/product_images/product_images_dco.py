"""DCO for the product_images table — WRITE operations."""

from uuid import UUID
from typing import Optional

from app.common.schemas.base import BaseSchema

class ProductImageDCO(BaseSchema):
    product_id: UUID
    image_url: str
    alt_text: Optional[str] = None
    display_order: Optional[int] = None

class ProductImageUpdateDCO(BaseSchema):
    product_id: Optional[UUID] = None
    image_url: Optional[str] = None
    alt_text: Optional[str] = None
    display_order: Optional[int] = None
