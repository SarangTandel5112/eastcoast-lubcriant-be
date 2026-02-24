from uuid import uuid4

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

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


async def _issue_token_pair(session: AsyncSession, user: UserDCO) -> TokenResponseDTO:
    refresh_jti = str(uuid4())
    token_data = {"sub": user.id, "role": user.role}

    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data, refresh_jti)

    await set_current_refresh_jti(session, user.id, refresh_jti)

    return TokenResponseDTO(access_token=access_token, refresh_token=refresh_token)


async def _assert_phone_available(session: AsyncSession, phone: str | None, exclude_user_id: str | None = None) -> None:
    if not phone:
        return

    existing = await find_users_by_phone(session, phone, include_deleted=False)
    for user in existing:
        if exclude_user_id and user.id == exclude_user_id:
            continue
        raise ConflictError(message="Phone already registered", resource="user", field="phone")


async def register_user(session: AsyncSession, body: RegisterRequestDTO) -> UserResponseDTO:
    if await find_user_by_email(session, body.email, include_deleted=True):
        raise ConflictError(message="Email already registered", resource="user", field="email")
    await _assert_phone_available(session, body.phone)

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
    created = await create_user(session, dco)

    logger.info("User registered | user_id={} email={}", created.id, created.email)
    return UserResponseDTO.from_dco(created)


async def create_user_by_admin(session: AsyncSession, body: AdminCreateUserRequestDTO, admin_user: dict) -> UserResponseDTO:
    if admin_user.get("role") != "ADMIN":
        raise AuthorizationError("Only admins can create users", required_role="ADMIN")

    if await find_user_by_email(session, body.email, include_deleted=True):
        raise ConflictError(message="Email already registered", resource="user", field="email")
    await _assert_phone_available(session, body.phone)

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
    created = await create_user(session, dco)

    logger.info(
        "User created by admin | admin_id={} user_id={} role={}",
        admin_user["user_id"],
        created.id,
        created.role,
    )
    return UserResponseDTO.from_dco(created)


async def login_user(session: AsyncSession, body: LoginRequestDTO) -> TokenResponseDTO:
    lookup_email = body.email
    lookup_phone = body.phone

    if body.identifier:
        if "@" in body.identifier:
            lookup_email = body.identifier
        else:
            lookup_phone = body.identifier

    user = None
    if lookup_email:
        user = await find_user_by_email(session, lookup_email)
    elif lookup_phone:
        candidates = await find_users_by_phone(session, lookup_phone)
        if len(candidates) > 1:
            raise AuthenticationError("Multiple accounts use this phone. Please login with email")
        if candidates:
            user = candidates[0]

    if not user or not verify_password(body.password, user.password_hash):
        raise AuthenticationError("Invalid email or password")

    if not user.is_active:
        raise AuthenticationError("Account is inactive. Contact administrator")

    await set_last_login(session, user.id)
    user = await find_user_by_id(session, user.id)
    if not user:
        raise AuthenticationError("Unable to load user session")

    logger.info("User logged in | user_id={} role={}", user.id, user.role)
    return await _issue_token_pair(session, user)


async def refresh_user_token(session: AsyncSession, body: RefreshTokenRequestDTO) -> TokenResponseDTO:
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

    user = await find_user_by_id(session, user_id)
    if not user:
        raise AuthenticationError("Invalid refresh token")

    if not user.is_active:
        raise AuthenticationError("Account is inactive. Contact administrator")

    if user.current_refresh_jti != refresh_jti:
        raise AuthenticationError("Refresh token already rotated or revoked")

    logger.info("Token refreshed | user_id={}", user.id)
    return await _issue_token_pair(session, user)


async def logout_user(session: AsyncSession, user_id: str) -> None:
    await set_current_refresh_jti(session, user_id, None)
    logger.info("User logged out | user_id={}", user_id)


async def get_user_profile(session: AsyncSession, user_id: str) -> UserResponseDTO:
    user = await find_user_by_id(session, user_id)
    if not user:
        raise NotFoundError("user", user_id)

    return UserResponseDTO.from_dco(user)


async def list_users_for_admin(session: AsyncSession, current_user: dict, role: str | None, is_active: bool | None) -> list[UserResponseDTO]:
    if current_user.get("role") != "ADMIN":
        raise AuthorizationError("Only admins can list users", required_role="ADMIN")

    users = await list_users(session, role=role, is_active=is_active)
    return [UserResponseDTO.from_dco(user) for user in users]


async def get_user_by_id(session: AsyncSession, target_user_id: str, current_user: dict) -> UserResponseDTO:
    is_owner = current_user.get("user_id") == target_user_id
    is_admin = current_user.get("role") == "ADMIN"

    if not is_owner and not is_admin:
        raise AuthorizationError("You can only access your own user record", required_role="ADMIN")

    user = await find_user_by_id(session, target_user_id)
    if not user:
        raise NotFoundError("user", target_user_id)

    return UserResponseDTO.from_dco(user)


async def update_my_profile(session: AsyncSession, current_user: dict, body: UpdateMyProfileRequestDTO) -> UserResponseDTO:
    updates = body.model_dump(exclude_none=True)
    if "phone" in updates:
        await _assert_phone_available(session, updates["phone"], exclude_user_id=current_user["user_id"])
        
    if not updates:
        user = await find_user_by_id(session, current_user["user_id"])
        if not user:
            raise NotFoundError("user", current_user["user_id"])
        return UserResponseDTO.from_dco(user)

    updated_user = await update_user(session, current_user["user_id"], updates)
    if not updated_user:
        raise NotFoundError("user", current_user["user_id"])

    logger.info("User profile updated | user_id={}", current_user["user_id"])
    return UserResponseDTO.from_dco(updated_user)


async def update_user_by_admin(
    session: AsyncSession,
    target_user_id: str,
    body: AdminUpdateUserRequestDTO,
    admin_user: dict,
) -> UserResponseDTO:
    if admin_user.get("role") != "ADMIN":
        raise AuthorizationError("Only admins can update users", required_role="ADMIN")

    existing = await find_user_by_id(session, target_user_id)
    if not existing:
        raise NotFoundError("user", target_user_id)

    updates = body.model_dump(exclude_none=True)

    if "role" in updates:
        updates["role"] = updates["role"].value

    if "password" in updates:
        updates["password_hash"] = hash_password(updates.pop("password"))
        updates["current_refresh_jti"] = None

    if "phone" in updates:
        await _assert_phone_available(session, updates["phone"], exclude_user_id=target_user_id)

    if "is_active" in updates and updates["is_active"] is False:
        updates["current_refresh_jti"] = None

    updated_user = await update_user(session, target_user_id, updates)
    if not updated_user:
        raise NotFoundError("user", target_user_id)

    logger.info(
        "User updated by admin | admin_id={} user_id={}",
        admin_user["user_id"],
        target_user_id,
    )
    return UserResponseDTO.from_dco(updated_user)


async def delete_user_by_admin(session: AsyncSession, target_user_id: str, admin_user: dict) -> None:
    if admin_user.get("role") != "ADMIN":
        raise AuthorizationError("Only admins can delete users", required_role="ADMIN")

    if not await soft_delete_user(session, target_user_id):
        raise NotFoundError("user", target_user_id)

    logger.info(
        "User soft-deleted by admin | admin_id={} user_id={}",
        admin_user["user_id"],
        target_user_id,
    )
