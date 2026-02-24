from fastapi import APIRouter, status, Depends, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.auth_dto import RegisterRequestDTO, LoginRequestDTO, RefreshTokenRequestDTO
from app.common.response import respond
from app.core import get_current_user, get_db_session
from app.core.rate_limit import limiter, RateLimits
from app.core.token_blacklist import blacklist_token
from app.core.config import settings
from app.modules.auth import auth_service

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


@router.post("/register", status_code=status.HTTP_201_CREATED)
@limiter.limit(RateLimits.AUTH_REGISTER)
async def register(
    request: Request,
    body: RegisterRequestDTO,
    db: AsyncSession = Depends(get_db_session),
):
    """Register a new user account."""
    user = await auth_service.register_user(db, body)
    return respond(data=user, message="User registered successfully", status_code=201)


@router.post("/login")
@limiter.limit(RateLimits.AUTH_LOGIN)
async def login(
    request: Request,
    body: LoginRequestDTO,
    db: AsyncSession = Depends(get_db_session),
):
    """Login with email and password to get JWT tokens."""
    tokens = await auth_service.login_user(db, body)
    return respond(data=tokens, message="Login successful")


@router.post("/refresh")
@limiter.limit(RateLimits.AUTH_REFRESH)
async def refresh_token(request: Request, body: RefreshTokenRequestDTO):
    """Refresh access token using refresh token."""
    tokens = await auth_service.refresh_user_token(body)
    return respond(data=tokens, message="Token refreshed successfully")


@router.get("/me")
@limiter.limit(RateLimits.API_READ)
async def get_me(
    request: Request,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Get current user profile information."""
    user = await auth_service.get_user_profile(db, current_user["user_id"])
    return respond(data=user, message="User profile fetched")


@router.post("/logout")
@limiter.limit(RateLimits.API_WRITE)
async def logout(
    request: Request,
    current_user: dict = Depends(get_current_user),
    token: str = Depends(oauth2_scheme)
):
    """Logout the current user by blacklisting their access token."""
    expires_in_seconds = settings.access_token_expire_minutes * 60
    blacklist_token(token, expires_in_seconds)

    return respond(
        message="Successfully logged out. Please login again to access protected endpoints.",
        status_code=200
    )
