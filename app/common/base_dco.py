"""Base Domain Class Object with shared fields."""

from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class BaseDCO:
    """Common fields shared by all domain objects."""
    id: str = ""
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
