from decimal import Decimal

from src.api.v1.schemas.coercion import coerce_optional_float


def test_coerce_optional_float_from_decimal():
    assert coerce_optional_float(Decimal("7.5")) == 7.5


def test_coerce_optional_float_from_string():
    assert coerce_optional_float("8.2") == 8.2


def test_coerce_optional_float_invalid_string():
    assert coerce_optional_float("not-a-number") is None


def test_coerce_optional_float_empty():
    assert coerce_optional_float(None) is None
    assert coerce_optional_float("") is None
