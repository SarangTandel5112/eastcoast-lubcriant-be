"""DTO for the dealer_addresses table — READ operations."""

from uuid import UUID
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class DealerAddressDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    dealer_id: UUID
    address_line1: str
    city: str
    province: str
    postal_code: str
    country: str
    label: Optional[str] = None
    address_line2: Optional[str] = None
    is_default: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
