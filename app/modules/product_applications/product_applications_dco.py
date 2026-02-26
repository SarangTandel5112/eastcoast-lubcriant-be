"""DCO for the product_applications junction table — WRITE operations."""

from uuid import UUID
from typing import Optional

from app.common.schemas.base import BaseSchema

class ProductApplicationDCO(BaseSchema):
    product_id: UUID
    application_id: UUID

class ProductApplicationUpdateDCO(BaseSchema):
    product_id: Optional[UUID] = None
    application_id: Optional[UUID] = None
