"""DCO for the product_applications junction table — WRITE operations."""

from uuid import UUID
from typing import Optional

from pydantic import BaseModel


class ProductApplicationDCO(BaseModel):
    product_id: UUID
    application_id: UUID


class ProductApplicationUpdateDCO(BaseModel):
    product_id: Optional[UUID] = None
    application_id: Optional[UUID] = None
