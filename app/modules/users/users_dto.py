"""DTO for the users table — READ operations."""

from uuid import UUID
from datetime import datetime
from typing import Optional

from app.common.schemas.base import BaseSchema
from app.modules.users.users_entity import RoleEnum

class UserDTO(BaseSchema):

    id: UUID
    role: RoleEnum
    business_name: str
    email: str
    password_hash: str
    province: str
    contact_name: Optional[str] = None
    phone: Optional[str] = None
    is_active: bool
    last_login_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
