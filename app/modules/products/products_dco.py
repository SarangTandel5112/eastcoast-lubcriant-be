"""DCO for the products table — WRITE operations."""

from uuid import UUID
from typing import Optional

from app.common.schemas.base import BaseSchema

class ProductDCO(BaseSchema):
    brand_id: UUID
    product_type_id: UUID
    category_id: UUID
    name: str
    slug: str
    short_description: Optional[str] = None
    description: Optional[str] = None
    is_active: bool = True

class ProductUpdateDCO(BaseSchema):
    brand_id: Optional[UUID] = None
    product_type_id: Optional[UUID] = None
    category_id: Optional[UUID] = None
    name: Optional[str] = None
    slug: Optional[str] = None
    short_description: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
