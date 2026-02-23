from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # App
    app_name: str = "EcommerceAPI"
    debug: bool = False
    api_v1_prefix: str = "/api/v1"

    # Security
    secret_key: str = "change-me-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # Redis
    redis_url: str = ""  # leave empty to disable Redis (caching + Celery)

    # CORS
    allowed_origins: List[str] = ["http://localhost:3000"]

    # External services
    stripe_secret_key: str = ""
    sendgrid_api_key: str = ""
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_s3_bucket: str = ""
    aws_region: str = "us-east-1"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
