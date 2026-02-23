from fastapi import APIRouter, status, Depends

from app.schemas import RegisterSchema, LoginSchema, RefreshTokenSchema, TokenSchema, UserResponseSchema
from app.core import get_current_user
from app.controllers import auth_controller

router = APIRouter()


@router.post("/register", response_model=UserResponseSchema, status_code=status.HTTP_201_CREATED)
async def register(body: RegisterSchema):
    return await auth_controller.register_user(body)


@router.post("/login", response_model=TokenSchema)
async def login(body: LoginSchema):
    return await auth_controller.login_user(body)


@router.post("/refresh", response_model=TokenSchema)
async def refresh_token(body: RefreshTokenSchema):
    return await auth_controller.refresh_user_token(body)


@router.get("/me", response_model=UserResponseSchema)
async def get_me(current_user: dict = Depends(get_current_user)):
    return await auth_controller.get_user_profile(current_user["user_id"])
