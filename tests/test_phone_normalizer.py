import pytest

from app.services.phone_normalizer import PhoneNormalizer


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("052-123-4567", "0521234567"),
        ("+972521234567", "0521234567"),
        ("972521234567", "0521234567"),
        ("(052) 123 4567", "0521234567"),
    ],
)
def test_phone_normalization(value: str, expected: str):
    assert PhoneNormalizer().normalize_israeli_phone(value) == expected
