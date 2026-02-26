"""DTO for the product_applications junction table — READ operations."""

from uuid import UUID

from app.common.schemas.base import BaseSchema

class ProductApplicationDTO(BaseSchema):

    product_id: UUID
    application_id: UUID
