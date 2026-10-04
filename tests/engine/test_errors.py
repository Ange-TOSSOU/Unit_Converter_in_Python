"""Tests for the engine's error types."""

import pytest

from unitconverter.engine.errors import (
    ConverterError,
    IncompatibleUnitsError,
    InvalidNumberError,
    RegistryError,
    UnknownUnitError,
)

# --- ConverterError -------------------------------------------------------


def test_converter_error_is_an_exception() -> None:
    assert issubclass(ConverterError, Exception)


def test_converter_error_can_be_raised_and_caught() -> None:
    with pytest.raises(ConverterError):
        raise ConverterError("something went wrong")


def test_converter_error_exposes_message() -> None:
    error = ConverterError("something went wrong")
    assert error.message == "something went wrong"


def test_converter_error_str_matches_message() -> None:
    error = ConverterError("something went wrong")
    assert str(error) == "something went wrong"


# --- InvalidNumberError ---------------------------------------------------


def test_invalid_number_error_keeps_value() -> None:
    error = InvalidNumberError("abc")
    assert error.value == "abc"


@pytest.mark.parametrize("value", ["abc", "1,5", "12abc", "--3"])
def test_invalid_number_error_message_with_value(value: str) -> None:
    error = InvalidNumberError(value)
    assert error.message == f"InvalidNumberError: '{value}' is not a valid number."


def test_invalid_number_error_empty_string_is_shown() -> None:
    error = InvalidNumberError("")
    assert error.message == "InvalidNumberError: '' is not a valid number."


def test_invalid_number_error_none_has_useful_message() -> None:
    error = InvalidNumberError(None)
    assert error.value is None
    assert error.message == "InvalidNumberError."


def test_invalid_number_error_is_caught_as_converter_error() -> None:
    with pytest.raises(ConverterError):
        raise InvalidNumberError("abc")


# --- UnknownUnitError -----------------------------------------------------


def test_unknown_unit_error_keeps_name() -> None:
    error = UnknownUnitError("kilometre")
    assert error.name == "kilometre"


def test_unknown_unit_error_defaults_to_no_suggestions() -> None:
    error = UnknownUnitError("blorp")
    assert error.suggestions == ()


def test_unknown_unit_error_suggestions_are_stored_as_tuple() -> None:
    error = UnknownUnitError("kilometre", ["kilometer", "kilometers"])
    assert isinstance(error.suggestions, tuple)


def test_unknown_unit_error_suggestions_keep_order() -> None:
    error = UnknownUnitError("kilometre", ["kilometer", "kilometers"])
    assert error.suggestions == ("kilometer", "kilometers")


def test_unknown_unit_error_without_suggestions_has_no_hint() -> None:
    error = UnknownUnitError("blorp")
    assert error.message == "UnknownUnitError: unknown unit 'blorp'."


def test_unknown_unit_error_with_one_suggestion() -> None:
    error = UnknownUnitError("kilometre", ["kilometer"])
    assert (
        error.message
        == "UnknownUnitError: unknown unit 'kilometre'. Did you mean 'kilometer'?"
    )


def test_unknown_unit_error_with_several_suggestions() -> None:
    error = UnknownUnitError("mter", ["meter", "metre", "miter"])
    assert error.message == (
        "UnknownUnitError: unknown unit 'mter'. Did you mean 'meter', 'metre', 'miter'?"
    )


def test_unknown_unit_error_bypass_suggestions_when_no_name() -> None:
    error = UnknownUnitError(suggestions=["kilometer"])
    assert error.message == "UnknownUnitError."


def test_unknown_unit_error_message_when_no_name_nor_suggestions() -> None:
    error = UnknownUnitError()
    assert error.message == "UnknownUnitError."


def test_unknown_unit_error_is_caught_as_converter_error() -> None:
    with pytest.raises(ConverterError):
        raise UnknownUnitError("blorp")


# --- IncompatibleUnitsError -----------------------------------------------


def test_incompatible_units_error_keeps_categories() -> None:
    error = IncompatibleUnitsError("mass", "length")
    assert error.from_category == "mass"
    assert error.to_category == "length"


def test_incompatible_units_error_message_mentions_both_in_order() -> None:
    error = IncompatibleUnitsError("mass", "length")
    assert (
        error.message
        == "IncompatibleUnitsError: cannot convert from 'mass' to 'length'."
    )


def test_incompatible_units_error_message_with_from_category_omitted() -> None:
    error = IncompatibleUnitsError(to_category="length")
    assert error.message == "IncompatibleUnitsError."


def test_incompatible_units_error_message_with_to_category_omitted() -> None:
    error = IncompatibleUnitsError(from_category="mass")
    assert error.message == "IncompatibleUnitsError."


def test_incompatible_units_error_is_caught_as_converter_error() -> None:
    with pytest.raises(ConverterError):
        raise IncompatibleUnitsError("mass", "length")


# --- Shared behaviour -----------------------------------------------------

ALL_ERRORS: list[ConverterError] = [
    ConverterError("base"),
    InvalidNumberError("abc"),
    UnknownUnitError("blorp", ["meter"]),
    IncompatibleUnitsError("mass", "length"),
]

SUBCLASS_ERRORS: list[ConverterError] = ALL_ERRORS[1:]


@pytest.mark.parametrize("error", ALL_ERRORS)
def test_every_error_is_a_converter_error(error: ConverterError) -> None:
    assert isinstance(error, ConverterError)


@pytest.mark.parametrize("error", ALL_ERRORS)
def test_every_error_str_matches_message(error: ConverterError) -> None:
    assert str(error) == error.message


@pytest.mark.parametrize("error", ALL_ERRORS)
def test_every_error_message_is_not_empty(error: ConverterError) -> None:
    assert error.message.strip() != ""


# --- RegistryError --------------------------------------------------------


def test_registry_error_is_an_exception() -> None:
    assert issubclass(RegistryError, Exception)


def test_registry_error_can_be_raised_and_caught() -> None:
    with pytest.raises(RegistryError):
        raise RegistryError("Bad data.")


def test_registry_error_keeps_detail() -> None:
    assert RegistryError("Bad data.").detail == "Bad data."


def test_registry_error_message() -> None:
    assert RegistryError("Bad data.").message == "RegistryError: Bad data."


def test_registry_error_str_matches_message() -> None:
    error = RegistryError("Bad data.")
    assert str(error) == error.message


def test_registry_error_is_not_a_converter_error() -> None:
    # Protects D45: a data bug must not be hidden behind the friendly,
    # user-facing ConverterError family.
    assert not issubclass(RegistryError, ConverterError)


def test_registry_error_is_not_caught_by_converter_error_handlers() -> None:
    caught_as_converter_error = False
    try:
        raise RegistryError("Bad data.")
    except ConverterError:
        caught_as_converter_error = True
    except RegistryError:
        pass
    assert not caught_as_converter_error
