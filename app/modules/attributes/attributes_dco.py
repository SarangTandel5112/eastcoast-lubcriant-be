"""DCO for the attributes table — WRITE operations."""

from typing import Optional

from pydantic import BaseModel

from app.modules.attributes.attributes_entity import DataTypeEnum


class AttributeDCO(BaseModel):
    name: str
    data_type: DataTypeEnum
    unit: Optional[str] = None


class AttributeUpdateDCO(BaseModel):
    name: Optional[str] = None
    data_type: Optional[DataTypeEnum] = None
    unit: Optional[str] = None
