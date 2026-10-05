"""Tests for the engine's data models."""

import pytest

from unitconverter.engine.models import Category, Quantity, Unit


def make_meter() -> Unit:
    return Unit(
        id="meter",
        name="meter",
        symbol="m",
        factor=1,
    )


def make_kilometer() -> Unit:
    return Unit(
        id="kilometer",
        name="kilometer",
        symbol="km",
        factor=1000,
        aliases=("kilometre", "kilometers", "kilometres"),
    )


# --- Unit ---


def test_unit_holds_the_fields_it_was_given() -> None:
    unit = make_kilometer()
    assert unit.id == "kilometer"
    assert unit.name == "kilometer"
    assert unit.symbol == "km"
    assert unit.factor == 1000
    assert unit.aliases == ("kilometre", "kilometers", "kilometres")


def test_unit_defaults_to_no_aliases_and_no_offset() -> None:
    unit = make_meter()
    assert unit.aliases == ()
    assert unit.offset == 0.0


def test_unit_accepts_an_offset() -> None:
    celsius = Unit(
        id="celsius",
        name="celsius",
        symbol="°C",
        factor=1,
        offset=273.15,
    )
    assert celsius.offset == 273.15


def test_units_with_identical_fields_are_equal() -> None:
    assert make_kilometer() == make_kilometer()


def test_units_differing_in_one_field_are_not_equal() -> None:
    other = make_kilometer()
    other.factor = 999
    assert make_kilometer() != other


def test_unit_requires_its_mandatory_fields() -> None:
    with pytest.raises(TypeError):
        Unit(id="meter", name="meter")  # type: ignore[call-arg]


# --- Category ---


def test_category_holds_the_fields_it_was_given() -> None:
    meter = make_meter()
    kilometer = make_kilometer()
    category = Category(
        name="length",
        base_unit_id="meter",
        units=(meter, kilometer),
    )
    assert category.name == "length"
    assert category.base_unit_id == "meter"
    assert category.units == (meter, kilometer)


def test_categories_with_identical_fields_are_equal() -> None:
    first = Category(name="length", base_unit_id="meter", units=(make_meter(),))
    second = Category(name="length", base_unit_id="meter", units=(make_meter(),))
    assert first == second


def test_category_requires_arguments() -> None:
    with pytest.raises(TypeError):
        Category("length", "meter")  # type: ignore[call-arg]


# --- Quantity ---


def test_quantity_holds_its_value_and_unit() -> None:
    kilometer = make_kilometer()
    quantity = Quantity(5.0, kilometer)
    assert quantity.value == 5.0
    assert quantity.unit is kilometer


def test_quantity_can_be_built_with_keywords() -> None:
    kilometer = make_kilometer()
    assert Quantity(value=5.0, unit=kilometer) == Quantity(5.0, kilometer)


def test_quantities_with_same_value_and_unit_are_equal() -> None:
    assert Quantity(5.0, make_kilometer()) == Quantity(5.0, make_kilometer())


def test_quantities_with_different_values_are_not_equal() -> None:
    assert Quantity(5.0, make_kilometer()) != Quantity(6.0, make_kilometer())


def test_quantities_with_different_units_are_not_equal() -> None:
    assert Quantity(5.0, make_kilometer()) != Quantity(5.0, make_meter())


def test_physically_equal_quantities_in_different_units_are_not_equal() -> None:
    assert Quantity(1.0, make_kilometer()) != Quantity(1000.0, make_meter())


def test_quantity_requires_both_fields() -> None:
    with pytest.raises(TypeError):
        Quantity(5.0)  # type: ignore[call-arg]
