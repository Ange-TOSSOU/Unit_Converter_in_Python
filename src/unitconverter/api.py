"""Public API: the only module the interfaces (CLI, GUI) need to import.

It builds the real registry from the unit data once, and hides the engine's
internals behind a few functions.
"""

from functools import lru_cache

from unitconverter.data import CATEGORIES, UNSUPPORTED
from unitconverter.engine import converter
from unitconverter.engine.errors import ConverterError
from unitconverter.engine.formatter import format_quantity
from unitconverter.engine.models import Quantity
from unitconverter.engine.registry import Registry
from unitconverter.engine.resolver import resolve

__all__ = [
    "ConverterError",
    "Quantity",
    "convert",
    "convert_and_format",
    "convert_quantity",
    "format_quantity",
    "get_registry",
    "list_units",
    "parse_quantity",
]


@lru_cache(maxsize=1)
def get_registry() -> Registry:
    """Return the registry of all supported units, built on first use."""
    return Registry(CATEGORIES, unsupported=UNSUPPORTED)


def parse_quantity(value: object, unit_name: str) -> Quantity:
    """Build a quantity from a typed value and a typed unit name.

    Raises:
        ConverterError: a subclass describing what is wrong (invalid number,
            unknown or unsupported unit).
    """
    return converter.parse(value, unit_name, get_registry())


def convert_quantity(quantity: Quantity, to_unit: str) -> Quantity:
    """Express a quantity in the unit a name refers to.

    Raises:
        ConverterError: a subclass describing what is wrong (unknown or
            unsupported unit, incompatible units).
    """
    registry = get_registry()
    target = resolve(to_unit, registry)
    return converter.convert(quantity, target, registry)


def convert(value: object, from_unit: str, to_unit: str) -> Quantity:
    """Convert a typed value between two typed unit names.

    The value is checked first, then the source unit, then the target unit.

    Raises:
        ConverterError: a subclass describing what is wrong (invalid number,
            unknown or unsupported unit, incompatible units).
    """
    return convert_quantity(parse_quantity(value, from_unit), to_unit)


def convert_and_format(value: object, from_unit: str, to_unit: str) -> str:
    """Convert and return display text such as ``6.2137 mi``."""
    return format_quantity(convert(value, from_unit, to_unit))


# For GUI purpose.
def list_units() -> dict[str, tuple[dict[str, str], ...]]:
    """Return the unit names of each category, for interface selectors."""
    return {
        category.name: tuple({unit.name: unit.symbol} for unit in category.units)
        for category in get_registry().categories
    }
