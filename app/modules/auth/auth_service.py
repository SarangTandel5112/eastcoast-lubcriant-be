from uuid import uuid4

from loguru import logger

from app.core import create_access_token, create_refresh_token, decode_token, hash_password, verify_password
from app.core.exceptions import AuthenticationError, AuthorizationError, ConflictError, NotFoundError
from app.modules.auth.auth_dco import UserDCO
from app.modules.auth.auth_dto import (
    AdminCreateUserRequestDTO,
    AdminUpdateUserRequestDTO,
    LoginRequestDTO,
    RefreshTokenRequestDTO,
    RegisterRequestDTO,
    TokenResponseDTO,
    UpdateMyProfileRequestDTO,
    UserResponseDTO,
)
from app.modules.auth.auth_model import (
    create_user,
    find_user_by_email,
    find_user_by_id,
    find_users_by_phone,
    list_users,
    set_current_refresh_jti,
    set_last_login,
    soft_delete_user,
    update_user,
)


def _issue_token_pair(user: UserDCO) -> TokenResponseDTO:
    refresh_jti = str(uuid4())
    token_data = {"sub": user.id, "role": user.role}

    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data, refresh_jti)

    set_current_refresh_jti(user.id, refresh_jti)

    return TokenResponseDTO(access_token=access_token, refresh_token=refresh_token)


def _assert_phone_available(phone: str | None, exclude_user_id: str | None = None) -> None:
    if not phone:
        return

    existing = find_users_by_phone(phone, include_deleted=False)
    for user in existing:
        if exclude_user_id and user.id == exclude_user_id:
            continue
        raise ConflictError(message="Phone already registered", resource="user", field="phone")


async def register_user(body: RegisterRequestDTO) -> UserResponseDTO:
    if find_user_by_email(body.email, include_deleted=True):
        raise ConflictError(message="Email already registered", resource="user", field="email")
    _assert_phone_available(body.phone)

    hashed = hash_password(body.password)

    dco = UserDCO(
        role="DEALER",
        business_name=body.business_name,
        email=body.email,
        password_hash=hashed,
        province=body.province,
        contact_name=body.contact_name,
        phone=body.phone,
        is_active=True,
    )
    created = create_user(dco)

    logger.info("User registered | user_id={} email={}", created.id, created.email)
    return UserResponseDTO.from_dco(created)


async def create_user_by_admin(body: AdminCreateUserRequestDTO, admin_user: dict) -> UserResponseDTO:
    if admin_user.get("role") != "ADMIN":
        raise AuthorizationError("Only admins can create users", required_role="ADMIN")

    if find_user_by_email(body.email, include_deleted=True):
        raise ConflictError(message="Email already registered", resource="user", field="email")
    _assert_phone_available(body.phone)

    dco = UserDCO(
        role=body.role.value,
        business_name=body.business_name,
        email=body.email,
        password_hash=hash_password(body.password),
        province=body.province,
        contact_name=body.contact_name,
        phone=body.phone,
        is_active=body.is_active,
    )
    created = create_user(dco)

    logger.info(
        "User created by admin | admin_id={} user_id={} role={}",
        admin_user["user_id"],
        created.id,
        created.role,
    )
    return UserResponseDTO.from_dco(created)


async def login_user(body: LoginRequestDTO) -> TokenResponseDTO:
    lookup_email = body.email
    lookup_phone = body.phone

    if body.identifier:
        if "@" in body.identifier:
            lookup_email = body.identifier
        else:
            lookup_phone = body.identifier

    user = None
    if lookup_email:
        user = find_user_by_email(lookup_email)
    elif lookup_phone:
        candidates = find_users_by_phone(lookup_phone)
        if len(candidates) > 1:
            raise AuthenticationError("Multiple accounts use this phone. Please login with email")
        if candidates:
            user = candidates[0]

    if not user or not verify_password(body.password, user.password_hash):
        raise AuthenticationError("Invalid email or password")

    if not user.is_active:
        raise AuthenticationError("Account is inactive. Contact administrator")

    set_last_login(user.id)
    user = find_user_by_id(user.id)
    if not user:
        raise AuthenticationError("Unable to load user session")

    logger.info("User logged in | user_id={} role={}", user.id, user.role)
    return _issue_token_pair(user)


async def refresh_user_token(body: RefreshTokenRequestDTO) -> TokenResponseDTO:
    try:
        payload = decode_token(body.refresh_token)
    except Exception as exc:
        raise AuthenticationError("Invalid or expired refresh token") from exc

    if payload.get("type") != "refresh":
        raise AuthenticationError("Invalid refresh token type")

    user_id = payload.get("sub")
    refresh_jti = payload.get("jti")
    if not user_id or not refresh_jti:
        raise AuthenticationError("Malformed refresh token")

    user = find_user_by_id(user_id)
    if not user:
        raise AuthenticationError("Invalid refresh token")

    if not user.is_active:
        raise AuthenticationError("Account is inactive. Contact administrator")

    if user.current_refresh_jti != refresh_jti:
        raise AuthenticationError("Refresh token already rotated or revoked")

    logger.info("Token refreshed | user_id={}", user.id)
    return _issue_token_pair(user)


async def logout_user(user_id: str) -> None:
    set_current_refresh_jti(user_id, None)
    logger.info("User logged out | user_id={}", user_id)


async def get_user_profile(user_id: str) -> UserResponseDTO:
    user = find_user_by_id(user_id)
    if not user:
        raise NotFoundError("user", user_id)

    return UserResponseDTO.from_dco(user)


async def list_users_for_admin(current_user: dict, role: str | None, is_active: bool | None) -> list[UserResponseDTO]:
    if current_user.get("role") != "ADMIN":
        raise AuthorizationError("Only admins can list users", required_role="ADMIN")

    users = list_users(role=role, is_active=is_active)
    return [UserResponseDTO.from_dco(user) for user in users]


async def get_user_by_id(target_user_id: str, current_user: dict) -> UserResponseDTO:
    is_owner = current_user.get("user_id") == target_user_id
    is_admin = current_user.get("role") == "ADMIN"

    if not is_owner and not is_admin:
        raise AuthorizationError("You can only access your own user record", required_role="ADMIN")

    user = find_user_by_id(target_user_id)
    if not user:
        raise NotFoundError("user", target_user_id)

    return UserResponseDTO.from_dco(user)


async def update_my_profile(current_user: dict, body: UpdateMyProfileRequestDTO) -> UserResponseDTO:
    updates = body.model_dump(exclude_none=True)
    if "phone" in updates:
        _assert_phone_available(updates["phone"], exclude_user_id=current_user["user_id"])
    if not updates:
        user = find_user_by_id(current_user["user_id"])
        if not user:
            raise NotFoundError("user", current_user["user_id"])
        return UserResponseDTO.from_dco(user)

    updated_user = update_user(current_user["user_id"], updates)
    if not updated_user:
        raise NotFoundError("user", current_user["user_id"])

    logger.info("User profile updated | user_id={}", current_user["user_id"])
    return UserResponseDTO.from_dco(updated_user)


async def update_user_by_admin(
    target_user_id: str,
    body: AdminUpdateUserRequestDTO,
    admin_user: dict,
) -> UserResponseDTO:
    if admin_user.get("role") != "ADMIN":
        raise AuthorizationError("Only admins can update users", required_role="ADMIN")

    existing = find_user_by_id(target_user_id)
    if not existing:
        raise NotFoundError("user", target_user_id)

    updates = body.model_dump(exclude_none=True)

    if "role" in updates:
        updates["role"] = updates["role"].value

    if "password" in updates:
        updates["password_hash"] = hash_password(updates.pop("password"))
        updates["current_refresh_jti"] = None

    if "phone" in updates:
        _assert_phone_available(updates["phone"], exclude_user_id=target_user_id)

    if "is_active" in updates and updates["is_active"] is False:
        updates["current_refresh_jti"] = None

    updated_user = update_user(target_user_id, updates)
    if not updated_user:
        raise NotFoundError("user", target_user_id)

    logger.info(
        "User updated by admin | admin_id={} user_id={}",
        admin_user["user_id"],
        target_user_id,
    )
    return UserResponseDTO.from_dco(updated_user)


async def delete_user_by_admin(target_user_id: str, admin_user: dict) -> None:
    if admin_user.get("role") != "ADMIN":
        raise AuthorizationError("Only admins can delete users", required_role="ADMIN")

    if not soft_delete_user(target_user_id):
        raise NotFoundError("user", target_user_id)

    logger.info(
        "User soft-deleted by admin | admin_id={} user_id={}",
        admin_user["user_id"],
        target_user_id,
    )
