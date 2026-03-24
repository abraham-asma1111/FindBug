"""
General-purpose helper utilities for FindBug Platform
"""
import uuid
import hashlib
import secrets
from typing import Any, Optional, TypeVar

T = TypeVar("T")


# ─── UUID ─────────────────────────────────────────────────────────────────────
def generate_uuid() -> str:
    """Generate a new UUID4 string."""
    return str(uuid.uuid4())


# ─── Tokens / Secrets ────────────────────────────────────────────────────────
def generate_secure_token(length: int = 32) -> str:
    """Generate a cryptographically secure random hex token."""
    return secrets.token_hex(length)


def generate_numeric_otp(digits: int = 6) -> str:
    """Generate a numeric OTP of given length."""
    return str(secrets.randbelow(10 ** digits)).zfill(digits)


def hash_string(value: str, salt: str = "") -> str:
    """SHA-256 hash of a string (not for passwords — use bcrypt for those)."""
    return hashlib.sha256((value + salt).encode()).hexdigest()


# ─── Dict / Object ───────────────────────────────────────────────────────────
def safe_get(obj: Any, *keys: str, default: Any = None) -> Any:
    """Safely traverse nested dict/object attributes without raising errors."""
    current = obj
    for key in keys:
        try:
            if isinstance(current, dict):
                current = current.get(key, default)
            else:
                current = getattr(current, key, default)
            if current is None:
                return default
        except Exception:
            return default
    return current


def exclude_none(d: dict) -> dict:
    """Remove None values from a dict."""
    return {k: v for k, v in d.items() if v is not None}


def exclude_keys(d: dict, keys: list[str]) -> dict:
    """Return dict without specified keys."""
    return {k: v for k, v in d.items() if k not in keys}


def merge_dicts(*dicts: dict) -> dict:
    """Merge multiple dicts left to right (later dicts win)."""
    result = {}
    for d in dicts:
        if d:
            result.update(d)
    return result


# ─── Pagination ───────────────────────────────────────────────────────────────
def paginate(items: list[T], page: int, page_size: int) -> list[T]:
    """Slice a list for in-memory pagination."""
    start = (page - 1) * page_size
    return items[start: start + page_size]


def get_offset(page: int, page_size: int) -> int:
    """Calculate SQL OFFSET from page number."""
    return (page - 1) * page_size


# ─── Type Coercion ────────────────────────────────────────────────────────────
def to_bool(value: Any) -> bool:
    """Convert various truthy representations to bool."""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in ("true", "1", "yes", "on", "y")
    return bool(value)


def to_int(value: Any, default: int = 0) -> int:
    """Safely convert value to int."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def to_float(value: Any, default: float = 0.0) -> float:
    """Safely convert value to float."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


# ─── List Utilities ───────────────────────────────────────────────────────────
def chunk_list(lst: list[T], size: int) -> list[list[T]]:
    """Split a list into chunks of given size."""
    return [lst[i: i + size] for i in range(0, len(lst), size)]


def deduplicate(lst: list) -> list:
    """Remove duplicates from a list while preserving order."""
    seen = set()
    result = []
    for item in lst:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


def first_or_none(lst: list[T]) -> Optional[T]:
    """Return the first element of a list, or None if empty."""
    return lst[0] if lst else None


# ─── String ───────────────────────────────────────────────────────────────────
def camel_to_snake(name: str) -> str:
    """Convert camelCase to snake_case."""
    import re
    s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def snake_to_camel(name: str) -> str:
    """Convert snake_case to camelCase."""
    parts = name.split("_")
    return parts[0] + "".join(word.capitalize() for word in parts[1:])
