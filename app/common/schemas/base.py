"""Base Pydantic schema for all DTOs and DCOs."""

from pydantic import BaseModel, ConfigDict


def to_camel(string: str) -> str:
    """
    Convert snake_case to camelCase.
    Example: brand_id -> brandId
    """
    components = string.split("_")
    if len(components) == 1:
        return components[0]
    return components[0] + "".join(x.title() for x in components[1:])


class BaseSchema(BaseModel):
    """
    Standard BaseSchema that all DTOs and DCOs should inherit from.
    - Automatically converts snake_case fields to camelCase for the API.
    - Allows populating models using either snake_case or camelCase.
    - Enables from_attributes=True for SQLAlchemy compatibility.
    """
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
        str_strip_whitespace=True,
        validate_assignment=True,
    )
