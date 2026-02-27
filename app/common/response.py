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
    from datetime import datetime

    if obj is None:
        return None
    
    # 1. Handle Pydantic models (V2)
    if hasattr(obj, "model_dump"):
        # We model_dump first, then recursively serialize the resulting dict 
        # to ensure any nested objects (not covered by model_dump) are handled
        return _serialize(obj.model_dump(by_alias=True))
    
    # 2. Handle Dataclasses
    if hasattr(obj, "__dataclass_fields__"):
        from dataclasses import asdict
        return _serialize(asdict(obj))
    
    # 3. Handle common primitive-like types
    if isinstance(obj, UUID):
        return str(obj)
    if isinstance(obj, (datetime, datetime)):
        return obj.isoformat()
    if isinstance(obj, Decimal):
        return str(obj)
    
    # 4. Handle collections recursively
    if isinstance(obj, (list, tuple, set)):
        return [_serialize(item) for item in obj]
        
    if isinstance(obj, dict):
        # Recursively serialize values AND convert keys to camelCase
        return {to_camel(k): _serialize(v) for k, v in obj.items()}
        
    return obj


def respond(
    data: Any = None,
    message: str = "Success",
    status_code: int = 200,
    meta: dict | None = None,
) -> JSONResponse:
    """Wrap any success payload in a consistent JSON envelope."""
    body = {
        "success": True,
        "statusCode": status_code,
        "message": message,
        "data": _serialize(data),
        "meta": _serialize(meta),
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
        "statusCode": status_code,
        "message": message,
        "errorCode": error_code,
        "errors": _serialize(errors),
        "details": _serialize(details),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    return JSONResponse(content=body, status_code=status_code)


def _serialize(obj: Any) -> Any:
    """Convert Pydantic models, dataclass DCOs, and lists thereof to dicts."""
    from uuid import UUID
    from decimal import Decimal
    from datetime import datetime

    if obj is None:
        return None
    
    # Handle Pydantic models
    if hasattr(obj, "model_dump"):
        return obj.model_dump(by_alias=True)
    
    # Handle Dataclasses
    if hasattr(obj, "__dataclass_fields__"):
        from dataclasses import asdict
        # asdict is not enough if it contains Pydantic models or other types
        return _serialize(asdict(obj))
    
    # Handle common types
    if isinstance(obj, UUID):
        return str(obj)
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, Decimal):
        return str(obj)
    
    # Handle collections recursively
    if isinstance(obj, list):
        return [_serialize(item) for item in obj]
    if isinstance(obj, dict):
        return {k: _serialize(v) for k, v in obj.items()}
        
    return obj
