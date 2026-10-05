"""Tests for the public API."""

import pytest

from unitconverter import api
from unitconverter.engine.errors import (
    ConverterError,
    IncompatibleUnitsError,
    InvalidNumberError,
    UnknownUnitError,
    UnsupportedUnitError,
)
from unitconverter.engine.models import Quantity

# --- convert ---


def test_convert_returns_a_quantity_in_the_target_unit() -> None:
    result = api.convert("10", "km", "miles")
    assert isinstance(result, Quantity)
    assert result.unit.id == "mile"
    assert result.value == pytest.approx(6.2137119223733395, rel=1e-6)


@pytest.mark.parametrize(
    ("value", "from_unit", "to_unit", "expected"),
    [
        ("100", "celsius", "fahrenheit", 212),
        (" 32 ", "Fahrenheit", "CELSIUS", 0),
        (1, "KILOMETRES", "  metres ", 1000),
        (2.5, "kg", "grams", 2500),
        ("1e3", "m", "km", 1),
        ("90", "minutes", "hours", 1.5),
    ],
)
def test_convert_accepts_flexible_input(
    value: str | float, from_unit: str, to_unit: str, expected: float
) -> None:
    result = api.convert(value, from_unit, to_unit)
    assert result.value == pytest.approx(expected, rel=1e-6, abs=1e-9)


# --- convert_and_format ---


@pytest.mark.parametrize(
    ("value", "from_unit", "to_unit", "expected"),
    [
        ("10", "km", "miles", "6.2137 mi"),
        ("100", "celsius", "fahrenheit", "212 F"),
        ("0", "kelvin", "celsius", "-273.15 C"),
        ("1", "mile", "kilometer", "1.6093 km"),
        ("5", "km", "mm", "5e6 mm"),
        ("1", "mm", "km", "1e-6 km"),
        ("0", "m", "km", "0 km"),
    ],
)
def test_convert_and_format_returns_display_text(
    value: str, from_unit: str, to_unit: str, expected: str
) -> None:
    assert api.convert_and_format(value, from_unit, to_unit) == expected


# --- Errors ---


def test_an_invalid_number_is_reported() -> None:
    with pytest.raises(InvalidNumberError):
        api.convert("abc", "km", "miles")


def test_an_unknown_source_unit_is_reported() -> None:
    with pytest.raises(UnknownUnitError) as info:
        api.convert("1", "kilomter", "miles")
    assert "kilometer" in info.value.suggestions


def test_an_unknown_target_unit_is_reported() -> None:
    with pytest.raises(UnknownUnitError) as info:
        api.convert("1", "km", "mils")
    assert info.value.name == "mils"


@pytest.mark.parametrize(
    ("from_unit", "to_unit"), [("gallon", "liter"), ("liter", "pints")]
)
def test_an_unsupported_unit_is_reported(from_unit: str, to_unit: str) -> None:
    with pytest.raises(UnsupportedUnitError):
        api.convert("1", from_unit, to_unit)


def test_units_of_different_categories_are_reported() -> None:
    with pytest.raises(IncompatibleUnitsError):
        api.convert("1", "kg", "meter")


def test_the_number_is_checked_first() -> None:
    with pytest.raises(InvalidNumberError):
        api.convert("abc", "blorp", "blorp")


def test_the_source_unit_is_checked_before_the_target_unit() -> None:
    with pytest.raises(UnknownUnitError) as info:
        api.convert("1", "blorp", "gallon")
    assert info.value.name == "blorp"


@pytest.mark.parametrize(
    ("value", "from_unit", "to_unit"),
    [
        ("abc", "km", "miles"),
        ("1", "blorp", "miles"),
        ("1", "gallon", "liter"),
        ("1", "kg", "meter"),
    ],
)
def test_every_user_error_is_a_converter_error(
    value: str, from_unit: str, to_unit: str
) -> None:
    with pytest.raises(ConverterError):
        api.convert_and_format(value, from_unit, to_unit)


# --- Registry and unit list ---


def test_the_registry_is_built_only_once() -> None:
    assert api.get_registry() is api.get_registry()


def test_list_units_returns_the_five_categories() -> None:
    assert list(api.list_units()) == [
        "length",
        "mass",
        "volume",
        "time",
        "temperature",
    ]


def test_list_units_returns_readable_unit_names() -> None:
    units = api.list_units()
    assert {"kilometer": "km"} in units["length"]
    assert {"nautical mile": "nmi"} in units["length"]
    assert units["temperature"] == (
        {"kelvin": "K"},
        {"celsius": "C"},
        {"fahrenheit": "F"},
    )


def test_every_listed_unit_name_can_be_converted_from() -> None:
    for names in api.list_units().values():
        for name_key in names:
            keys = [n for n in name_key]
            assert len(keys) == 1
            name = keys[0]
            assert api.convert("1", name, name).value == 1


# --- Building blocks: parse_quantity and convert_quantity ---


def test_parse_quantity_builds_a_quantity() -> None:
    quantity = api.parse_quantity("10", "Kilometres")
    assert quantity.value == 10.0
    assert quantity.unit.symbol == "km"


def test_parse_quantity_reports_the_number_first() -> None:
    with pytest.raises(InvalidNumberError):
        api.parse_quantity("abc", "blorp")


def test_parse_quantity_reports_an_unknown_unit() -> None:
    with pytest.raises(UnknownUnitError):
        api.parse_quantity("1", "blorp")


def test_convert_quantity_converts_to_a_named_unit() -> None:
    result = api.convert_quantity(api.parse_quantity("10", "km"), "miles")
    assert result.unit.symbol == "mi"
    assert result.value == pytest.approx(6.2137119223733395, rel=1e-6)


def test_convert_quantity_does_not_modify_its_input() -> None:
    quantity = api.parse_quantity("10", "km")
    api.convert_quantity(quantity, "miles")
    assert quantity.value == 10.0
    assert quantity.unit.symbol == "km"


def test_convert_quantity_rejects_an_unsupported_target() -> None:
    with pytest.raises(UnsupportedUnitError):
        api.convert_quantity(api.parse_quantity("1", "liter"), "gallon")


def test_convert_quantity_rejects_incompatible_units() -> None:
    with pytest.raises(IncompatibleUnitsError):
        api.convert_quantity(api.parse_quantity("1", "kg"), "meter")


def test_convert_is_parse_then_convert() -> None:
    direct = api.convert("10", "km", "miles")
    composed = api.convert_quantity(api.parse_quantity("10", "km"), "miles")
    assert direct == composed


# --- What the interfaces can import ---


def test_the_api_exposes_what_the_interfaces_need() -> None:
    assert api.ConverterError is ConverterError
    assert api.Quantity is Quantity
    assert api.format_quantity(api.convert("10", "km", "miles")) == "6.2137 mi"


def test_every_exported_name_exists() -> None:
    for name in api.__all__:
        assert hasattr(api, name), name
