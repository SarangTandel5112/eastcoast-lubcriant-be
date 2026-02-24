"""Auth DTOs — request & response Pydantic models for the Auth API."""

from pydantic import BaseModel, EmailStr, Field, validator
import re

from app.modules.auth.auth_dco import UserDCO


# ── Request DTOs ─────────────────────────────────────────────

class RegisterRequestDTO(BaseModel):
    """DTO for user registration."""
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(
        ...,
        min_length=12,
        max_length=128,
        description="Password must be 12-128 characters with uppercase, lowercase, digit, and special character"
    )

    @validator("name")
    def validate_name(cls, v):
        """Validate name has no leading/trailing spaces and valid characters."""
        if v.strip() != v:
            raise ValueError("Name cannot have leading or trailing spaces")

        # Check for suspicious characters (basic XSS prevention)
        if any(char in v for char in ["<", ">", "&", '"', "'"]):
            raise ValueError("Name contains invalid characters")

        return v.strip()

    @validator("password")
    def validate_password_strength(cls, v):
        """Enforce strong password policy."""
        if len(v) < 12:
            raise ValueError("Password must be at least 12 characters long")

        if len(v) > 128:
            raise ValueError("Password must not exceed 128 characters")

        # Check for required character types
        checks = [
            (r"[A-Z]", "at least one uppercase letter"),
            (r"[a-z]", "at least one lowercase letter"),
            (r"\d", "at least one digit"),
            (r"[!@#$%^&*(),.?\":{}|<>_\-+=\[\]\\\/`~;']", "at least one special character"),
        ]

        missing_requirements = []
        for pattern, requirement in checks:
            if not re.search(pattern, v):
                missing_requirements.append(requirement)

        if missing_requirements:
            raise ValueError(
                f"Password must contain: {', '.join(missing_requirements)}"
            )

        # Check against common weak passwords
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

        if v.lower() in common_passwords:
            raise ValueError("Password is too common, please choose a stronger password")

        # Check for sequential characters (like "12345" or "abcde")
        if any(v.lower()[i:i+4] in "0123456789abcdefghijklmnopqrstuvwxyz" for i in range(len(v)-3)):
            raise ValueError("Password contains sequential characters, please use a more complex password")

        return v


class LoginRequestDTO(BaseModel):
    """DTO for user login."""
    email: EmailStr
    password: str


class RefreshTokenRequestDTO(BaseModel):
    """DTO for refreshing a JWT token pair."""
    refresh_token: str


# ── Response DTOs ────────────────────────────────────────────

class TokenResponseDTO(BaseModel):
    """DTO for JWT token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserResponseDTO(BaseModel):
    """DTO returned for user profile information."""
    id: str
    name: str
    email: str
    role: str = "customer"

    @classmethod
    def from_dco(cls, dco: UserDCO) -> "UserResponseDTO":
        """Build a response DTO from a user DCO."""
        return cls(
            id=dco.id,
            name=dco.name,
            email=dco.email,
            role=dco.role,
        )
