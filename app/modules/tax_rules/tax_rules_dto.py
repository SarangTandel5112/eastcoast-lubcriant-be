"""DTO for the tax_rules table — READ operations."""

from uuid import UUID
from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict


class TaxRuleDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    province: str
    gst_rate: Decimal
    pst_rate: Optional[Decimal] = None
    hst_rate: Optional[Decimal] = None
    created_at: Optional[datetime] = None
