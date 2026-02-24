"""Token blacklist for JWT revocation."""

from typing import Optional
from loguru import logger

from app.core.config import settings


# In-memory blacklist for development (will be replaced with Redis)
_token_blacklist: set[str] = set()


def blacklist_token(token: str, expires_in_seconds: int) -> None:
    """
    Add a token to the blacklist.

    Args:
        token: The JWT token to blacklist
        expires_in_seconds: How long until the token would naturally expire

    Note:
        In production with Redis, the token would be stored with TTL
        to automatically expire when the token would naturally expire.
    """
    if not token:
        return

    try:
        if settings.redis_url:
            # Use Redis for distributed token blacklist
            import redis
            redis_client = redis.from_url(settings.redis_url)
            redis_client.setex(
                f"blacklist:token:{token}",
                expires_in_seconds,
                "1"
            )
            logger.debug("Token blacklisted in Redis | expires_in={}s", expires_in_seconds)
        else:
            # Fall back to in-memory storage (single-instance only)
            _token_blacklist.add(token)
            logger.warning(
                "Token blacklisted in memory. "
                "Configure Redis for production to support multiple instances."
            )

    except Exception as e:
        logger.error("Failed to blacklist token | error={}", str(e))
        # Fall back to in-memory storage
        _token_blacklist.add(token)


def is_token_blacklisted(token: str) -> bool:
    """
    Check if a token has been blacklisted (revoked).

    Args:
        token: The JWT token to check

    Returns:
        True if the token is blacklisted, False otherwise
    """
    if not token:
        return False

    try:
        if settings.redis_url:
            # Check Redis for distributed blacklist
            import redis
            redis_client = redis.from_url(settings.redis_url)
            exists = redis_client.exists(f"blacklist:token:{token}")
            return exists == 1
        else:
            # Check in-memory storage
            return token in _token_blacklist

    except Exception as e:
        logger.error("Failed to check token blacklist | error={}", str(e))
        # Fall back to in-memory check
        return token in _token_blacklist


def blacklist_all_user_tokens(user_id: str) -> None:
    """
    Blacklist all tokens for a specific user.

    This is useful when:
    - User changes password
    - User reports account compromise
    - Admin needs to force logout a user

    Args:
        user_id: The user ID whose tokens should be revoked

    Note:
        This requires storing a mapping of user_id -> tokens in Redis.
        For now, we'll track this in the JWT claims with 'iat' (issued at).
    """
    if not user_id:
        return

    try:
        if settings.redis_url:
            import redis
            from datetime import datetime, timezone

            redis_client = redis.from_url(settings.redis_url)

            # Store the timestamp when all tokens were revoked
            # Tokens issued before this time are invalid
            revocation_time = datetime.now(timezone.utc).timestamp()
            redis_client.setex(
                f"blacklist:user:{user_id}",
                60 * 60 * 24 * 7,  # Store for 7 days (max refresh token lifetime)
                str(revocation_time)
            )

            logger.info("All tokens revoked for user | user_id={}", user_id)
        else:
            logger.warning(
                "Cannot revoke all user tokens without Redis. "
                "Configure REDIS_URL to enable this feature."
            )

    except Exception as e:
        logger.error("Failed to revoke all user tokens | user_id={} error={}", user_id, str(e))


def are_user_tokens_revoked(user_id: str, token_issued_at: Optional[float]) -> bool:
    """
    Check if all tokens for a user have been revoked.

    Args:
        user_id: The user ID to check
        token_issued_at: Unix timestamp when the token was issued (from 'iat' claim)

    Returns:
        True if the token was issued before the revocation time, False otherwise
    """
    if not user_id or token_issued_at is None:
        return False

    try:
        if settings.redis_url:
            import redis
            redis_client = redis.from_url(settings.redis_url)

            revocation_time_str = redis_client.get(f"blacklist:user:{user_id}")

            if revocation_time_str:
                revocation_time = float(revocation_time_str)
                # Token is revoked if it was issued before the revocation time
                return token_issued_at < revocation_time

        return False

    except Exception as e:
        logger.error(
            "Failed to check user token revocation | user_id={} error={}",
            user_id,
            str(e)
        )
        return False


def clear_blacklist() -> None:
    """
    Clear the entire token blacklist.

    WARNING: This should only be used in testing/development.
    In production, let tokens expire naturally.
    """
    global _token_blacklist

    try:
        if settings.redis_url:
            import redis
            redis_client = redis.from_url(settings.redis_url)

            # Delete all blacklist keys
            cursor = 0
            while True:
                cursor, keys = redis_client.scan(cursor, match="blacklist:*", count=100)
                if keys:
                    redis_client.delete(*keys)
                if cursor == 0:
                    break

            logger.warning("Token blacklist cleared from Redis")
        else:
            _token_blacklist.clear()
            logger.warning("In-memory token blacklist cleared")

    except Exception as e:
        logger.error("Failed to clear token blacklist | error={}", str(e))
