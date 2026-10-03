"""Tests for the unit-name normalization helper."""

import pytest

from unitconverter.utils.normalize import normalize

# --- Case -----------------------------------------------------------------


@pytest.mark.parametrize("name", ["celsius", "Celsius", "CELSIUS", "cElSiUs"])
def test_case_is_ignored(name: str) -> None:
    assert normalize(name) == "celsius"


def test_casefold_handles_non_english_letters() -> None:
    # casefold (not lower) so that "ß" and "SS" compare equal.
    assert normalize("Straße") == normalize("STRASSE")


# --- Whitespace -----------------------------------------------------------


def test_leading_and_trailing_whitespace_is_removed() -> None:
    assert normalize("  celsius  ") == "celsius"


def test_repeated_inner_spaces_are_collapsed() -> None:
    assert normalize("degrees    celsius") == "degrees celsius"


def test_tabs_and_newlines_count_as_whitespace() -> None:
    assert normalize("\tdegrees\n celsius\t") == "degrees celsius"


def test_non_breaking_space_counts_as_whitespace() -> None:
    # Written as an escape so the exact character is visible.
    assert normalize("nautical\u00a0 mile") == "nautical mile"


# --- Empty input ----------------------------------------------------------


@pytest.mark.parametrize("name", ["", " ", "   ", "\t\n"])
def test_empty_and_whitespace_only_input_returns_empty_string(name: str) -> None:
    assert normalize(name) == ""


# --- What normalize must not do -------------------------------------------


@pytest.mark.parametrize("name", ["feet", "inches", "metres", "kilometers"])
def test_plurals_are_left_untouched(name: str) -> None:
    assert normalize(name) == name


def test_spelling_is_not_corrected() -> None:
    assert normalize("Kilometre") == "kilometre"


# --- Properties -----------------------------------------------------------


@pytest.mark.parametrize(
    "name",
    [
        "Celsius",
        "  DEGREES   Celsius ",
        "nautical\u00a0 MILE",
        "Straße",
        "",
        "   ",
        "km",
    ],
)
def test_normalize_is_idempotent(name: str) -> None:
    once = normalize(name)
    assert normalize(once) == once


def test_non_ascii_input_does_not_crash() -> None:
    assert normalize("  Ünït ñame 单位 ") == "ünït ñame 单位"
