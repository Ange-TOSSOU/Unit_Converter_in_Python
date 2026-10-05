"""Tests for the resolver: names to units, unsupported names and suggestions."""

import pytest

from unitconverter.data import CATEGORIES, UNSUPPORTED
from unitconverter.engine.errors import UnknownUnitError, UnsupportedUnitError
from unitconverter.engine.models import Category, Unit
from unitconverter.engine.registry import Registry
from unitconverter.engine.resolver import MAX_SUGGESTIONS, resolve, suggest_units

REGISTRY = Registry(CATEGORIES, unsupported=UNSUPPORTED)


def make_registry(*units: Unit, base_id: str) -> Registry:
    """Build a small registry, to test the mechanics on controlled data."""
    category = Category(name="x", base_unit_id=base_id, units=units)
    return Registry([category])


# --- Names that resolve ---


@pytest.mark.parametrize(
    ("name", "unit_id"),
    [
        ("kilometer", "kilometer"),
        ("km", "kilometer"),
        ("Kilometres", "kilometer"),
        ("  FEET ", "foot"),
        ("degrees   celsius", "celsius"),
        ("K", "kelvin"),
    ],
)
def test_resolve_finds_the_unit(name: str, unit_id: str) -> None:
    assert resolve(name, REGISTRY).id == unit_id


def test_resolve_returns_the_registry_unit() -> None:
    assert resolve("miles", REGISTRY) is REGISTRY.find_unit("miles")


# --- Unsupported names ---


@pytest.mark.parametrize("name", ["gallon", "Gallons", "  PINT ", "fl oz", "year"])
def test_resolve_rejects_unsupported_names(name: str) -> None:
    with pytest.raises(UnsupportedUnitError) as info:
        resolve(name, REGISTRY)
    assert info.value.name == name


# --- Unknown names ---


def test_resolve_rejects_unknown_names_and_keeps_the_text() -> None:
    with pytest.raises(UnknownUnitError) as info:
        resolve("Blorp", REGISTRY)
    assert info.value.name == "Blorp"


@pytest.mark.parametrize("name", ["", "   "])
def test_resolve_rejects_empty_names_without_suggestions(name: str) -> None:
    with pytest.raises(UnknownUnitError) as info:
        resolve(name, REGISTRY)
    assert info.value.suggestions == ()


def test_unknown_unit_error_carries_the_suggestions() -> None:
    with pytest.raises(UnknownUnitError) as info:
        resolve("kilomter", REGISTRY)
    assert sorted(info.value.suggestions) == sorted(suggest_units("kilomter", REGISTRY))
    assert "kilometer" in info.value.suggestions


# --- Suggestions ---

# (typo, the unit that should be suggested first)
TYPOS = [
    ("metr", "meter"),
    ("kilomter", "kilometer"),
    ("KILOMTER", "kilometer"),
    ("kilogam", "kilogram"),
    ("milimeter", "millimeter"),
    ("litr", "liter"),
    ("pund", "pound"),
    ("wek", "week"),
    ("secnd", "second"),
    ("celcius", "celsius"),
    ("farenheit", "fahrenheit"),
    ("kelvn", "kelvin"),
    ("nauticalmile", "nautical mile"),
    ("nautical mil", "nautical mile"),
]


@pytest.mark.parametrize(("typo", "expected"), TYPOS)
def test_a_typo_suggests_the_right_unit_first(typo: str, expected: str) -> None:
    assert suggest_units(typo, REGISTRY)[0] == expected


@pytest.mark.parametrize(
    "name", ["blorp", "xyz", "abc", "galon", "miles per hour", "m2", ""]
)
def test_nothing_close_gives_no_suggestions(name: str) -> None:
    assert suggest_units(name, REGISTRY) == ()


def test_suggestions_are_limited() -> None:
    units = tuple(
        Unit(id=f"abcd{i}", name=f"abcd{i}", symbol=f"s{i}", factor=1)
        for i in range(1, 6)
    )
    registry = make_registry(*units, base_id="abcd1")
    suggestions = suggest_units("abcd", registry)
    assert len(suggestions) == MAX_SUGGESTIONS


def test_suggestions_are_a_tuple_of_strings() -> None:
    suggestions = suggest_units("kilomter", REGISTRY)
    assert isinstance(suggestions, tuple)
    assert all(isinstance(s, str) for s in suggestions)


def test_suggestions_never_include_unsupported_names() -> None:
    for name in ("gallo", "tonn", "yeer", "pin"):
        assert not set(suggest_units(name, REGISTRY)) & set(UNSUPPORTED)
