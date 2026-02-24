from fastapi import APIRouter, status, Depends, Request
from fastapi.security import OAuth2PasswordBearer

from app.modules.auth.auth_dto import RegisterRequestDTO, LoginRequestDTO, RefreshTokenRequestDTO
from app.common.response import respond
from app.core import get_current_user
from app.core.rate_limit import limiter, RateLimits
from app.core.token_blacklist import blacklist_token
from app.core.config import settings
from app.modules.auth import auth_service  # Import service directly

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


@router.post("/register", status_code=status.HTTP_201_CREATED)
@limiter.limit(RateLimits.AUTH_REGISTER)  # 3 registrations per minute per IP
async def register(request: Request, body: RegisterRequestDTO):
    """Register a new user account."""
    user = await auth_service.register_user(body)
    return respond(data=user, message="User registered successfully", status_code=201)


@router.post("/login")
@limiter.limit(RateLimits.AUTH_LOGIN)  # 5 login attempts per minute per IP
async def login(request: Request, body: LoginRequestDTO):
    """Login with email and password to get JWT tokens."""
    tokens = await auth_service.login_user(body)
    return respond(data=tokens, message="Login successful")


@router.post("/refresh")
@limiter.limit(RateLimits.AUTH_REFRESH)  # 10 token refreshes per minute
async def refresh_token(request: Request, body: RefreshTokenRequestDTO):
    """Refresh access token using refresh token."""
    tokens = await auth_service.refresh_user_token(body)
    return respond(data=tokens, message="Token refreshed successfully")


@router.get("/me")
@limiter.limit(RateLimits.API_READ)  # 60 requests per minute
async def get_me(request: Request, current_user: dict = Depends(get_current_user)):
    """Get current user profile information."""
    user = await auth_service.get_user_profile(current_user["user_id"])
    return respond(data=user, message="User profile fetched")


@router.post("/logout")
@limiter.limit(RateLimits.API_WRITE)  # 30 requests per minute
async def logout(
    request: Request,
    current_user: dict = Depends(get_current_user),
    token: str = Depends(oauth2_scheme)
):
    """
    Logout the current user by blacklisting their access token.

    This immediately invalidates the current access token.
    The user will need to login again to get a new token.
    """
    # Calculate remaining token lifetime for blacklist TTL
    expires_in_seconds = settings.access_token_expire_minutes * 60

    # Blacklist the current token
    blacklist_token(token, expires_in_seconds)

    return respond(
        message="Successfully logged out. Please login again to access protected endpoints.",
        status_code=200
    )
