"""Generic response wrapper — every route calls respond() or error_respond()."""

from datetime import datetime, timezone
from typing import Any

from fastapi.responses import JSONResponse


def respond(
    data: Any = None,
    message: str = "Success",
    status_code: int = 200,
    meta: dict | None = None,
) -> JSONResponse:
    """Wrap any success payload in a consistent JSON envelope."""
    body = {
        "success": True,
        "status_code": status_code,
        "message": message,
        "data": _serialize(data),
        "meta": meta,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    return JSONResponse(content=body, status_code=status_code)


def error_respond(
    message: str = "Something went wrong",
    status_code: int = 500,
    error_code: str = "INTERNAL_ERROR",
    errors: list[dict] | None = None,
    details: dict | None = None,
) -> JSONResponse:
    """Wrap any error in a consistent JSON envelope."""
    body = {
        "success": False,
        "status_code": status_code,
        "message": message,
        "error_code": error_code,
        "errors": errors,
        "details": details,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    return JSONResponse(content=body, status_code=status_code)


def _serialize(obj: Any) -> Any:
    """Convert Pydantic models, dataclass DCOs, and lists thereof to dicts."""
    if obj is None:
        return None
    if hasattr(obj, "model_dump"):
        return obj.model_dump()
    if hasattr(obj, "__dataclass_fields__"):
        from dataclasses import asdict
        return asdict(obj)
    if isinstance(obj, list):
        return [_serialize(item) for item in obj]
    if isinstance(obj, dict):
        return obj
    return obj
