from fastapi import APIRouter, status, Depends

from app.modules.auth.auth_dto import RegisterRequestDTO, LoginRequestDTO, RefreshTokenRequestDTO
from app.common.response import respond
from app.core import get_current_user
from app.modules.auth import auth_controller

router = APIRouter()


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(body: RegisterRequestDTO):
    user = await auth_controller.register_user(body)
    return respond(data=user, message="User registered successfully", status_code=201)


@router.post("/login")
async def login(body: LoginRequestDTO):
    tokens = await auth_controller.login_user(body)
    return respond(data=tokens, message="Login successful")


@router.post("/refresh")
async def refresh_token(body: RefreshTokenRequestDTO):
    tokens = await auth_controller.refresh_user_token(body)
    return respond(data=tokens, message="Token refreshed successfully")


@router.get("/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    user = await auth_controller.get_user_profile(current_user["user_id"])
    return respond(data=user, message="User profile fetched")
