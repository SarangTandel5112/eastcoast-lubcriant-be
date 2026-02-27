"""DTO for the products table — READ operations."""

from uuid import UUID
from datetime import datetime
from typing import Optional

from app.common.schemas.base import BaseSchema

class ProductDTO(BaseSchema):

    id: UUID
    brand_id: UUID
    product_type_id: UUID
    category_id: UUID
    name: str
    slug: str
    short_description: Optional[str] = None
    description: Optional[str] = None
    is_active: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
