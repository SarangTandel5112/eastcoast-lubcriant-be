"""DCO for the applications table — WRITE operations."""

from typing import Optional

from pydantic import BaseModel


class ApplicationDCO(BaseModel):
    name: str


class ApplicationUpdateDCO(BaseModel):
    name: Optional[str] = None
