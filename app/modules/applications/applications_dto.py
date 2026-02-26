"""DTO for the applications table — READ operations."""

from uuid import UUID

from app.common.schemas.base import BaseSchema

class ApplicationDTO(BaseSchema):

    id: UUID
    name: str
