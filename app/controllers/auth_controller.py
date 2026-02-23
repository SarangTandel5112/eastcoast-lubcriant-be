from fastapi import status
from loguru import logger

from app.schemas import RegisterSchema, LoginSchema, RefreshTokenSchema, TokenSchema, UserResponseSchema
from app.core import (
    hash_password, verify_password,
    create_access_token, create_refresh_token,
    decode_token,
)
from app.core.exceptions import (
    ConflictError,
    NotFoundError,
    AuthenticationError,
    ValidationError,
    UserValidationError
)
from app.models import create_user, find_user_by_email, find_user_by_id


async def register_user(body: RegisterSchema) -> UserResponseSchema:
    if find_user_by_email(body.email):
        raise ConflictError(
            message="Email already registered",
            resource="user",
            field="email"
        )

    hashed = hash_password(body.password)
    user = create_user(name=body.name, email=body.email, hashed_password=hashed)
    logger.info("New user registered | user_id={} email={}", user["id"], body.email)

    return UserResponseSchema(**user)


async def login_user(body: LoginSchema) -> TokenSchema:
    user = find_user_by_email(body.email)
    if not user or not verify_password(body.password, user["password"]):
        raise AuthenticationError("Invalid email or password")

    token_data = {"sub": user["id"], "role": user["role"]}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    logger.info("User logged in | user_id={}", user["id"])
    return TokenSchema(access_token=access_token, refresh_token=refresh_token)


async def refresh_user_token(body: RefreshTokenSchema) -> TokenSchema:
    try:
        payload = decode_token(body.refresh_token)
    except Exception:
        raise AuthenticationError("Invalid or expired refresh token")
    
    if payload.get("type") != "refresh":
        raise AuthenticationError("Invalid refresh token")

    token_data = {"sub": payload["sub"], "role": payload.get("role", "customer")}
    return TokenSchema(
        access_token=create_access_token(token_data),
        refresh_token=create_refresh_token(token_data),
    )


async def get_user_profile(user_id: str) -> UserResponseSchema:
    user = find_user_by_id(user_id)
    if not user:
        raise NotFoundError("user", user_id)

    return UserResponseSchema(**user)
