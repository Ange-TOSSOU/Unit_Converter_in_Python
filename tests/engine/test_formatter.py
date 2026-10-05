"""Tests for the output formatter."""

import math

import pytest

from unitconverter.engine.formatter import format_number, format_quantity
from unitconverter.engine.models import Quantity, Unit

# --- Zero and ordinary values ---


@pytest.mark.parametrize("x", [0, 0.0, -0.0])
def test_zero_is_shown_as_zero(x: float) -> None:
    assert format_number(x) == "0"


@pytest.mark.parametrize(
    ("x", "expected"),
    [
        (5, "5"),
        (5.0, "5"),
        (5.5, "5.5"),
        (100, "100"),
        (100000, "100000"),
        (999999, "999999"),
        (0.5, "0.5"),
        (0.1, "0.1"),
        (1234.5678, "1234.5678"),
        (123456.789, "123456.789"),
        (12.345678, "12.3457"),
        (6.21371192, "6.2137"),
        (999999.5, "999999.5"),
    ],
)
def test_ordinary_values_use_up_to_four_decimals(x: float, expected: str) -> None:
    assert format_number(x) == expected


def test_trailing_zeros_are_removed() -> None:
    assert format_number(2.5000) == "2.5"
    assert format_number(1.00001) == "1"


@pytest.mark.parametrize(
    ("x", "expected"),
    [
        (-5, "-5"),
        (-0.5, "-0.5"),
        (-1234.5678, "-1234.5678"),
        (-0.00001234, "-1.234e-5"),
        (-1e6, "-1e6"),
    ],
)
def test_negative_values_keep_their_sign(x: float, expected: str) -> None:
    assert format_number(x) == expected


# --- Small values: at least 4 significant digits ---


@pytest.mark.parametrize(
    ("x", "expected"),
    [
        (0.123456, "0.1235"),
        (0.012345678, "0.01235"),
        (0.0012345678, "0.001235"),
        (0.000123456, "0.0001235"),
        (0.00015, "0.00015"),
        (0.0001, "0.0001"),
    ],
)
def test_small_values_keep_four_significant_digits(x: float, expected: str) -> None:
    assert format_number(x) == expected


# --- Scientific notation ---


@pytest.mark.parametrize(
    ("x", "expected"),
    [
        (1e6, "1e6"),
        (2e7, "2e7"),
        (1234567890, "1.235e9"),
        (1.5e12, "1.5e12"),
        (0.00009999, "9.999e-5"),
        (0.00001234, "1.234e-5"),
        (1e-10, "1e-10"),
    ],
)
def test_extreme_values_use_scientific_notation(x: float, expected: str) -> None:
    assert format_number(x) == expected


def test_scientific_notation_has_no_plus_sign_or_padding() -> None:
    for x in (1e6, 2.5e9, 1.2e-5, 3e-10, 4e100):
        text = format_number(x)
        assert "e+" not in text
        assert "e0" not in text
        assert "e-0" not in text


# --- Thresholds ---


def test_the_upper_threshold_is_one_million() -> None:
    assert format_number(999999) == "999999"
    assert format_number(1000000) == "1e6"


def test_the_lower_threshold_is_one_ten_thousandth() -> None:
    assert format_number(0.0001) == "0.0001"
    assert format_number(0.00009999) == "9.999e-5"


def test_rounding_across_the_upper_threshold_switches_notation() -> None:
    # Fixed notation would show 1000000.0000, which is not allowed.
    assert format_number(999999.99996) == "1e6"


def test_rounding_up_to_the_next_power_of_ten_is_clean() -> None:
    assert format_number(0.99996) == "1"
    assert format_number(0.00099999) == "0.001"


def test_just_below_the_lower_threshold_can_round_up_to_it() -> None:
    assert format_number(0.000099999) == "1e-4"


# --- Properties ---


@pytest.mark.parametrize(
    "x",
    [5, 5.5, 0.5, 1234.5678, 12.345678, 0.000123456, 1e6, 1e-10, -3.25, 123456.789],
)
def test_output_never_ends_with_a_decimal_point_or_zero_decimals(x: float) -> None:
    text = format_number(x)
    mantissa = text.split("e")[0]
    if "." in mantissa:
        assert not mantissa.endswith("0")
        assert not mantissa.endswith(".")


@pytest.mark.parametrize("x", [0.1, 12.5, 999.999, 0.00123, 123456.7])
def test_fixed_output_reads_back_close_to_the_input(x: float) -> None:
    assert float(format_number(x)) == pytest.approx(x, rel=1e-3)


@pytest.mark.parametrize("x", [1e6, 1.234e8, 5.5e-5, 9e-9, -2e12])
def test_scientific_output_reads_back_close_to_the_input(x: float) -> None:
    assert float(format_number(x)) == pytest.approx(x, rel=1e-3)


# --- Non-finite values ---


def test_infinities_are_shown_as_such() -> None:
    assert format_number(math.inf) == "inf"
    assert format_number(-math.inf) == "-inf"


def test_nan_is_shown_as_nan() -> None:
    assert format_number(math.nan) == "nan"


# --- format_quantity ---


def make_unit(symbol: str) -> Unit:
    return Unit(id="u", name="u", symbol=symbol, factor=1)


@pytest.mark.parametrize(
    ("value", "symbol", "expected"),
    [
        (6.21371192, "mi", "6.2137 mi"),
        (0, "C", "0 C"),
        (2e7, "m", "2e7 m"),
        (-40, "F", "-40 F"),
        (0.000123456, "kg", "0.0001235 kg"),
    ],
)
def test_quantity_is_shown_as_number_and_symbol(
    value: float, symbol: str, expected: str
) -> None:
    assert format_quantity(Quantity(value, make_unit(symbol))) == expected
