from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.security import OAuth2PasswordBearer

from app.common.response import respond
from app.core import get_current_user, require_admin
from app.core.config import settings
from app.core.rate_limit import RateLimits, limiter
from app.core.token_blacklist import blacklist_token
from app.modules.auth import auth_service
from app.modules.auth.auth_dto import (
    AdminCreateUserRequestDTO,
    AdminUpdateUserRequestDTO,
    LoginRequestDTO,
    RefreshTokenRequestDTO,
    RegisterRequestDTO,
    UpdateMyProfileRequestDTO,
    UserRole,
)

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


def _cookie_domain() -> str | None:
    domain = settings.cookie_domain.strip()
    return domain or None


def _set_auth_cookies(response, access_token: str, refresh_token: str) -> None:
    response.set_cookie(
        key=settings.access_token_cookie_name,
        value=access_token,
        max_age=settings.access_token_expire_minutes * 60,
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
        path="/",
        domain=_cookie_domain(),
    )
    response.set_cookie(
        key=settings.refresh_token_cookie_name,
        value=refresh_token,
        max_age=settings.refresh_token_expire_days * 24 * 60 * 60,
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
        path="/",
        domain=_cookie_domain(),
    )


def _clear_auth_cookies(response) -> None:
    response.delete_cookie(
        key=settings.access_token_cookie_name,
        path="/",
        domain=_cookie_domain(),
    )
    response.delete_cookie(
        key=settings.refresh_token_cookie_name,
        path="/",
        domain=_cookie_domain(),
    )


@router.post("/register", status_code=status.HTTP_201_CREATED)
@limiter.limit(RateLimits.AUTH_REGISTER)
async def register(request: Request, body: RegisterRequestDTO):
    """Public registration endpoint (creates DEALER users)."""
    user = await auth_service.register_user(body)
    return respond(data=user, message="User registered successfully", status_code=201)


@router.post("/login")
@limiter.limit(RateLimits.AUTH_LOGIN)
async def login(request: Request, body: LoginRequestDTO):
    """Login with email and password to get JWT access + refresh tokens."""
    tokens = await auth_service.login_user(body)
    response = respond(data=tokens, message="Login successful")
    _set_auth_cookies(response, tokens.access_token, tokens.refresh_token)
    return response


@router.post("/refresh")
@limiter.limit(RateLimits.AUTH_REFRESH)
async def refresh_token(request: Request, body: RefreshTokenRequestDTO | None = None):
    """Rotate refresh token and issue a fresh access token pair."""
    refresh_token_value = None
    if body:
        refresh_token_value = body.refresh_token
    if not refresh_token_value:
        refresh_token_value = request.cookies.get(settings.refresh_token_cookie_name)
    if not refresh_token_value:
        refresh_token_value = request.headers.get("X-Refresh-Token")
    if not refresh_token_value:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token required")

    tokens = await auth_service.refresh_user_token(
        RefreshTokenRequestDTO(refresh_token=refresh_token_value)
    )
    response = respond(data=tokens, message="Token refreshed successfully")
    _set_auth_cookies(response, tokens.access_token, tokens.refresh_token)
    return response


@router.post("/logout")
@limiter.limit(RateLimits.API_WRITE)
async def logout(
    request: Request,
    current_user: dict = Depends(get_current_user),
    token: str | None = Depends(oauth2_scheme),
):
    """Logout current session by revoking access token and refresh token chain."""
    access_token = token or request.cookies.get(settings.access_token_cookie_name)
    if access_token:
        expires_in_seconds = settings.access_token_expire_minutes * 60
        blacklist_token(access_token, expires_in_seconds)
    await auth_service.logout_user(current_user["user_id"])

    response = respond(
        message="Successfully logged out. Please login again to access protected endpoints.",
        status_code=200,
    )
    _clear_auth_cookies(response)
    return response


@router.get("/me")
@limiter.limit(RateLimits.API_READ)
async def get_me(request: Request, current_user: dict = Depends(get_current_user)):
    """Get current authenticated user profile."""
    user = await auth_service.get_user_profile(current_user["user_id"])
    return respond(data=user, message="User profile fetched")


@router.patch("/me")
@limiter.limit(RateLimits.API_WRITE)
async def update_me(
    request: Request,
    body: UpdateMyProfileRequestDTO,
    current_user: dict = Depends(get_current_user),
):
    """Update current authenticated user's own profile."""
    user = await auth_service.update_my_profile(current_user, body)
    return respond(data=user, message="Profile updated successfully")


@router.post("/users", status_code=status.HTTP_201_CREATED)
@limiter.limit(RateLimits.API_WRITE)
async def create_user_by_admin(
    request: Request,
    body: AdminCreateUserRequestDTO,
    admin: dict = Depends(require_admin),
):
    """Create a user as admin (ADMIN/DEALER)."""
    user = await auth_service.create_user_by_admin(body, admin)
    return respond(data=user, message="User created successfully", status_code=201)


@router.get("/users")
@limiter.limit(RateLimits.API_READ)
async def get_users(
    request: Request,
    role: UserRole | None = Query(default=None),
    is_active: bool | None = Query(default=None),
    admin: dict = Depends(require_admin),
):
    """List users (admin only)."""
    users = await auth_service.list_users_for_admin(
        admin,
        role.value if role else None,
        is_active,
    )
    return respond(data=users, message="Users fetched")


@router.get("/users/{user_id}")
@limiter.limit(RateLimits.API_READ)
async def get_user_by_id(
    request: Request,
    user_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Get user by ID (self or admin)."""
    user = await auth_service.get_user_by_id(user_id, current_user)
    return respond(data=user, message="User fetched")


@router.patch("/users/{user_id}")
@limiter.limit(RateLimits.API_WRITE)
async def update_user_by_admin(
    request: Request,
    user_id: str,
    body: AdminUpdateUserRequestDTO,
    admin: dict = Depends(require_admin),
):
    """Update user as admin."""
    user = await auth_service.update_user_by_admin(user_id, body, admin)
    return respond(data=user, message="User updated successfully")


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit(RateLimits.API_DELETE)
async def delete_user_by_admin(
    request: Request,
    user_id: str,
    admin: dict = Depends(require_admin),
):
    """Soft-delete user as admin."""
    await auth_service.delete_user_by_admin(user_id, admin)
