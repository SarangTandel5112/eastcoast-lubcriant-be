"""Supabase Python client singleton for auth, storage, and other SDK features."""

from loguru import logger
from supabase import create_client, Client

from app.core.config import settings

_supabase_client: Client | None = None


def get_supabase_client() -> Client:
    """Return the shared Supabase client instance (lazy-initialised).

    Raises:
        RuntimeError: If SUPABASE_URL or SUPABASE_KEY are not configured.
    """
    global _supabase_client

    if _supabase_client is not None:
        return _supabase_client

    if not settings.supabase_url or not settings.supabase_key:
        raise RuntimeError(
            "Supabase client not configured. "
            "Set SUPABASE_URL and SUPABASE_KEY in your .env file."
        )

    _supabase_client = create_client(settings.supabase_url, settings.supabase_key)
    logger.info("Supabase client initialised | url={}", settings.supabase_url)
    return _supabase_client
