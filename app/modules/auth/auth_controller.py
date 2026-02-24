from app.modules.auth import auth_service
from app.modules.auth.auth_dto import (
    RegisterRequestDTO, LoginRequestDTO, RefreshTokenRequestDTO,
    TokenResponseDTO, UserResponseDTO,
)


async def register_user(body: RegisterRequestDTO) -> UserResponseDTO:
    return await auth_service.register_user(body)


async def login_user(body: LoginRequestDTO) -> TokenResponseDTO:
    return await auth_service.login_user(body)


async def refresh_user_token(body: RefreshTokenRequestDTO) -> TokenResponseDTO:
    return await auth_service.refresh_user_token(body)


async def get_user_profile(user_id: str) -> UserResponseDTO:
    return await auth_service.get_user_profile(user_id)
