"""Generic response wrapper — every route calls respond() or error_respond()."""

from datetime import datetime, timezone
from typing import Any

from fastapi.responses import JSONResponse


def to_camel(string: Any) -> Any:
    """
    Convert snake_case to camelCase.
    Also handles non-string keys by returning them as-is.
    """
    if not isinstance(string, str):
        return string
        
    components = string.split("_")
    if len(components) == 1:
        return components[0]
    return components[0] + "".join(x.title() for x in components[1:])


def _serialize(obj: Any) -> Any:
    """
    Convert Pydantic models, dataclass DCOs, and collections to dicts/lists.
    Ensures all dictionary keys are camelCased recursively.
    """
    from uuid import UUID
    from decimal import Decimal

    if obj is None:
        return None
    
    # 1. Handle Pydantic models (V2)
    if hasattr(obj, "model_dump"):
        return _serialize(obj.model_dump(by_alias=True))
    
    # 2. Handle Dataclasses
    if hasattr(obj, "__dataclass_fields__"):
        from dataclasses import asdict
        return _serialize(asdict(obj))
    
    # 3. Handle common primitive-like types
    if isinstance(obj, UUID):
        return str(obj)
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, Decimal):
        return str(obj)
    
    # 4. Handle collections recursively
    if isinstance(obj, (list, tuple, set)):
        return [_serialize(item) for item in obj]
        
    if isinstance(obj, dict):
        return {to_camel(k): _serialize(v) for k, v in obj.items()}
        
    return obj


def respond(
    data: Any = None,
    message: str = "Success",
    status_code: int = 200,
    meta: dict | None = None,
    request_id: str | None = None,
) -> JSONResponse:
    """Wrap any success payload in a consistent JSON envelope."""
    body = {
        "success": True,
        "statusCode": status_code,
        "message": message,
        "data": _serialize(data),
        "meta": _serialize(meta),
        "requestId": request_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    return JSONResponse(content=body, status_code=status_code)


def error_respond(
    message: str = "Something went wrong",
    status_code: int = 500,
    error_code: str = "INTERNAL_ERROR",
    errors: list[dict] | None = None,
    details: dict | None = None,
    request_id: str | None = None,
    headers: dict | None = None,
) -> JSONResponse:
    """Wrap any error in a consistent JSON envelope."""
    body = {
        "success": False,
        "statusCode": status_code,
        "message": message,
        "errorCode": error_code,
        "errors": _serialize(errors),
        "details": _serialize(details),
        "requestId": request_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    return JSONResponse(content=body, status_code=status_code, headers=headers)
