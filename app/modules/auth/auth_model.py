from datetime import datetime, timezone
from typing import Optional

from app.modules.auth.auth_dco import UserDCO


# ── In-memory store (replace with real DB later) ─────────
_users_db: dict[str, dict] = {}
_user_counter: int = 0


def create_user(dco: UserDCO) -> UserDCO:
    """Persist a new user and return the hydrated DCO with generated id."""
    global _user_counter
    _user_counter += 1
    user_id = f"user_{_user_counter}"

    dco.id = user_id
    dco.created_at = datetime.now(timezone.utc).isoformat()

    _users_db[dco.email] = dco.to_dict()
    return dco


def find_user_by_email(email: str) -> Optional[UserDCO]:
    data = _users_db.get(email)
    if data is None:
        return None
    return UserDCO.from_dict(data)


def find_user_by_id(user_id: str) -> Optional[UserDCO]:
    for user_data in _users_db.values():
        if user_data["id"] == user_id:
            return UserDCO.from_dict(user_data)
    return None
