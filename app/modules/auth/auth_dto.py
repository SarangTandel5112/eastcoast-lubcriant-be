"""Auth DTOs — request & response Pydantic models for the Auth API."""

from pydantic import BaseModel, EmailStr, Field

from app.modules.auth.auth_dco import UserDCO


# ── Request DTOs ─────────────────────────────────────────────

class RegisterRequestDTO(BaseModel):
    """DTO for user registration."""
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8)


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
