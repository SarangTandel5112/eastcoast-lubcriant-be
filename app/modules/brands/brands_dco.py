"""DCO for the brands table — WRITE operations."""

from typing import Optional

from pydantic import BaseModel


class BrandDCO(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    logo_url: Optional[str] = None


class BrandUpdateDCO(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    logo_url: Optional[str] = None
