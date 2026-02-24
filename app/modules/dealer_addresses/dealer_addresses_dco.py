"""DCO for the dealer_addresses table — WRITE operations."""

from uuid import UUID
from typing import Optional

from pydantic import BaseModel


class DealerAddressDCO(BaseModel):
    dealer_id: UUID
    address_line1: str
    city: str
    province: str
    postal_code: str
    country: str
    label: Optional[str] = None
    address_line2: Optional[str] = None
    is_default: Optional[bool] = None


class DealerAddressUpdateDCO(BaseModel):
    dealer_id: Optional[UUID] = None
    address_line1: Optional[str] = None
    city: Optional[str] = None
    province: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    label: Optional[str] = None
    address_line2: Optional[str] = None
    is_default: Optional[bool] = None
