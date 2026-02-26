"""DCO for the brands table — WRITE operations."""

from typing import Optional

from app.common.schemas.base import BaseSchema

class BrandDCO(BaseSchema):
    name: str
    slug: str
    description: Optional[str] = None
    logo_url: Optional[str] = None

class BrandUpdateDCO(BaseSchema):
    name: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    logo_url: Optional[str] = None
