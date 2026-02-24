"""In-memory user persistence layer (replace with real DB repository later)."""

from datetime import datetime, timezone
import re
from typing import Optional
from uuid import uuid4

from app.modules.auth.auth_dco import UserDCO


_users_by_id: dict[str, dict] = {}
_email_to_user_id: dict[str, str] = {}
_phone_to_user_ids: dict[str, set[str]] = {}


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _normalize_email(email: str) -> str:
    return email.strip().lower()


def _normalize_phone(phone: str) -> str:
    stripped = phone.strip()
    if stripped.startswith("+"):
        return "+" + re.sub(r"\D", "", stripped[1:])
    return re.sub(r"\D", "", stripped)


def create_user(dco: UserDCO) -> UserDCO:
    """Persist a new user and return the hydrated DCO with generated uuid."""
    now = _utc_now_iso()
    dco.id = str(uuid4())
    dco.email = _normalize_email(dco.email)
    dco.created_at = now
    dco.updated_at = now

    _users_by_id[dco.id] = dco.to_dict()
    _email_to_user_id[dco.email] = dco.id
    if dco.phone:
        normalized_phone = _normalize_phone(dco.phone)
        _phone_to_user_ids.setdefault(normalized_phone, set()).add(dco.id)
    return dco


def find_user_by_email(email: str, include_deleted: bool = False) -> Optional[UserDCO]:
    normalized_email = _normalize_email(email)
    user_id = _email_to_user_id.get(normalized_email)
    if not user_id:
        return None

    data = _users_by_id.get(user_id)
    if not data:
        return None

    if data.get("deleted_at") and not include_deleted:
        return None

    return UserDCO.from_dict(data)


def find_user_by_id(user_id: str, include_deleted: bool = False) -> Optional[UserDCO]:
    data = _users_by_id.get(user_id)
    if not data:
        return None

    if data.get("deleted_at") and not include_deleted:
        return None

    return UserDCO.from_dict(data)


def find_users_by_phone(phone: str, include_deleted: bool = False) -> list[UserDCO]:
    normalized_phone = _normalize_phone(phone)
    user_ids = _phone_to_user_ids.get(normalized_phone, set())
    users: list[UserDCO] = []

    for user_id in user_ids:
        data = _users_by_id.get(user_id)
        if not data:
            continue
        if data.get("deleted_at") and not include_deleted:
            continue
        users.append(UserDCO.from_dict(data))

    return users


def list_users(role: str | None = None, is_active: bool | None = None) -> list[UserDCO]:
    users: list[UserDCO] = []

    for data in _users_by_id.values():
        if data.get("deleted_at"):
            continue

        if role is not None and data.get("role") != role:
            continue

        if is_active is not None and data.get("is_active") is not is_active:
            continue

        users.append(UserDCO.from_dict(data))

    users.sort(key=lambda user: user.created_at, reverse=True)
    return users


def update_user(user_id: str, updates: dict) -> Optional[UserDCO]:
    existing = _users_by_id.get(user_id)
    if not existing or existing.get("deleted_at"):
        return None

    # Email updates are intentionally unsupported for simplicity and uniqueness safety.
    updates.pop("email", None)

    previous_phone = existing.get("phone")
    next_phone = updates.get("phone", previous_phone)

    updated = {**existing, **updates, "updated_at": _utc_now_iso()}
    _users_by_id[user_id] = updated

    # Maintain phone lookup index when phone changes.
    if previous_phone != next_phone:
        if previous_phone:
            normalized_old_phone = _normalize_phone(previous_phone)
            user_ids = _phone_to_user_ids.get(normalized_old_phone, set())
            user_ids.discard(user_id)
            if not user_ids and normalized_old_phone in _phone_to_user_ids:
                _phone_to_user_ids.pop(normalized_old_phone, None)
        if next_phone:
            normalized_new_phone = _normalize_phone(next_phone)
            _phone_to_user_ids.setdefault(normalized_new_phone, set()).add(user_id)

    return UserDCO.from_dict(updated)


def set_last_login(user_id: str) -> Optional[UserDCO]:
    return update_user(user_id, {"last_login_at": _utc_now_iso()})


def set_current_refresh_jti(user_id: str, refresh_jti: str | None) -> Optional[UserDCO]:
    return update_user(user_id, {"current_refresh_jti": refresh_jti})


def soft_delete_user(user_id: str) -> bool:
    existing = _users_by_id.get(user_id)
    if not existing or existing.get("deleted_at"):
        return False

    deleted_at = _utc_now_iso()
    existing["deleted_at"] = deleted_at
    existing["updated_at"] = deleted_at
    existing["is_active"] = False
    existing["current_refresh_jti"] = None
    _users_by_id[user_id] = existing
    return True
