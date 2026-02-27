"""DCO for the variant_images table — WRITE operations."""

from uuid import UUID
from typing import Optional

from app.common.schemas.base import BaseSchema

class VariantImageDCO(BaseSchema):
    variant_id: UUID
    image_url: str
    alt_text: Optional[str] = None
    display_order: Optional[int] = None

class VariantImageUpdateDCO(BaseSchema):
    variant_id: Optional[UUID] = None
    image_url: Optional[str] = None
    alt_text: Optional[str] = None
    display_order: Optional[int] = None
