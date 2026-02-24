"""Auth module — registration, login, JWT tokens, user profiles."""

from app.modules.auth.auth_dto import (
    AdminCreateUserRequestDTO,
    AdminUpdateUserRequestDTO,
    RegisterRequestDTO,
    LoginRequestDTO,
    TokenResponseDTO,
    RefreshTokenRequestDTO,
    UpdateMyProfileRequestDTO,
    UserResponseDTO,
    UserRole,
)
from app.modules.auth.auth_dco import UserDCO
from app.modules.auth.auth_model import (
    create_user,
    find_user_by_email,
    find_user_by_id,
)

__all__ = [
    "RegisterRequestDTO",
    "AdminCreateUserRequestDTO",
    "AdminUpdateUserRequestDTO",
    "LoginRequestDTO",
    "TokenResponseDTO",
    "RefreshTokenRequestDTO",
    "UpdateMyProfileRequestDTO",
    "UserResponseDTO",
    "UserRole",
    "UserDCO",
    "create_user",
    "find_user_by_email",
    "find_user_by_id",
]
