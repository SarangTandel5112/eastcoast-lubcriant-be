"""DCO for the variant_images table — WRITE operations."""

from uuid import UUID
from typing import Optional

from pydantic import BaseModel


class VariantImageDCO(BaseModel):
    variant_id: UUID
    image_url: str
    alt_text: Optional[str] = None
    display_order: Optional[int] = None


class VariantImageUpdateDCO(BaseModel):
    variant_id: Optional[UUID] = None
    image_url: Optional[str] = None
    alt_text: Optional[str] = None
    display_order: Optional[int] = None
