"""DTO for the categories table — READ operations."""

from uuid import UUID
from datetime import datetime
from typing import Optional

from app.common.schemas.base import BaseSchema

class CategoryDTO(BaseSchema):

    id: UUID
    name: str
    slug: str
    parent_id: Optional[UUID] = None
    sort_order: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
