"""Tests for parsing quantities and converting them between units."""

import math
from collections.abc import Callable

import pytest

from unitconverter.data import CATEGORIES, UNSUPPORTED
from unitconverter.engine.converter import convert, parse
from unitconverter.engine.errors import (
    ConverterError,
    IncompatibleUnitsError,
    InvalidNumberError,
    UnknownUnitError,
    UnsupportedUnitError,
)
from unitconverter.engine.models import Quantity, Unit
from unitconverter.engine.registry import Registry

REGISTRY = Registry(CATEGORIES, unsupported=UNSUPPORTED)


def unit(unit_id: str) -> Unit:
    found = REGISTRY.find_unit(unit_id.replace("_", " "))
    assert found is not None, f"unit '{unit_id}' not found"
    return found


def converted(value: float, from_id: str, to_id: str) -> float:
    return convert(Quantity(value, unit(from_id)), unit(to_id), REGISTRY).value


# --- Parse ---


def test_parse_builds_a_quantity() -> None:
    quantity = parse("10", "km", REGISTRY)
    assert quantity.value == 10.0
    assert quantity.unit is unit("kilometer")


@pytest.mark.parametrize("value", ["10", " 10 ", 10, 10.0])
def test_parse_accepts_text_and_numbers(value: str | float) -> None:
    assert parse(value, "meter", REGISTRY).value == 10.0


def test_parse_accepts_flexible_unit_names() -> None:
    assert parse("1", "  KILOMETRES ", REGISTRY).unit is unit("kilometer")


def test_parse_rejects_an_invalid_number() -> None:
    with pytest.raises(InvalidNumberError):
        parse("abc", "km", REGISTRY)


def test_parse_rejects_an_unknown_unit() -> None:
    with pytest.raises(UnknownUnitError):
        parse("1", "blorp", REGISTRY)


def test_parse_rejects_an_unsupported_unit() -> None:
    with pytest.raises(UnsupportedUnitError):
        parse("1", "gallon", REGISTRY)


def test_parse_reports_the_number_first_when_both_are_wrong() -> None:
    with pytest.raises(InvalidNumberError):
        parse("abc", "blorp", REGISTRY)


# --- Reference SI conversions to base unit ---


@pytest.mark.parametrize(
    ("value", "from_id", "to_id", "expected"),
    [
        # Length, in meters
        (1, "millimeter", "meter", 0.001),
        (1, "centimeter", "meter", 0.01),
        (1, "decimeter", "meter", 0.1),
        (1, "meter", "meter", 1),
        (1, "kilometer", "meter", 1000),
        (1, "inch", "meter", 0.0254),
        (1, "foot", "meter", 0.3048006096),
        (1, "yard", "meter", 0.91440183),
        (1, "mile", "meter", 1609.344),
        (1, "nautical mile", "meter", 1852),
        # Mass, in kilograms
        (1, "milligram", "kilogram", 1e-6),
        (1, "gram", "kilogram", 0.001),
        (1, "kilogram", "kilogram", 1),
        (1, "metric ton", "kilogram", 1000),
        (1, "ounce", "kilogram", 0.028349523125),
        (1, "pound", "kilogram", 0.45359237),
        (1, "stone", "kilogram", 6.35029318),
        # Volume, in liters
        (1, "milliliter", "liter", 0.001),
        (1, "cubic centimeter", "liter", 0.001),
        (1, "liter", "liter", 1),
        (1, "cubic meter", "liter", 1000),
        (1, "cubic inch", "liter", 0.016387064),
        (1, "cubic foot", "liter", 28.316846592),
        # Time, in seconds
        (1, "millisecond", "second", 0.001),
        (1, "second", "second", 1),
        (1, "minute", "second", 60),
        (1, "hour", "second", 3600),
        (1, "day", "second", 86400),
        (1, "week", "second", 604800),
        # Temperature, in kelvin
        (0, "celsius", "kelvin", 273.15),
        (1, "kelvin", "kelvin", 1),
        (32, "fahrenheit", "kelvin", 273.15),
    ],
)
def test_reference_conversion_to_base_unit(
    value: float, from_id: str, to_id: str, expected: float
) -> None:
    assert converted(value, from_id, to_id) == pytest.approx(
        expected, rel=1e-6, abs=1e-9
    )


# --- Reference conversions ---


@pytest.mark.parametrize(
    ("value", "from_id", "to_id", "expected"),
    [
        (10, "kilometer", "mile", 6.2137119224),
        (1, "mile", "kilometer", 1.609344),
        (1, "inch", "centimeter", 2.54),
        (1, "foot", "inch", 12),
        (1, "nautical_mile", "meter", 1852),
        (1, "pound", "gram", 453.59237),
        (16, "ounce", "pound", 1),
        (1, "stone", "pound", 14),
        (1, "metric_ton", "kilogram", 1000),
        (1, "liter", "cubic_centimeter", 1000),
        (1, "cubic_foot", "liter", 28.316846592),
        (1, "cubic_meter", "liter", 1000),
        (1, "week", "hour", 168),
        (1, "day", "minute", 1440),
        (90, "minute", "hour", 1.5),
        (100, "celsius", "fahrenheit", 212),
        (32, "fahrenheit", "celsius", 0),
        (0, "kelvin", "celsius", -273.15),
        (0, "celsius", "kelvin", 273.15),
        (-40, "celsius", "fahrenheit", -40),
        (98.6, "fahrenheit", "celsius", 37),
    ],
)
def test_reference_conversion(
    value: float, from_id: str, to_id: str, expected: float
) -> None:
    assert converted(value, from_id, to_id) == pytest.approx(
        expected, rel=1e-5, abs=1e-9
    )


# --- Every pair of units in a category ---

# Size of each linear unit in its category's base unit, typed here
# independently of the data modules.
LINEAR_FACTORS: dict[str, dict[str, float]] = {
    "length": {
        "millimeter": 0.001,
        "centimeter": 0.01,
        "decimeter": 0.1,
        "meter": 1,
        "kilometer": 1000,
        "inch": 0.0254,
        "foot": 0.3048,
        "yard": 0.9144,
        "mile": 1609.344,
        "nautical_mile": 1852,
    },
    "mass": {
        "milligram": 1e-6,
        "gram": 0.001,
        "kilogram": 1,
        "metric_ton": 1000,
        "ounce": 0.028349523125,
        "pound": 0.45359237,
        "stone": 6.35029318,
    },
    "volume": {
        "milliliter": 0.001,
        "cubic_centimeter": 0.001,
        "liter": 1,
        "cubic_meter": 1000,
        "cubic_inch": 0.016387064,
        "cubic_foot": 28.316846592,
    },
    "time": {
        "millisecond": 0.001,
        "second": 1,
        "minute": 60,
        "hour": 3600,
        "day": 86400,
        "week": 604800,
    },
}


# --- Test temperature cross-conversions ---

TO_KELVIN: dict[str, Callable[[float], float]] = {
    "kelvin": lambda t: t,
    "celsius": lambda t: t + 273.15,
    "fahrenheit": lambda t: (t + 459.67) * 5 / 9,
}


@pytest.mark.parametrize(
    ("value", "from_id", "to_id", "expected"),
    [(7, from_id, "kelvin", f(7)) for from_id, f in TO_KELVIN.items()],
)
def test_conversion_to_kelvin(
    value: float, from_id: str, to_id: str, expected: float
) -> None:
    assert converted(value, from_id, to_id) == pytest.approx(
        expected, rel=1e-6, abs=1e-9
    )


TO_CELCIUS: dict[str, Callable[[float], float]] = {
    "kelvin": lambda t: t - 273.15,
    "celsius": lambda t: t,
    "fahrenheit": lambda t: (t - 32) * 5 / 9,
}


@pytest.mark.parametrize(
    ("value", "from_id", "to_id", "expected"),
    [(7, from_id, "celsius", f(7)) for from_id, f in TO_CELCIUS.items()],
)
def test_conversion_to_celcius(
    value: float, from_id: str, to_id: str, expected: float
) -> None:
    assert converted(value, from_id, to_id) == pytest.approx(
        expected, rel=1e-6, abs=1e-9
    )


TO_FAHRENHEIT: dict[str, Callable[[float], float]] = {
    "kelvin": lambda t: t * 9 / 5 - 459.67,
    "celsius": lambda t: t * 9 / 5 + 32,
    "fahrenheit": lambda t: t,
}


@pytest.mark.parametrize(
    ("value", "from_id", "to_id", "expected"),
    [(7, from_id, "fahrenheit", f(7)) for from_id, f in TO_FAHRENHEIT.items()],
)
def test_conversion_to_fahrenheit(
    value: float, from_id: str, to_id: str, expected: float
) -> None:
    assert converted(value, from_id, to_id) == pytest.approx(
        expected, rel=1e-6, abs=1e-9
    )


# --- Result and inputs ---


def test_the_result_is_a_quantity_in_the_target_unit() -> None:
    result = convert(Quantity(10, unit("kilometer")), unit("mile"), REGISTRY)
    assert isinstance(result, Quantity)
    assert result.unit is unit("mile")


def test_the_original_quantity_is_not_modified() -> None:
    original = Quantity(10, unit("kilometer"))
    convert(original, unit("mile"), REGISTRY)
    assert original.value == 10
    assert original.unit is unit("kilometer")


def test_converting_to_the_same_unit_returns_the_exact_value() -> None:
    # No arithmetic, so no floating-point noise (0.1 C would not survive it).
    assert converted(0.1, "celsius", "celsius") == 0.1
    assert converted(123.456, "mile", "mile") == 123.456


# --- Edge cases ---


def test_zero_converts_to_zero_for_linear_units() -> None:
    assert converted(0, "kilometer", "mile") == 0


def test_negative_values_convert() -> None:
    assert converted(-5, "kilometer", "meter") == pytest.approx(-5000)


def test_very_large_values_convert() -> None:
    assert converted(1e300, "meter", "kilometer") == pytest.approx(1e297)


def test_very_small_values_convert() -> None:
    assert converted(1e-300, "kilometer", "meter") == pytest.approx(1e-297)


def test_a_result_too_large_to_represent_becomes_infinity() -> None:
    # Known limitation: float overflow, documented in convert().
    assert math.isinf(converted(1e308, "kilometer", "millimeter"))


def test_absolute_zero_is_the_same_in_every_scale() -> None:
    assert converted(0, "kelvin", "fahrenheit") == pytest.approx(-459.67)
    assert converted(-273.15, "celsius", "kelvin") == pytest.approx(0, abs=1e-9)


# --- Errors ---


def test_units_of_different_categories_are_rejected() -> None:
    with pytest.raises(IncompatibleUnitsError) as info:
        convert(Quantity(1, unit("kilogram")), unit("meter"), REGISTRY)
    assert info.value.from_category == "mass"
    assert info.value.to_category == "length"


@pytest.mark.parametrize(
    ("from_id", "to_id"),
    [
        ("celsius", "kilogram"),
        ("second", "liter"),
        ("liter", "celsius"),
        ("meter", "second"),
    ],
)
def test_other_cross_category_conversions_are_rejected(
    from_id: str, to_id: str
) -> None:
    with pytest.raises(IncompatibleUnitsError):
        converted(1, from_id, to_id)


def test_incompatible_units_are_a_converter_error() -> None:
    with pytest.raises(ConverterError):
        converted(1, "kilogram", "meter")


def test_a_unit_from_another_registry_is_rejected() -> None:
    stranger = Unit(id="furlong", name="furlong", symbol="fur", factor=201.168)
    with pytest.raises(ConverterError):
        convert(Quantity(1, stranger), unit("meter"), REGISTRY)
