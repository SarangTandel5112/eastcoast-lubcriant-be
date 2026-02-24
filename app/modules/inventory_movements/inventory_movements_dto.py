"""DTO for the inventory_movements table — READ operations."""

from uuid import UUID
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.modules.inventory_movements.inventory_movements_entity import MovementTypeEnum


class InventoryMovementDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    variant_id: UUID
    warehouse_id: UUID
    movement_type: MovementTypeEnum
    quantity: int
    reference_type: Optional[str] = None
    reference_id: Optional[UUID] = None
    created_at: Optional[datetime] = None
