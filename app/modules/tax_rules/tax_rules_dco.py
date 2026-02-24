"""DCO for the tax_rules table — WRITE operations."""

from decimal import Decimal
from typing import Optional

from pydantic import BaseModel


class TaxRuleDCO(BaseModel):
    province: str
    gst_rate: Decimal
    pst_rate: Optional[Decimal] = None
    hst_rate: Optional[Decimal] = None


class TaxRuleUpdateDCO(BaseModel):
    province: Optional[str] = None
    gst_rate: Optional[Decimal] = None
    pst_rate: Optional[Decimal] = None
    hst_rate: Optional[Decimal] = None
