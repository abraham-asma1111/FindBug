"""Coerce DB/API numeric types for JSON-friendly response schemas."""
from decimal import Decimal, InvalidOperation
from typing import Any, Optional


def coerce_optional_float(value: Any) -> Optional[float]:
    """Normalize Decimal, int, float, or numeric strings to float for JSON APIs."""
    if value is None or value == "":
        return None
    try:
        if isinstance(value, bool):
            return None
        if isinstance(value, Decimal):
            parsed = float(value)
        elif isinstance(value, (int, float)):
            parsed = float(value)
        else:
            parsed = float(value)
    except (TypeError, ValueError, InvalidOperation):
        return None
    if parsed != parsed:  # NaN
        return None
    return parsed
