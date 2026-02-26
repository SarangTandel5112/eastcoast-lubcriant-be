"""DTO for the product_variant_attributes junction table — READ operations."""

from uuid import UUID

from app.common.schemas.base import BaseSchema

class ProductVariantAttributeDTO(BaseSchema):

    variant_id: UUID
    attribute_id: UUID
    value: str
