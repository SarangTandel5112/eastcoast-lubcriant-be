"""DCO for the inventory_movements table — WRITE operations."""

from uuid import UUID
from typing import Optional

from app.common.schemas.base import BaseSchema
from app.modules.inventory_movements.inventory_movements_entity import MovementTypeEnum

class InventoryMovementDCO(BaseSchema):
    variant_id: UUID
    warehouse_id: UUID
    movement_type: MovementTypeEnum
    quantity: int
    reference_type: Optional[str] = None
    reference_id: Optional[UUID] = None

class InventoryMovementUpdateDCO(BaseSchema):
    variant_id: Optional[UUID] = None
    warehouse_id: Optional[UUID] = None
    movement_type: Optional[MovementTypeEnum] = None
    quantity: Optional[int] = None
    reference_type: Optional[str] = None
    reference_id: Optional[UUID] = None
