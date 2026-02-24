"""DTO for the product_variant_attributes junction table — READ operations."""

from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ProductVariantAttributeDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    variant_id: UUID
    attribute_id: UUID
    value: str
