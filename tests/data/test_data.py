"""Tests for the unit catalog: completeness, aliases and reference values.

The expected numbers below are written out independently of the data modules
on purpose, so a typo in a factor cannot hide behind itself.
"""

import re

import pytest

from unitconverter.data import CATEGORIES, UNSUPPORTED
from unitconverter.data.factors import FACTORS
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


# --- Units that must NOT exist ---


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


# --- Unsupported names ---


EXPECTED_UNSUPPORTED = (
    "decameter",
    "decameters",
    "decametre",
    "decametres",
    "decasecond",
    "decaseconds",
    "decagram",
    "decagrams",
    "decagramme",
    "decagrammes",
    "decacelcius",
    "decadegree celsius",
    "decadegrees celsius",
    "decacentigrade",
    "decakelvin",
    "decakelvins",
    "decafahrenheit",
    "decadegree fahrenheit",
    "decadegrees fahrenheit",
    "decaliter",
    "decaliters",
    "decalitre",
    "decalitres",
    "kilosecond",
    "kiloseconds",
    "kilocelcius",
    "kilodegree celsius",
    "kilodegrees celsius",
    "kilocentigrade",
    "kilokelvin",
    "kilokelvins",
    "kilofahrenheit",
    "kilodegree fahrenheit",
    "kilodegrees fahrenheit",
    "kiloliter",
    "kiloliters",
    "kilolitre",
    "kilolitres",
    "megameter",
    "megameters",
    "megametre",
    "megametres",
    "megasecond",
    "megaseconds",
    "megagram",
    "megagrams",
    "megagramme",
    "megagrammes",
    "megacelcius",
    "megadegree celsius",
    "megadegrees celsius",
    "megacentigrade",
    "megakelvin",
    "megakelvins",
    "megafahrenheit",
    "megadegree fahrenheit",
    "megadegrees fahrenheit",
    "megaliter",
    "megaliters",
    "megalitre",
    "megalitres",
    "gigameter",
    "gigameters",
    "gigametre",
    "gigametres",
    "gigasecond",
    "gigaseconds",
    "gigagram",
    "gigagrams",
    "gigagramme",
    "gigagrammes",
    "gigacelcius",
    "gigadegree celsius",
    "gigadegrees celsius",
    "gigacentigrade",
    "gigakelvin",
    "gigakelvins",
    "gigafahrenheit",
    "gigadegree fahrenheit",
    "gigadegrees fahrenheit",
    "gigaliter",
    "gigaliters",
    "gigalitre",
    "gigalitres",
    "terameter",
    "terameters",
    "terametre",
    "terametres",
    "terasecond",
    "teraseconds",
    "teragram",
    "teragrams",
    "teragramme",
    "teragrammes",
    "teracelcius",
    "teradegree celsius",
    "teradegrees celsius",
    "teracentigrade",
    "terakelvin",
    "terakelvins",
    "terafahrenheit",
    "teradegree fahrenheit",
    "teradegrees fahrenheit",
    "teraliter",
    "teraliters",
    "teralitre",
    "teralitres",
    "petameter",
    "petameters",
    "petametre",
    "petametres",
    "petasecond",
    "petaseconds",
    "petagram",
    "petagrams",
    "petagramme",
    "petagrammes",
    "petacelcius",
    "petadegree celsius",
    "petadegrees celsius",
    "petacentigrade",
    "petakelvin",
    "petakelvins",
    "petafahrenheit",
    "petadegree fahrenheit",
    "petadegrees fahrenheit",
    "petaliter",
    "petaliters",
    "petalitre",
    "petalitres",
    "exameter",
    "exameters",
    "exametre",
    "exametres",
    "exasecond",
    "exaseconds",
    "exagram",
    "exagrams",
    "exagramme",
    "exagrammes",
    "exacelcius",
    "exadegree celsius",
    "exadegrees celsius",
    "exacentigrade",
    "exakelvin",
    "exakelvins",
    "exafahrenheit",
    "exadegree fahrenheit",
    "exadegrees fahrenheit",
    "exaliter",
    "exaliters",
    "exalitre",
    "exalitres",
    "zettameter",
    "zettameters",
    "zettametre",
    "zettametres",
    "zettasecond",
    "zettaseconds",
    "zettagram",
    "zettagrams",
    "zettagramme",
    "zettagrammes",
    "zettacelcius",
    "zettadegree celsius",
    "zettadegrees celsius",
    "zettacentigrade",
    "zettakelvin",
    "zettakelvins",
    "zettafahrenheit",
    "zettadegree fahrenheit",
    "zettadegrees fahrenheit",
    "zettaliter",
    "zettaliters",
    "zettalitre",
    "zettalitres",
    "yottameter",
    "yottameters",
    "yottametre",
    "yottametres",
    "yottasecond",
    "yottaseconds",
    "yottagram",
    "yottagrams",
    "yottagramme",
    "yottagrammes",
    "yottacelcius",
    "yottadegree celsius",
    "yottadegrees celsius",
    "yottacentigrade",
    "yottakelvin",
    "yottakelvins",
    "yottafahrenheit",
    "yottadegree fahrenheit",
    "yottadegrees fahrenheit",
    "yottaliter",
    "yottaliters",
    "yottalitre",
    "yottalitres",
    "ronnameter",
    "ronnameters",
    "ronnametre",
    "ronnametres",
    "ronnasecond",
    "ronnaseconds",
    "ronnagram",
    "ronnagrams",
    "ronnagramme",
    "ronnagrammes",
    "ronnacelcius",
    "ronnadegree celsius",
    "ronnadegrees celsius",
    "ronnacentigrade",
    "ronnakelvin",
    "ronnakelvins",
    "ronnafahrenheit",
    "ronnadegree fahrenheit",
    "ronnadegrees fahrenheit",
    "ronnaliter",
    "ronnaliters",
    "ronnalitre",
    "ronnalitres",
    "quettameter",
    "quettameters",
    "quettametre",
    "quettametres",
    "quettasecond",
    "quettaseconds",
    "quettagram",
    "quettagrams",
    "quettagramme",
    "quettagrammes",
    "quettacelcius",
    "quettadegree celsius",
    "quettadegrees celsius",
    "quettacentigrade",
    "quettakelvin",
    "quettakelvins",
    "quettafahrenheit",
    "quettadegree fahrenheit",
    "quettadegrees fahrenheit",
    "quettaliter",
    "quettaliters",
    "quettalitre",
    "quettalitres",
    "decisecond",
    "deciseconds",
    "decigram",
    "decigrams",
    "decigramme",
    "decigrammes",
    "decicelcius",
    "decidegree celsius",
    "decidegrees celsius",
    "decicentigrade",
    "decikelvin",
    "decikelvins",
    "decifahrenheit",
    "decidegree fahrenheit",
    "decidegrees fahrenheit",
    "deciliter",
    "deciliters",
    "decilitre",
    "decilitres",
    "centisecond",
    "centiseconds",
    "centigram",
    "centigrams",
    "centigramme",
    "centigrammes",
    "centicelcius",
    "centidegree celsius",
    "centidegrees celsius",
    "centicentigrade",
    "centikelvin",
    "centikelvins",
    "centifahrenheit",
    "centidegree fahrenheit",
    "centidegrees fahrenheit",
    "centiliter",
    "centiliters",
    "centilitre",
    "centilitres",
    "millicelcius",
    "millidegree celsius",
    "millidegrees celsius",
    "millicentigrade",
    "millikelvin",
    "millikelvins",
    "millifahrenheit",
    "millidegree fahrenheit",
    "millidegrees fahrenheit",
    "micrometer",
    "micrometers",
    "micrometre",
    "micrometres",
    "microsecond",
    "microseconds",
    "microgram",
    "micrograms",
    "microgramme",
    "microgrammes",
    "microcelcius",
    "microdegree celsius",
    "microdegrees celsius",
    "microcentigrade",
    "microkelvin",
    "microkelvins",
    "microfahrenheit",
    "microdegree fahrenheit",
    "microdegrees fahrenheit",
    "microliter",
    "microliters",
    "microlitre",
    "microlitres",
    "nanometer",
    "nanometers",
    "nanometre",
    "nanometres",
    "nanosecond",
    "nanoseconds",
    "nanogram",
    "nanograms",
    "nanogramme",
    "nanogrammes",
    "nanocelcius",
    "nanodegree celsius",
    "nanodegrees celsius",
    "nanocentigrade",
    "nanokelvin",
    "nanokelvins",
    "nanofahrenheit",
    "nanodegree fahrenheit",
    "nanodegrees fahrenheit",
    "nanoliter",
    "nanoliters",
    "nanolitre",
    "nanolitres",
    "picometer",
    "picometers",
    "picometre",
    "picometres",
    "picosecond",
    "picoseconds",
    "picogram",
    "picograms",
    "picogramme",
    "picogrammes",
    "picocelcius",
    "picodegree celsius",
    "picodegrees celsius",
    "picocentigrade",
    "picokelvin",
    "picokelvins",
    "picofahrenheit",
    "picodegree fahrenheit",
    "picodegrees fahrenheit",
    "picoliter",
    "picoliters",
    "picolitre",
    "picolitres",
    "femtometer",
    "femtometers",
    "femtometre",
    "femtometres",
    "femtosecond",
    "femtoseconds",
    "femtogram",
    "femtograms",
    "femtogramme",
    "femtogrammes",
    "femtocelcius",
    "femtodegree celsius",
    "femtodegrees celsius",
    "femtocentigrade",
    "femtokelvin",
    "femtokelvins",
    "femtofahrenheit",
    "femtodegree fahrenheit",
    "femtodegrees fahrenheit",
    "femtoliter",
    "femtoliters",
    "femtolitre",
    "femtolitres",
    "attometer",
    "attometers",
    "attometre",
    "attometres",
    "attosecond",
    "attoseconds",
    "attogram",
    "attograms",
    "attogramme",
    "attogrammes",
    "attocelcius",
    "attodegree celsius",
    "attodegrees celsius",
    "attocentigrade",
    "attokelvin",
    "attokelvins",
    "attofahrenheit",
    "attodegree fahrenheit",
    "attodegrees fahrenheit",
    "attoliter",
    "attoliters",
    "attolitre",
    "attolitres",
    "zeptometer",
    "zeptometers",
    "zeptometre",
    "zeptometres",
    "zeptosecond",
    "zeptoseconds",
    "zeptogram",
    "zeptograms",
    "zeptogramme",
    "zeptogrammes",
    "zeptocelcius",
    "zeptodegree celsius",
    "zeptodegrees celsius",
    "zeptocentigrade",
    "zeptokelvin",
    "zeptokelvins",
    "zeptofahrenheit",
    "zeptodegree fahrenheit",
    "zeptodegrees fahrenheit",
    "zeptoliter",
    "zeptoliters",
    "zeptolitre",
    "zeptolitres",
    "yoctometer",
    "yoctometers",
    "yoctometre",
    "yoctometres",
    "yoctosecond",
    "yoctoseconds",
    "yoctogram",
    "yoctograms",
    "yoctogramme",
    "yoctogrammes",
    "yoctocelcius",
    "yoctodegree celsius",
    "yoctodegrees celsius",
    "yoctocentigrade",
    "yoctokelvin",
    "yoctokelvins",
    "yoctofahrenheit",
    "yoctodegree fahrenheit",
    "yoctodegrees fahrenheit",
    "yoctoliter",
    "yoctoliters",
    "yoctolitre",
    "yoctolitres",
    "rontometer",
    "rontometers",
    "rontometre",
    "rontometres",
    "rontosecond",
    "rontoseconds",
    "rontogram",
    "rontograms",
    "rontogramme",
    "rontogrammes",
    "rontocelcius",
    "rontodegree celsius",
    "rontodegrees celsius",
    "rontocentigrade",
    "rontokelvin",
    "rontokelvins",
    "rontofahrenheit",
    "rontodegree fahrenheit",
    "rontodegrees fahrenheit",
    "rontoliter",
    "rontoliters",
    "rontolitre",
    "rontolitres",
    "quectometer",
    "quectometers",
    "quectometre",
    "quectometres",
    "quectosecond",
    "quectoseconds",
    "quectogram",
    "quectograms",
    "quectogramme",
    "quectogrammes",
    "quectocelcius",
    "quectodegree celsius",
    "quectodegrees celsius",
    "quectocentigrade",
    "quectokelvin",
    "quectokelvins",
    "quectofahrenheit",
    "quectodegree fahrenheit",
    "quectodegrees fahrenheit",
    "quectoliter",
    "quectoliters",
    "quectolitre",
    "quectolitres",
    "radian",
    "steradian",
    "hertz",
    "newton",
    "pascal",
    "joule",
    "watt",
    "coulomb",
    "volt",
    "farad",
    "ohm",
    "siemens",
    "weber",
    "tesla",
    "henry",
    "lumen",
    "lux",
    "becquerel",
    "gray",
    "sievert",
    "katal",
    "ampere",
    "mole",
    "candela",
    "degree",
    "are",
    "hectare",
    "barn",
    "angstrom",
    "bar",
    "dalton",
    "astronomical unit",
    "knot",
    "electronvolt",
    "neper",
    "bel",
    "decibel",
    "var",
    "square meter",
    "micron",
    "erg",
    "dyne",
    "calorie",
    "poise",
    "stilb",
    # Size differs between countries
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
    # Length varies
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


# --- Supported names and aliases ---

SUPPORTED_NAMES_AND_ALIASES = []
SUPPORTED_NAMES_AND_ALIASES.extend([name for name in EXPECTED_ALIASES])
for category in CATEGORIES:
    for unit in category.units:
        name_and_aliases = [unit.name]
        name_and_aliases.extend(list(unit.aliases))
        SUPPORTED_NAMES_AND_ALIASES.extend(name_and_aliases)


@pytest.mark.parametrize("name", SUPPORTED_NAMES_AND_ALIASES)
def test_no_supported_units_is_also_unsupported(name: str) -> None:
    assert not REGISTRY.is_unsupported(name)


# --- SI prefixes ---

EXPECTED_FACTORS: dict[str, float] = {
    "deca": 1e1,
    "hecto": 1e2,
    "kilo": 1e3,
    "mega": 1e6,
    "giga": 1e9,
    "tera": 1e12,
    "peta": 1e15,
    "exa": 1e18,
    "zetta": 1e21,
    "yotta": 1e24,
    "ronna": 1e27,
    "quetta": 1e30,
    "deci": 1e-1,
    "centi": 1e-2,
    "milli": 1e-3,
    "micro": 1e-6,
    "nano": 1e-9,
    "pico": 1e-12,
    "femto": 1e-15,
    "atto": 1e-18,
    "zepto": 1e-21,
    "yocto": 1e-24,
    "ronto": 1e-27,
    "quecto": 1e-30,
}


def test_units_factors_are_exactly_the_expected_ones() -> None:
    assert FACTORS == EXPECTED_FACTORS
