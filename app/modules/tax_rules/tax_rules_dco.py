"""DCO for the tax_rules table — WRITE operations."""

from decimal import Decimal
from typing import Optional

from app.common.schemas.base import BaseSchema

class TaxRuleDCO(BaseSchema):
    province: str
    gst_rate: Decimal
    pst_rate: Optional[Decimal] = None
    hst_rate: Optional[Decimal] = None

class TaxRuleUpdateDCO(BaseSchema):
    province: Optional[str] = None
    gst_rate: Optional[Decimal] = None
    pst_rate: Optional[Decimal] = None
    hst_rate: Optional[Decimal] = None
