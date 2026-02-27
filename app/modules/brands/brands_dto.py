"""DTO for the brands table — READ operations."""

from uuid import UUID
from datetime import datetime
from typing import Optional

from app.common.schemas.base import BaseSchema

class BrandDTO(BaseSchema):

    id: UUID
    name: str
    slug: str
    description: Optional[str] = None
    logo_url: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
