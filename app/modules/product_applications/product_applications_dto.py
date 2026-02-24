"""DTO for the product_applications junction table — READ operations."""

from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ProductApplicationDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    product_id: UUID
    application_id: UUID
