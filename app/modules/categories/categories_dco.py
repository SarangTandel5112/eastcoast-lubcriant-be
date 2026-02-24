"""DCO for the categories table — WRITE operations."""

from uuid import UUID
from typing import Optional

from pydantic import BaseModel


class CategoryDCO(BaseModel):
    name: str
    slug: str
    parent_id: Optional[UUID] = None
    sort_order: Optional[int] = None


class CategoryUpdateDCO(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    parent_id: Optional[UUID] = None
    sort_order: Optional[int] = None
