"""DTO for the product_images table — READ operations."""

from uuid import UUID
from datetime import datetime
from typing import Optional

from app.common.schemas.base import BaseSchema

class ProductImageDTO(BaseSchema):

    id: UUID
    product_id: UUID
    image_url: str
    alt_text: Optional[str] = None
    display_order: Optional[int] = None
    created_at: Optional[datetime] = None
