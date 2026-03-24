"""
Input validators for FindBug Platform
"""
import re
import uuid
from typing import Optional
from .constants import MIN_PASSWORD_LENGTH


# ─── Email ────────────────────────────────────────────────────────────────────
EMAIL_REGEX = re.compile(
    r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$"
)

FREE_EMAIL_DOMAINS = {
    "gmail.com", "yahoo.com", "hotmail.com", "outlook.com",
    "aol.com", "icloud.com", "mail.com", "protonmail.com",
}


def validate_email(email: str) -> bool:
    """Validate email format."""
    return bool(EMAIL_REGEX.match(email.strip().lower()))


def is_business_email(email: str) -> bool:
    """Return True if email is NOT from a free provider (i.e. business email)."""
    domain = email.strip().lower().split("@")[-1]
    return domain not in FREE_EMAIL_DOMAINS


# ─── Password ────────────────────────────────────────────────────────────────
def validate_password_strength(password: str) -> tuple[bool, list[str]]:
    """
    Validate password strength.
    Returns (is_valid, list_of_errors).
    """
    errors = []
    if len(password) < MIN_PASSWORD_LENGTH:
        errors.append(f"Password must be at least {MIN_PASSWORD_LENGTH} characters long.")
    if not re.search(r"[A-Z]", password):
        errors.append("Password must contain at least one uppercase letter.")
    if not re.search(r"[a-z]", password):
        errors.append("Password must contain at least one lowercase letter.")
    if not re.search(r"\d", password):
        errors.append("Password must contain at least one digit.")
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        errors.append("Password must contain at least one special character.")
    return len(errors) == 0, errors


# ─── URL ──────────────────────────────────────────────────────────────────────
URL_REGEX = re.compile(
    r"^(https?://)"
    r"(([a-zA-Z0-9\-]+\.)+[a-zA-Z]{2,})"
    r"(:\d+)?"
    r"(/[^\s]*)?$"
)


def validate_url(url: str) -> bool:
    """Validate a URL format."""
    return bool(URL_REGEX.match(url.strip()))


# ─── Phone ────────────────────────────────────────────────────────────────────
PHONE_REGEX = re.compile(r"^\+?[1-9]\d{6,14}$")


def validate_phone(phone: str) -> bool:
    """Validate international phone number."""
    cleaned = re.sub(r"[\s\-\(\)]", "", phone)
    return bool(PHONE_REGEX.match(cleaned))


# ─── UUID ─────────────────────────────────────────────────────────────────────
def validate_uuid(value: str) -> bool:
    """Check if string is a valid UUID."""
    try:
        uuid.UUID(str(value))
        return True
    except ValueError:
        return False


# ─── CVSS Score ───────────────────────────────────────────────────────────────
def validate_cvss_score(score: float) -> bool:
    """CVSS score must be between 0.0 and 10.0."""
    return 0.0 <= score <= 10.0


# ─── File ─────────────────────────────────────────────────────────────────────
def validate_file_size(size_bytes: int, max_bytes: int) -> bool:
    """Check if file size is within limit."""
    return size_bytes <= max_bytes


def validate_mime_type(mime_type: str, allowed: set) -> bool:
    """Check if mime type is in the allowed set."""
    return mime_type.lower() in allowed


# ─── Pagination ───────────────────────────────────────────────────────────────
def validate_pagination(page: int, page_size: int, max_size: int = 100) -> tuple[bool, str]:
    """Validate pagination parameters."""
    if page < 1:
        return False, "Page number must be >= 1"
    if page_size < 1:
        return False, "Page size must be >= 1"
    if page_size > max_size:
        return False, f"Page size must be <= {max_size}"
    return True, ""


# ─── Name / Text ──────────────────────────────────────────────────────────────
def validate_non_empty_string(value: str, field_name: str = "Field") -> tuple[bool, str]:
    """Ensure a string is non-empty after stripping."""
    if not value or not value.strip():
        return False, f"{field_name} cannot be empty."
    return True, ""


def validate_string_length(
    value: str,
    min_len: int = 0,
    max_len: int = 255,
    field_name: str = "Field"
) -> tuple[bool, str]:
    """Validate string falls within allowed length range."""
    length = len(value.strip())
    if length < min_len:
        return False, f"{field_name} must be at least {min_len} characters."
    if length > max_len:
        return False, f"{field_name} must be at most {max_len} characters."
    return True, ""


# ─── Amount ───────────────────────────────────────────────────────────────────
def validate_positive_amount(amount: float, field_name: str = "Amount") -> tuple[bool, str]:
    """Validate that a monetary amount is positive."""
    if amount <= 0:
        return False, f"{field_name} must be a positive number."
    return True, ""
