from loguru import logger

from app.modules.auth.auth_dto import (
    RegisterRequestDTO, LoginRequestDTO, RefreshTokenRequestDTO,
    TokenResponseDTO, UserResponseDTO,
)
from app.modules.auth.auth_dco import UserDCO
from app.core import (
    hash_password, verify_password,
    create_access_token, create_refresh_token,
    decode_token,
)
from app.core.exceptions import (
    ConflictError,
    NotFoundError,
    AuthenticationError,
)
from app.modules.auth.auth_model import create_user, find_user_by_email, find_user_by_id


async def register_user(body: RegisterRequestDTO) -> UserResponseDTO:
    if find_user_by_email(body.email):
        raise ConflictError(
            message="Email already registered",
            resource="user",
            field="email"
        )

    hashed = hash_password(body.password)

    # DTO → DCO
    dco = UserDCO(name=body.name, email=body.email, password=hashed)
    created = create_user(dco)

    logger.info("New user registered | user_id={} email={}", created.id, body.email)
    return UserResponseDTO.from_dco(created)


async def login_user(body: LoginRequestDTO) -> TokenResponseDTO:
    user = find_user_by_email(body.email)
    if not user or not verify_password(body.password, user.password):
        raise AuthenticationError("Invalid email or password")

    token_data = {"sub": user.id, "role": user.role}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    logger.info("User logged in | user_id={}", user.id)
    return TokenResponseDTO(access_token=access_token, refresh_token=refresh_token)


async def refresh_user_token(body: RefreshTokenRequestDTO) -> TokenResponseDTO:
    try:
        payload = decode_token(body.refresh_token)
    except Exception:
        raise AuthenticationError("Invalid or expired refresh token")

    if payload.get("type") != "refresh":
        raise AuthenticationError("Invalid refresh token")

    token_data = {"sub": payload["sub"], "role": payload.get("role", "customer")}
    return TokenResponseDTO(
        access_token=create_access_token(token_data),
        refresh_token=create_refresh_token(token_data),
    )


async def get_user_profile(user_id: str) -> UserResponseDTO:
    user = find_user_by_id(user_id)
    if not user:
        raise NotFoundError("user", user_id)

    return UserResponseDTO.from_dco(user)
