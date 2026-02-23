from datetime import datetime, timezone
from typing import Optional


# ── In-memory store (replace with real DB later) ─────────
_users_db: dict[str, dict] = {}
_user_counter: int = 0


def create_user(name: str, email: str, hashed_password: str, role: str = "customer") -> dict:
    global _user_counter
    _user_counter += 1
    user_id = f"user_{_user_counter}"

    user = {
        "id": user_id,
        "name": name,
        "email": email,
        "password": hashed_password,
        "role": role,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    _users_db[email] = user
    return user


def find_user_by_email(email: str) -> Optional[dict]:
    return _users_db.get(email)


def find_user_by_id(user_id: str) -> Optional[dict]:
    for user in _users_db.values():
        if user["id"] == user_id:
            return user
    return None
