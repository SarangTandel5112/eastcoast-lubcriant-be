"""DTO for the applications table — READ operations."""

from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ApplicationDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
