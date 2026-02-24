"""DTO for the product_variant_standards junction table — READ operations."""

from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ProductVariantStandardDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    variant_id: UUID
    standard_id: UUID
