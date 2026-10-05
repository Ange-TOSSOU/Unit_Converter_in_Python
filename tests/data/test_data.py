"""Tests for the unit catalog: completeness, aliases and reference values.

The expected numbers below are written out independently of the data modules
on purpose, so a typo in a factor cannot hide behind itself.
"""

import re

import pytest

from unitconverter.data import CATEGORIES, UNSUPPORTED
from unitconverter.engine.models import Category, Unit
from unitconverter.engine.registry import Registry

REGISTRY = Registry(CATEGORIES, UNSUPPORTED)


def get_unit(name: str) -> Unit:
    unit = REGISTRY.find_unit(name)
    assert unit is not None
    return unit


# --- Catalog structure ---

EXPECTED_UNIT_IDS = {
    "length": (
        "millimeter",
        "centimeter",
        "decimeter",
        "meter",
        "kilometer",
        "inch",
        "foot",
        "yard",
        "mile",
        "nautical_mile",
    ),
    "mass": (
        "milligram",
        "gram",
        "kilogram",
        "metric_ton",
        "ounce",
        "pound",
        "stone",
    ),
    "volume": (
        "milliliter",
        "cubic_centimeter",
        "liter",
        "cubic_meter",
        "cubic_inch",
        "cubic_foot",
    ),
    "time": ("millisecond", "second", "minute", "hour", "day", "week"),
    "temperature": ("kelvin", "celsius", "fahrenheit"),
}

EXPECTED_BASE_IDS = {
    "length": "meter",
    "mass": "kilogram",
    "volume": "liter",
    "time": "second",
    "temperature": "kelvin",
}


def test_catalog_loads_into_a_registry() -> None:
    Registry(CATEGORIES)  # raises RegistryError if the data is invalid


def test_the_five_categories_are_present_in_order() -> None:
    names = [category.name for category in CATEGORIES]
    assert names == ["length", "mass", "volume", "time", "temperature"]


@pytest.mark.parametrize("category", CATEGORIES)
def test_category_contains_exactly_the_expected_units(category: Category) -> None:
    ids = tuple(unit.id for unit in category.units)
    assert sorted(ids) == sorted(EXPECTED_UNIT_IDS[category.name])


@pytest.mark.parametrize("category", CATEGORIES)
def test_category_has_the_expected_base_unit(category: Category) -> None:
    assert category.base_unit_id == EXPECTED_BASE_IDS[category.name]
    base = get_unit(category.base_unit_id)
    assert base.factor == 1
    assert base.offset == 0


def test_unit_ids_are_lowercase_snake_case() -> None:
    pattern = re.compile(r"^[a-z]+(_[a-z]+)*$")
    for category in CATEGORIES:
        for unit in category.units:
            assert pattern.match(unit.id)


def test_every_name_symbol_and_alias_is_plain_ascii() -> None:
    for category in CATEGORIES:
        for unit in category.units:
            for text in (unit.name, unit.symbol, *unit.aliases):
                assert text.isascii()


# --- Symbols and aliases ---

EXPECTED_SYMBOLS = {
    "millimeter": "mm",
    "centimeter": "cm",
    "decimeter": "dm",
    "meter": "m",
    "kilometer": "km",
    "inch": "in",
    "foot": "ft",
    "yard": "yd",
    "mile": "mi",
    "nautical_mile": "nmi",
    "milligram": "mg",
    "gram": "g",
    "kilogram": "kg",
    "metric_ton": "t",
    "ounce": "oz",
    "pound": "lb",
    "stone": "st",
    "milliliter": "ml",
    "cubic_centimeter": "cm3",
    "liter": "l",
    "cubic_meter": "m3",
    "cubic_inch": "in3",
    "cubic_foot": "ft3",
    "millisecond": "ms",
    "second": "s",
    "minute": "min",
    "hour": "h",
    "day": "d",
    "week": "wk",
    "kelvin": "K",
    "celsius": "C",
    "fahrenheit": "F",
}

EXPECTED_ALIASES = {
    "millimeter": ("millimeters", "millimetre", "millimetres"),
    "centimeter": ("centimeters", "centimetre", "centimetres"),
    "decimeter": ("decimeters", "decimetre", "decimetres"),
    "meter": ("meters", "metre", "metres"),
    "kilometer": ("kilometers", "kilometre", "kilometres"),
    "inch": ("inches",),
    "foot": ("feet",),
    "yard": ("yards",),
    "mile": ("miles",),
    "nautical_mile": ("nautical miles",),
    "milligram": ("milligrams", "milligramme", "milligrammes"),
    "gram": ("grams", "gramme", "grammes"),
    "kilogram": ("kilograms", "kilogramme", "kilogrammes", "kilo", "kilos"),
    "metric_ton": ("metric tons", "tonne", "tonnes"),
    "ounce": ("ounces",),
    "pound": ("pounds", "lbs"),
    "stone": ("stones",),
    "milliliter": ("milliliters", "millilitre", "millilitres"),
    "cubic_centimeter": (
        "cubic centimeters",
        "cubic centimetre",
        "cubic centimetres",
        "cc",
    ),
    "liter": ("liters", "litre", "litres"),
    "cubic_meter": ("cubic meters", "cubic metre", "cubic metres"),
    "cubic_inch": ("cubic inches",),
    "cubic_foot": ("cubic feet",),
    "millisecond": ("milliseconds",),
    "second": ("seconds", "sec", "secs"),
    "minute": ("minutes", "mins"),
    "hour": ("hours", "hr", "hrs"),
    "day": ("days",),
    "week": ("weeks", "wks"),
    "kelvin": ("kelvins",),
    "celsius": ("degree celsius", "degrees celsius", "centigrade"),
    "fahrenheit": ("degree fahrenheit", "degrees fahrenheit"),
}

ALIAS_CASES = [
    (alias, unit_id)
    for unit_id, aliases in EXPECTED_ALIASES.items()
    for alias in aliases
]


def test_symbol_table_covers_every_unit() -> None:
    all_ids = {unit.id for category in CATEGORIES for unit in category.units}
    assert set(EXPECTED_SYMBOLS) == all_ids
    assert set(EXPECTED_ALIASES) == all_ids


@pytest.mark.parametrize(("unit_id", "symbol"), EXPECTED_SYMBOLS.items())
def test_symbol_finds_its_unit(unit_id: str, symbol: str) -> None:
    unit = get_unit(symbol)
    assert unit.id == unit_id
    assert unit.symbol == symbol


@pytest.mark.parametrize("unit_id", EXPECTED_SYMBOLS)
def test_unit_id_name_finds_its_unit(unit_id: str) -> None:
    name = unit_id.replace("_", " ")
    assert get_unit(name).id == unit_id


@pytest.mark.parametrize(("alias", "unit_id"), ALIAS_CASES)
def test_alias_finds_its_unit(alias: str, unit_id: str) -> None:
    assert get_unit(alias).id == unit_id


def test_lookup_ignores_case_and_spacing() -> None:
    assert get_unit("  Degrees   CELSIUS ").id == "celsius"
    assert get_unit("NAUTICAL  Miles").id == "nautical_mile"


# --- Reference factors and offsets ---

# (offset, unit name, factor in the category's base unit)
REFERENCE_FO = [
    # Length, in meters
    (0, "millimeter", 0.001),
    (0, "centimeter", 0.01),
    (0, "decimeter", 0.1),
    (0, "meter", 1),
    (0, "kilometer", 1000),
    (0, "inch", 0.0254),
    (0, "foot", 0.3048006096),
    (0, "yard", 0.91440183),
    (0, "mile", 1609.344),
    (0, "nautical mile", 1852),
    # Mass, in kilograms
    (0, "milligram", 1e-6),
    (0, "gram", 0.001),
    (0, "kilogram", 1),
    (0, "metric ton", 1000),
    (0, "pound", 0.45359237),
    (0, "ounce", 0.028349523125),
    (0, "stone", 6.35029318),
    # Volume, in liters
    (0, "milliliter", 0.001),
    (0, "cubic centimeter", 0.001),
    (0, "liter", 1),
    (0, "cubic meter", 1000),
    (0, "cubic inch", 0.016387064),
    (0, "cubic foot", 28.316846592),
    # Time, in seconds
    (0, "millisecond", 0.001),
    (0, "second", 1),
    (0, "minute", 60),
    (0, "hour", 3600),
    (0, "day", 86400),
    (0, "week", 604800),
    # Temperature, in kelvin
    (273.15, "celsius", 1),
    (0, "kelvin", 1),
    (459.67, "fahrenheit", 5 / 9),
]


@pytest.mark.parametrize(("offset", "name", "factor"), REFERENCE_FO)
def test_reference_factors_and_offsets(factor: float, name: str, offset: float) -> None:
    unit = get_unit(name)
    assert unit.factor == factor and unit.offset == offset


# --- Units that must NOT exist --------------------------------------------


@pytest.mark.parametrize(
    "name",
    [
        "gallon",
        "pint",
        "ton",
        "cup",
        "tablespoon",
        "teaspoon",
        "fluid ounce",
        "tbsp",
        "tsp",
        "month",
        "year",
    ],
)
def test_regionally_ambiguous_or_variable_units_are_absent(name: str) -> None:
    assert REGISTRY.find_unit(name) is None


# --- Unsupported names ----------------------------------------------------


EXPECTED_UNSUPPORTED = (
    "gallon",
    "gallons",
    "gal",
    "pint",
    "pints",
    "ton",
    "tons",
    "fluid ounce",
    "fluid ounces",
    "fl oz",
    "cup",
    "cups",
    "tablespoon",
    "tablespoons",
    "tbsp",
    "teaspoon",
    "teaspoons",
    "tsp",
    "month",
    "months",
    "year",
    "years",
)


def test_unsupported_names_are_exactly_the_expected_ones() -> None:
    assert set(UNSUPPORTED) == set(EXPECTED_UNSUPPORTED)


def test_unsupported_names_have_no_repeats() -> None:
    assert len(set(UNSUPPORTED)) == len(UNSUPPORTED)


@pytest.mark.parametrize("name", EXPECTED_UNSUPPORTED)
def test_expected_names_are_reported_as_unsupported(name: str) -> None:
    assert REGISTRY.is_unsupported(name)
    assert REGISTRY.find_unit(name) is None


@pytest.mark.parametrize("name", ["Gallons", "  FL   OZ ", "TBSP"])
def test_unsupported_lookup_ignores_case_and_spacing(name: str) -> None:
    assert REGISTRY.is_unsupported(name)


@pytest.mark.parametrize("name", ["tonne", "tonnes", "metric ton", "kilogram", "t"])
def test_supported_look_alikes_are_not_unsupported(name: str) -> None:
    # "ton" is unsupported but "tonne" and the metric ton are fine.
    assert not REGISTRY.is_unsupported(name)
    assert REGISTRY.find_unit(name) is not None


def test_unsupported_names_are_plain_ascii() -> None:
    assert all(name.isascii() for name in UNSUPPORTED)
