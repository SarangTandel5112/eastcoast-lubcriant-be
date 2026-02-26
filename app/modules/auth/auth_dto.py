"""Auth DTOs — request & response Pydantic models for the Auth API."""

from enum import Enum
import re

from pydantic import EmailStr, Field, field_validator, model_validator

from app.common.schemas.base import BaseSchema
from app.modules.auth.auth_dco import UserDCO

class UserRole(str, Enum):
    ADMIN = "ADMIN"
    DEALER = "DEALER"

# ── Request DTOs ─────────────────────────────────────────────

class RegisterRequestDTO(BaseSchema):
    """Public registration DTO (default role: DEALER)."""

    business_name: str = Field(..., min_length=2, max_length=150)
    email: EmailStr
    password: str = Field(
        ...,
        min_length=12,
        max_length=128,
        description=(
            "Password must be 12-128 characters with uppercase, lowercase, "
            "digit, and special character"
        ),
    )
    province: str = Field(..., min_length=2, max_length=100)
    contact_name: str | None = Field(default=None, min_length=2, max_length=100)
    phone: str | None = Field(default=None, max_length=30)

    @field_validator("business_name", "province", "contact_name")
    @classmethod
    def validate_text_fields(cls, value: str | None) -> str | None:
        if value is None:
            return value

        stripped = value.strip()
        if stripped != value:
            raise ValueError("Value cannot have leading or trailing spaces")

        if any(char in stripped for char in ["<", ">", "&", '"', "'"]):
            raise ValueError("Value contains invalid characters")

        return stripped

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str | None) -> str | None:
        if value is None:
            return value

        stripped = value.strip()
        if not re.fullmatch(r"^[+]?[-()\d\s]{7,30}$", stripped):
            raise ValueError("Phone must contain only digits, spaces, +, -, and parentheses")

        return stripped

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, value: str) -> str:
        checks = [
            (r"[A-Z]", "at least one uppercase letter"),
            (r"[a-z]", "at least one lowercase letter"),
            (r"\d", "at least one digit"),
            (r"[!@#$%^&*(),.?\":{}|<>_\-+=\[\]\\/`~;']", "at least one special character"),
        ]

        missing_requirements = [requirement for pattern, requirement in checks if not re.search(pattern, value)]
        if missing_requirements:
            raise ValueError(f"Password must contain: {', '.join(missing_requirements)}")

        common_passwords = {
            "password123!",
            "password1234",
            "admin123!@#",
            "welcome123!",
            "p@ssw0rd123",
            "qwerty123!@#",
            "12345678!@#",
            "passw0rd!@#",
        }

        if value.lower() in common_passwords:
            raise ValueError("Password is too common, please choose a stronger password")

        return value

class AdminCreateUserRequestDTO(RegisterRequestDTO):
    """Admin-only user creation DTO."""

    role: UserRole = UserRole.DEALER
    is_active: bool = True

class LoginRequestDTO(BaseSchema):
    """DTO for user login."""

    email: EmailStr | None = None
    phone: str | None = None
    identifier: str | None = None
    password: str

    @field_validator("phone")
    @classmethod
    def validate_login_phone(cls, value: str | None) -> str | None:
        if value is None:
            return value

        stripped = value.strip()
        if not re.fullmatch(r"^[+]?[-()\d\s]{7,30}$", stripped):
            raise ValueError("Phone must contain only digits, spaces, +, -, and parentheses")
        return stripped

    @field_validator("identifier")
    @classmethod
    def validate_identifier(cls, value: str | None) -> str | None:
        if value is None:
            return value
        stripped = value.strip()
        if not stripped:
            raise ValueError("identifier cannot be empty")
        return stripped

    @model_validator(mode="after")
    def validate_login_identifier(self):
        if not self.email and not self.phone and not self.identifier:
            raise ValueError("Provide either email, phone, or identifier (email/phone)")
        return self

class RefreshTokenRequestDTO(BaseSchema):
    """DTO for refreshing a JWT token pair."""

    refresh_token: str

class UpdateMyProfileRequestDTO(BaseSchema):
    """Self-service profile updates for authenticated users."""

    business_name: str | None = Field(default=None, min_length=2, max_length=150)
    province: str | None = Field(default=None, min_length=2, max_length=100)
    contact_name: str | None = Field(default=None, min_length=2, max_length=100)
    phone: str | None = Field(default=None, max_length=30)

    @field_validator("business_name", "province", "contact_name")
    @classmethod
    def validate_optional_text_fields(cls, value: str | None) -> str | None:
        if value is None:
            return value

        stripped = value.strip()
        if stripped != value:
            raise ValueError("Value cannot have leading or trailing spaces")

        if any(char in stripped for char in ["<", ">", "&", '"', "'"]):
            raise ValueError("Value contains invalid characters")

        return stripped

    @field_validator("phone")
    @classmethod
    def validate_optional_phone(cls, value: str | None) -> str | None:
        if value is None:
            return value

        stripped = value.strip()
        if not re.fullmatch(r"^[+]?[-()\d\s]{7,30}$", stripped):
            raise ValueError("Phone must contain only digits, spaces, +, -, and parentheses")

        return stripped

class AdminUpdateUserRequestDTO(BaseSchema):
    """Admin-only user updates."""

    role: UserRole | None = None
    is_active: bool | None = None
    business_name: str | None = Field(default=None, min_length=2, max_length=150)
    province: str | None = Field(default=None, min_length=2, max_length=100)
    contact_name: str | None = Field(default=None, min_length=2, max_length=100)
    phone: str | None = Field(default=None, max_length=30)
    password: str | None = Field(default=None, min_length=12, max_length=128)

    @field_validator("business_name", "province", "contact_name")
    @classmethod
    def validate_admin_optional_text_fields(cls, value: str | None) -> str | None:
        if value is None:
            return value

        stripped = value.strip()
        if stripped != value:
            raise ValueError("Value cannot have leading or trailing spaces")

        if any(char in stripped for char in ["<", ">", "&", '"', "'"]):
            raise ValueError("Value contains invalid characters")

        return stripped

    @field_validator("phone")
    @classmethod
    def validate_admin_optional_phone(cls, value: str | None) -> str | None:
        if value is None:
            return value

        stripped = value.strip()
        if not re.fullmatch(r"^[+]?[-()\d\s]{7,30}$", stripped):
            raise ValueError("Phone must contain only digits, spaces, +, -, and parentheses")

        return stripped

# ── Response DTOs ────────────────────────────────────────────

class TokenResponseDTO(BaseSchema):
    """DTO for JWT token response."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class UserResponseDTO(BaseSchema):
    """DTO returned for user profile information."""

    id: str
    role: str
    business_name: str
    email: str
    province: str
    contact_name: str | None = None
    phone: str | None = None
    is_active: bool
    last_login_at: str | None = None
    created_at: str
    updated_at: str
    deleted_at: str | None = None

    @classmethod
    def from_dco(cls, dco: UserDCO) -> "UserResponseDTO":
        """Build a response DTO from a user DCO."""
        return cls(
            id=dco.id,
            role=dco.role,
            business_name=dco.business_name,
            email=dco.email,
            province=dco.province,
            contact_name=dco.contact_name,
            phone=dco.phone,
            is_active=dco.is_active,
            last_login_at=dco.last_login_at,
            created_at=dco.created_at,
            updated_at=dco.updated_at,
            deleted_at=dco.deleted_at,
        )
