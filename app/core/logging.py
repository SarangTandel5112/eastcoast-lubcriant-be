import sys
from loguru import logger
from app.core.config import settings


def setup_logging():
    logger.remove()  # remove default handler

    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )

    # Console handler
    logger.add(
        sys.stdout,
        format=log_format,
        level="DEBUG" if settings.debug else "INFO",
        colorize=True,
    )

    # File handler — rotates at 10MB, keeps 10 days
    logger.add(
        "logs/app.log",
        format=log_format,
        level="INFO",
        rotation="10 MB",
        retention="10 days",
        compression="zip",
    )

    # Separate error log
    logger.add(
        "logs/error.log",
        format=log_format,
        level="ERROR",
        rotation="10 MB",
        retention="30 days",
    )

    # JSON structured log — for Datadog / CloudWatch
    logger.add(
        "logs/structured.json",
        level="INFO",
        rotation="10 MB",
        retention="10 days",
        serialize=True,  # outputs JSON
    )
