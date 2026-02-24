from pydantic_settings import BaseSettings
from pydantic import Field, validator
from typing import List
import secrets


class Settings(BaseSettings):
    # App
    app_name: str = "EcommerceAPI"
    debug: bool = False
    api_v1_prefix: str = "/api/v1"
    environment: str = Field(default="development", description="Environment: development, staging, production")

    # Security - CRITICAL: Secret key must be set via environment variable
    secret_key: str = Field(
        ...,  # Required field, no default
        min_length=32,
        description="Secret key for JWT signing. Generate with: openssl rand -hex 32"
    )
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # Redis
    redis_url: str = ""  # leave empty to disable Redis (caching + Celery)

    # CORS - Restrict origins in production
    allowed_origins: List[str] = ["http://localhost:3000"]

    # External services
    stripe_secret_key: str = ""
    sendgrid_api_key: str = ""
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_s3_bucket: str = ""
    aws_region: str = "us-east-1"

    # Database (Supabase Postgres)
    database_url: str = ""       # postgresql+asyncpg://user:pass@host:port/db

    # Supabase client (for auth/storage SDK features)
    supabase_url: str = ""       # https://xxxxx.supabase.co
    supabase_key: str = ""       # anon or service_role key


    # Documentation access (for protecting Swagger/ReDoc)
    docs_username: str = Field(default="admin", description="Username for API docs access")
    docs_password: str = Field(default="", description="Password for API docs access")

    @validator("secret_key")
    def validate_secret_key(cls, v, values):
        """Validate secret key is secure."""
        if not v:
            raise ValueError("SECRET_KEY must be set in environment variables")

        if len(v) < 32:
            raise ValueError(
                "SECRET_KEY must be at least 32 characters long. "
                "Generate a secure key with: openssl rand -hex 32"
            )

        # Prevent common weak keys
        weak_keys = {
            "change-me-in-production",
            "secret",
            "password",
            "12345678901234567890123456789012",
            "00000000000000000000000000000000",
        }

        if v.lower() in weak_keys:
            raise ValueError(
                "SECRET_KEY is too weak or commonly used. "
                "Generate a secure random key with: openssl rand -hex 32"
            )

        return v

    @validator("allowed_origins")
    def validate_cors_origins(cls, v, values):
        """Warn about wildcard CORS in production."""
        environment = values.get("environment", "development")

        if environment == "production" and "*" in v:
            raise ValueError(
                "Wildcard CORS origins (*) are not allowed in production. "
                "Specify exact allowed origins."
            )

        return v

    @validator("docs_password")
    def validate_docs_password(cls, v, values):
        """Require docs password in production."""
        environment = values.get("environment", "development")

        if environment == "production" and not v:
            raise ValueError(
                "DOCS_PASSWORD must be set in production to protect API documentation"
            )

        return v

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
