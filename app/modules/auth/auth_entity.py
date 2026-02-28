"""Legacy auth entity — re-exports User from the canonical users module.

The canonical entity class for the `users` table is now:
    app.modules.users.users_entity.User

This file exists for backward compatibility with the auth module.
"""

from app.modules.users.users_entity import User as UserEntity, RoleEnum  # noqa: F401

__all__ = ["UserEntity", "RoleEnum"]
