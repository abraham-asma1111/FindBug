import pytest
from src.utils.validators import (
    validate_email,
    is_business_email,
    validate_password_strength,
    validate_url,
    validate_phone
)
from src.utils.formatters import (
    format_currency_etb,
    format_currency_usd,
    slugify,
    mask_email
)
from src.utils.helpers import generate_uuid


def test_validate_email():
    assert validate_email("test@example.com") is True
    assert validate_email("john.doe+alias@domain.co") is True
    assert validate_email("invalid-email") is False
    assert validate_email("test@") is False


def test_is_business_email():
    assert is_business_email("admin@findbug.com") is True
    assert is_business_email("test@gmail.com") is False
    assert is_business_email("user@yahoo.com") is False


def test_validate_password_strength():
    # Valid password
    valid, errors = validate_password_strength("Str0ngP@ssw0rd!")
    assert valid is True
    assert len(errors) == 0

    # Invalid: no special char
    valid, errors = validate_password_strength("Password1234")
    assert valid is False
    assert len(errors) == 1

    # Invalid: too short, no upper, no digit, no special
    valid, errors = validate_password_strength("weak")
    assert valid is False
    assert len(errors) == 4


def test_validate_url():
    assert validate_url("https://example.com") is True
    assert validate_url("http://sub.domain.co.uk/path") is True
    assert validate_url("invalid-url") is False
    assert validate_url("ftp://example.com") is False


def test_validate_phone():
    assert validate_phone("+1234567890") is True
    assert validate_phone("251911223344") is True
    assert validate_phone("invalid") is False


def test_format_currency():
    assert format_currency_etb(1500.5) == "ETB 1,500.50"
    assert format_currency_usd(1500.5) == "$1,500.50"


def test_slugify():
    assert slugify("Hello World!") == "hello-world"
    assert slugify("SQL Injection (SQLi)") == "sql-injection-sqli"


def test_mask_email():
    assert mask_email("johndoe@example.com") == "jo*****@example.com"
    assert mask_email("ab@example.com") == "**@example.com"


def test_generate_uuid():
    # Check it generates a valid format string
    uuid_str = generate_uuid()
    assert isinstance(uuid_str, str)
    assert len(uuid_str) == 36
