"""Reading quantities and converting them between units."""

from unitconverter.engine.errors import ConverterError, IncompatibleUnitsError
from unitconverter.engine.models import Quantity, Unit
from unitconverter.engine.numbers import parse_number
from unitconverter.engine.registry import Registry
from unitconverter.engine.resolver import resolve


def parse(value: object, unit_name: str, registry: Registry) -> Quantity:
    """Build a quantity from a typed value and a typed unit name.

    The number is checked first, then the unit, so when both are wrong the
    error is about the number.

    Raises:
        InvalidNumberError: the value is not a finite number.
        UnsupportedUnitError: the unit is recognized but not supported.
        UnknownUnitError: the unit is not known.
    """
    number = parse_number(value)
    unit = resolve(unit_name, registry)
    return Quantity(number, unit)


def convert(quantity: Quantity, target_unit: Unit, registry: Registry) -> Quantity:
    """Express a quantity in another unit of the same category.

    Every unit is defined relative to its category's base unit, so the value
    goes to the base unit and from there to the target unit. The original
    quantity is not modified. A value too large to represent after conversion
    becomes ``inf``.

    Raises:
        IncompatibleUnitsError: the units belong to different categories.
    """
    # Check the conversion is possible.
    from_category = registry.category_of(quantity.unit)
    to_category = registry.category_of(target_unit)

    # Check a category were found.
    if from_category is None:
        raise ConverterError(
            f"unit '{quantity.unit.id}' has no category in the registry."
        )
    if to_category is None:
        raise ConverterError(
            f"unit '{target_unit.id}' has no category in the registry."
        )

    # We convert in a same category.
    if from_category.name != to_category.name:
        raise IncompatibleUnitsError(from_category.name, to_category.name)

    if quantity.unit.id == target_unit.id:
        # Same unit: skip the arithmetic so the value comes back exactly.
        return Quantity(quantity.value, target_unit)

    # Perform the calculation.
    # First convert to the base unit.
    base_value = (quantity.value + quantity.unit.offset) * quantity.unit.factor
    # Then convert the value obtained above to the target unit.
    value = base_value / target_unit.factor - target_unit.offset
    return Quantity(value, target_unit)
