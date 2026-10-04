"""Registry of units: validates unit data and provides fast lookups."""

import math
from collections.abc import Iterable

from unitconverter.engine.errors import RegistryError
from unitconverter.engine.models import Category, Unit
from unitconverter.utils.normalize import normalize


class Registry:
    """Holds every category and unit, and refuses to load invalid data.

    All validation happens in the constructor, before the registry exists,
    so a half-built registry can never be used. Lookups are by normalized
    name, symbol or alias. The registry only looks things up: deciding what
    a miss means (unknown, unsupported, suggestions) is the resolver's job.
    """

    def __init__(self, categories: Iterable[Category]) -> None:
        category_list = tuple(categories)
        category_names: set[str] = set()
        units_category_list: dict[str, Category] = {}
        keys_unit_list: dict[str, Unit] = {}

        for category in category_list:
            # Check there is no duplicate category ie no categories with same name.
            if category.name in category_names:
                raise RegistryError(f"duplicate category name '{category.name}'.")
            category_names.add(category.name)

            check_base_unit(category)

            for unit in category.units:
                # A unit can't belong to two different categories.
                # Also, check there is no duplicate units in one category.
                c = units_category_list.get(unit.id)
                if c:
                    if category == c:
                        raise RegistryError(
                            f"duplicate unit id '{unit.id}' "
                            f"found in category '{category.name}'."
                        )
                    else:
                        raise RegistryError(
                            f"duplicate unit id '{unit.id}' "
                            f"found in categories '{category.name}' and '{c.name}'."
                        )

                check_numbers(unit)

                # Check two different units can't share a same name, symbol or alias.
                for key in keys_of(unit):
                    owner = keys_unit_list.get(key)
                    if owner is not None and owner.id != unit.id:
                        raise RegistryError(
                            f"key '{key}' is used by both unit '{owner.id}' "
                            f"and unit '{unit.id}'."
                        )
                    # Keep track to which unit a key belongs.
                    keys_unit_list[key] = unit

                # Keep track to which category a unit belongs.
                units_category_list[unit.id] = category

        self._categories = category_list
        self._units_category_list = units_category_list
        self._keys_unit_list = keys_unit_list
        self._aliases = tuple(keys_unit_list)

    @property
    def categories(self) -> tuple[Category, ...]:
        """All categories, in the order they were given."""
        return self._categories

    def aliases(self) -> tuple[str, ...]:
        """Every normalized lookup key, e.g. for "did you mean" suggestions."""
        return self._aliases

    def category_of(self, unit: Unit) -> Category | None:
        """Return the category of a unit, looked up by the unit's id."""
        try:
            return self._units_category_list[unit.id]
        except KeyError:
            return None
            # raise RegistryError(f"unit '{unit.id}' is not in this registry.")

    def find_unit(self, name: str) -> Unit | None:
        """Return the unit matching a name, symbol or alias, or None."""
        return self._keys_unit_list.get(normalize(name))


def check_base_unit(category: Category) -> None:
    # Check the base_unit comes from the list of units.
    base: Unit | None = None
    for unit in category.units:
        if category.base_unit_id == unit.id:
            base = unit
            break

    if base is None:
        raise RegistryError(
            f"category '{category.name}' has no unit with its base id "
            f"'{category.base_unit_id}'."
        )

    # Check base factor and offset values.
    if base.factor != 1 or base.offset != 0:
        raise RegistryError(
            f"base unit '{base.id}' of category '{category.name}' must have "
            f"factor 1 and offset 0."
        )


def check_numbers(unit: Unit) -> None:
    # Check unit factor and offset values.
    if not (math.isfinite(unit.factor) and unit.factor > 0):
        raise RegistryError(
            f"unit '{unit.id}' has an invalid factor '{unit.factor}': "
            f"it must be positive and finite."
        )
    if not math.isfinite(unit.offset):
        raise RegistryError(
            f"unit '{unit.id}' has an invalid offset '{unit.offset}': "
            f"it must be finite."
        )


def keys_of(unit: Unit) -> list[str]:
    # Check that name, symbol and aliases fields are not empty.
    labelled = [("name", unit.name), ("symbol", unit.symbol)]
    labelled += [("alias", alias) for alias in unit.aliases]

    keys: list[str] = []
    for label, text in labelled:
        key = normalize(text)
        if key == "":
            raise RegistryError(f"unit '{unit.id}' has an empty {label}.")
        keys.append(key)

    return keys
