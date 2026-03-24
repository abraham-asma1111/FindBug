"""
Formatting helpers for FindBug Platform
"""
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Optional


# ─── Date / Time ─────────────────────────────────────────────────────────────
def format_datetime(dt: Optional[datetime], fmt: str = "%Y-%m-%d %H:%M:%S UTC") -> Optional[str]:
    """Format datetime to human-readable string."""
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.strftime(fmt)


def format_date(dt: Optional[datetime]) -> Optional[str]:
    """Format datetime to date-only string."""
    return dt.strftime("%Y-%m-%d") if dt else None


def utcnow() -> datetime:
    """Return current UTC datetime (timezone-aware)."""
    return datetime.now(timezone.utc)


def datetime_to_iso(dt: Optional[datetime]) -> Optional[str]:
    """Convert datetime to ISO 8601 string."""
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.isoformat()


# ─── Currency ─────────────────────────────────────────────────────────────────
def format_currency_etb(amount: float) -> str:
    """Format amount as Ethiopian Birr."""
    return f"ETB {amount:,.2f}"


def format_currency_usd(amount: float) -> str:
    """Format amount as US Dollars."""
    return f"${amount:,.2f}"


def round_currency(amount: float, decimals: int = 2) -> float:
    """Round to financial precision."""
    return float(round(Decimal(str(amount)), decimals))


# ─── Pagination ───────────────────────────────────────────────────────────────
def build_pagination_response(
    items: list,
    total: int,
    page: int,
    page_size: int,
) -> dict:
    """Build a standard paginated API response envelope."""
    total_pages = max(1, (total + page_size - 1) // page_size)
    return {
        "items": items,
        "pagination": {
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_previous": page > 1,
        },
    }


# ─── String ───────────────────────────────────────────────────────────────────
def truncate(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate a string to max_length, appending suffix if truncated."""
    if len(text) <= max_length:
        return text
    return text[: max_length - len(suffix)] + suffix


def slugify(text: str) -> str:
    """Convert a string to a URL-friendly slug."""
    import re
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    text = re.sub(r"^-+|-+$", "", text)
    return text


def mask_email(email: str) -> str:
    """Mask an email address for display: ab***@example.com"""
    parts = email.split("@")
    if len(parts) != 2:
        return email
    username, domain = parts
    if len(username) <= 2:
        return f"{'*' * len(username)}@{domain}"
    return f"{username[:2]}{'*' * (len(username) - 2)}@{domain}"


# ─── Error formatting ─────────────────────────────────────────────────────────
def flatten_errors(errors: Any) -> list[str]:
    """Flatten pydantic-style validation errors to a list of strings."""
    result = []
    if isinstance(errors, list):
        for err in errors:
            if isinstance(err, dict):
                loc = " → ".join(str(l) for l in err.get("loc", []))
                msg = err.get("msg", "Unknown error")
                result.append(f"{loc}: {msg}" if loc else msg)
            else:
                result.append(str(err))
    elif isinstance(errors, dict):
        for field, msgs in errors.items():
            if isinstance(msgs, list):
                for msg in msgs:
                    result.append(f"{field}: {msg}")
            else:
                result.append(f"{field}: {msgs}")
    else:
        result.append(str(errors))
    return result
