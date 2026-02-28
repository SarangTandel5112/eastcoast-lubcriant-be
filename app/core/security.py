from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordBearer
from loguru import logger

from app.core.config import settings
from app.core.token_blacklist import is_token_blacklisted, are_user_tokens_revoked
from app.core.exceptions import AuthenticationError, AuthorizationError

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


# ── Password ──────────────────────────────────────────────

def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# ── JWT ───────────────────────────────────────────────────

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    expire = now + (expires_delta or timedelta(minutes=settings.access_token_expire_minutes))
    to_encode.update({
        "exp": expire,
        "iat": now,  # Issued at timestamp (for revocation checking)
        "type": "access"
    })
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def create_refresh_token(data: dict, refresh_jti: str) -> str:
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    expire = now + timedelta(days=settings.refresh_token_expire_days)
    to_encode.update({
        "exp": expire,
        "iat": now,  # Issued at timestamp (for revocation checking)
        "type": "refresh",
        "jti": refresh_jti,
    })
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return payload
    except JWTError:
        raise AuthenticationError("Invalid or expired token")


# ── Dependencies (attach to protected routes) ─────────────

async def get_current_user(request: Request, token: str | None = Depends(oauth2_scheme)) -> dict:
    if not token:
        token = request.cookies.get(settings.access_token_cookie_name)

    if not token:
        raise AuthenticationError("Not authenticated")

    # Check if token is blacklisted (revoked)
    if is_token_blacklisted(token):
        logger.warning("Attempted to use blacklisted token")
        raise AuthenticationError("Token has been revoked. Please login again.")

    payload = decode_token(token)
    user_id: str = payload.get("sub")
    token_issued_at: float = payload.get("iat")

    if not user_id:
        raise AuthenticationError("Invalid token payload")

    # Check if all tokens for this user have been revoked
    # (e.g., after password change)
    if are_user_tokens_revoked(user_id, token_issued_at):
        logger.warning("Attempted to use revoked user token | user_id={}", user_id)
        raise AuthenticationError("All sessions have been terminated. Please login again.")

    return {"user_id": user_id, "role": payload.get("role", "DEALER")}


async def require_admin(current_user: dict = Depends(get_current_user)) -> dict:
    if current_user.get("role") != "ADMIN":
        raise AuthorizationError("Admin access required", required_role="ADMIN")
    return current_user
