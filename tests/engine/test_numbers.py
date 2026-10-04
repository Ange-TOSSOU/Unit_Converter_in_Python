"""Tests for reading numbers typed by a user."""

import pytest

from unitconverter.engine.errors import ConverterError, InvalidNumberError
from unitconverter.engine.numbers import parse_number

# --- Valid input ----------------------------------------------------------


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("5", 5.0),
        (" 5 ", 5.0),
        ("\t5\n", 5.0),
        ("-2.5", -2.5),
        ("+3", 3.0),
        ("0", 0.0),
        ("1e3", 1000.0),
        ("1E-3", 0.001),
        (".5", 0.5),
        ("5.", 5.0),
        ("007", 7.0),
        (5, 5.0),
        (-5, -5.0),
        (0, 0.0),
        (2.5, 2.5),
    ],
)
def test_valid_input_is_read(value: str | float, expected: float) -> None:
    assert parse_number(value) == expected


@pytest.mark.parametrize("value", ["5", 5, 5.0])
def test_result_is_always_a_float(value: str | float) -> None:
    assert isinstance(parse_number(value), float)


# --- Invalid input --------------------------------------------------------


@pytest.mark.parametrize(
    "value",
    [
        "",
        "   ",
        "abc",
        "5 km",
        "5km",
        "1,5",  # decimal comma
        "1 000",  # space as thousands separator
        "1,000",  # comma as thousands separator
        "1_000",  # Python accepts this, we do not
        "0x10",
        "--3",
        "nan",
        "NaN",
        "inf",
        "-inf",
        "Infinity",
        "1e999",  # too large for a float
        "\u0661\u0662\u0663",  # Arabic-Indic digits
        "\uff11\uff12",  # full-width digits
        float("nan"),
        float("inf"),
        float("-inf"),
        10**400,  # an int too large for a float
    ],
)
def test_invalid_numbers_are_rejected(value: object) -> None:
    with pytest.raises(InvalidNumberError):
        parse_number(value)


@pytest.mark.parametrize("value", [None, True, False, [], (), {}, b"5", object()])
def test_other_types_are_rejected(value: object) -> None:
    with pytest.raises(InvalidNumberError):
        parse_number(value)


# --- The error ------------------------------------------------------------


@pytest.mark.parametrize("value", ["abc", "", "1,5", None, True])
def test_the_error_keeps_the_original_input(value: object) -> None:
    with pytest.raises(InvalidNumberError) as info:
        parse_number(value)
    assert info.value.value is value


def test_the_error_message_shows_the_input() -> None:
    with pytest.raises(InvalidNumberError) as info:
        parse_number("1,5")
    assert info.value.message == "InvalidNumberError: '1,5' is not a valid number."


def test_the_error_is_a_converter_error() -> None:
    with pytest.raises(ConverterError):
        parse_number("abc")
