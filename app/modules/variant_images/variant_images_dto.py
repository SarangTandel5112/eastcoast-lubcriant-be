"""DTO for the variant_images table — READ operations."""

from uuid import UUID
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class VariantImageDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    variant_id: UUID
    image_url: str
    alt_text: Optional[str] = None
    display_order: Optional[int] = None
    created_at: Optional[datetime] = None
