"""DCO for the attributes table — WRITE operations."""

from typing import Optional

from app.common.schemas.base import BaseSchema

from app.modules.attributes.attributes_entity import DataTypeEnum

class AttributeDCO(BaseSchema):
    name: str
    data_type: DataTypeEnum
    unit: Optional[str] = None

class AttributeUpdateDCO(BaseSchema):
    name: Optional[str] = None
    data_type: Optional[DataTypeEnum] = None
    unit: Optional[str] = None
