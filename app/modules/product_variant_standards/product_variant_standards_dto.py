"""DTO for the product_variant_standards junction table — READ operations."""

from uuid import UUID

from app.common.schemas.base import BaseSchema

class ProductVariantStandardDTO(BaseSchema):

    variant_id: UUID
    standard_id: UUID
