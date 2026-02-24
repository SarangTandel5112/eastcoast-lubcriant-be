"""DCO for the users table — WRITE operations."""

from typing import Optional

from pydantic import BaseModel

from app.modules.users.users_entity import RoleEnum


class UserDCO(BaseModel):
    role: RoleEnum
    business_name: str
    email: str
    password_hash: str
    province: str
    contact_name: Optional[str] = None
    phone: Optional[str] = None
    is_active: bool = True


class UserUpdateDCO(BaseModel):
    role: Optional[RoleEnum] = None
    business_name: Optional[str] = None
    email: Optional[str] = None
    password_hash: Optional[str] = None
    province: Optional[str] = None
    contact_name: Optional[str] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = None
