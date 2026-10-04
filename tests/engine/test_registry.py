"""Tests for the unit registry."""

import pytest

from unitconverter.engine.errors import RegistryError
from unitconverter.engine.models import Category, System, Unit
from unitconverter.engine.registry import Registry
from unitconverter.utils.normalize import normalize

# --- Helpers --------------------------------------------------------------


def make_unit(
    id: str = "a",
    name: str = "a",
    symbol: str = "a",
    factor: float = 1,
    system: System = System.METRIC,
    aliases: tuple[str, ...] = (),
    offset: float = 0.0,
) -> Unit:
    return Unit(id, name, symbol, factor, system, aliases, offset)


def make_category(*units: Unit, base_id: str = "a", name: str = "x") -> Category:
    return Category(name=name, base_unit_id=base_id, units=tuple(units))


METER = Unit(
    id="meter",
    name="meter",
    symbol="m",
    factor=1,
    system=System.METRIC,
    aliases=("metre", "meters", "metres"),
)
KILOMETER = Unit(
    id="kilometer",
    name="kilometer",
    symbol="km",
    factor=1000,
    system=System.METRIC,
    aliases=("kilometre", "kilometers", "kilometres"),
)

KELVIN = Unit(
    id="kelvin",
    name="kelvin",
    symbol="K",
    factor=1,
    system=System.IMPERIAL,
)
CELSIUS = Unit(
    id="celsius",
    name="celsius",
    symbol="C",
    factor=1,
    system=System.IMPERIAL,
    aliases=("degree celsius", "degrees celsius"),
    offset=273.15,
)

LENGTH = make_category(METER, KILOMETER, base_id="meter", name="length")
TEMPERATURE = make_category(KELVIN, CELSIUS, base_id="kelvin", name="temperature")


def make_registry() -> Registry:
    return Registry([LENGTH, TEMPERATURE])


# --- Lookups: happy path --------------------------------------------------


def test_find_unit_by_name() -> None:
    assert make_registry().find_unit("kilometer") is KILOMETER


def test_find_unit_by_name_ignoring_case() -> None:
    assert make_registry().find_unit("KiloMeter") is KILOMETER


def test_find_unit_by_symbol() -> None:
    assert make_registry().find_unit("km") is KILOMETER


def test_find_unit_by_symbol_ignoring_case() -> None:
    assert make_registry().find_unit("kM") is KILOMETER


def test_find_unit_by_alias() -> None:
    assert make_registry().find_unit("kilometres") is KILOMETER


def test_find_unit_by_alias_ignoring_case() -> None:
    assert make_registry().find_unit("KiloMetrES") is KILOMETER


def test_find_unit_ignores_surrounding_and_repeated_spaces() -> None:
    assert make_registry().find_unit("  Degrees   Celsius ") is CELSIUS


def test_find_unit_matches_symbols_case_insensitively() -> None:
    assert make_registry().find_unit("k") is KELVIN


def test_categories_keep_the_given_order() -> None:
    assert make_registry().categories == (LENGTH, TEMPERATURE)


def test_category_of_returns_the_unit_category() -> None:
    registry = make_registry()
    assert registry.category_of(KILOMETER) is LENGTH
    assert registry.category_of(CELSIUS) is TEMPERATURE


def test_category_of_returns_none_for_unknown_unit() -> None:
    registry = make_registry()
    assert registry.category_of(make_unit()) is None


def test_aliases_contains_normalized_keys() -> None:
    aliases = make_registry().aliases()
    expected_aliases = (
        "meter",
        "m",
        "metre",
        "meters",
        "metres",
        "kilometer",
        "km",
        "kilometre",
        "kilometers",
        "kilometres",
        "kelvin",
        "k",
        "celsius",
        "c",
        "degree celsius",
        "degrees celsius",
    )
    assert sorted(aliases) == sorted(expected_aliases)


def test_aliases_are_all_normalized() -> None:
    for key in make_registry().aliases():
        assert key == normalize(key)


def test_registry_accepts_any_iterable_of_categories() -> None:
    registry = Registry(category for category in (LENGTH, TEMPERATURE))
    assert registry.categories == (LENGTH, TEMPERATURE)


def test_unit_with_an_offset_loads() -> None:
    assert make_registry().find_unit("celsius") is CELSIUS


# --- Lookups: misses ------------------------------------------------------


@pytest.mark.parametrize("name", ["blorp", "gallon", "", "   "])
def test_find_unit_returns_none_for_unknown_names(name: str) -> None:
    assert make_registry().find_unit(name) is None


# --- Repeated names inside one unit ---------------------------------------


def test_repeating_a_name_inside_one_unit_is_ignored() -> None:
    unit = make_unit(aliases=("a", "A", "a"))
    registry = Registry([make_category(unit)])
    assert registry.aliases() == ("a",)
    assert registry.find_unit("A") is unit


# --- Validation: categories -----------------------------------------------


def test_duplicate_category_name_is_rejected() -> None:
    with pytest.raises(
        RegistryError,
        match="^RegistryError: duplicate category name 'length'.$",
    ):
        Registry([LENGTH, LENGTH])


def test_category_without_its_base_unit_is_rejected() -> None:
    category = make_category(make_unit(), base_id="zz")
    with pytest.raises(
        RegistryError,
        match="^RegistryError: category 'x' has no unit with its base id 'zz'.$",
    ):
        Registry([category])


def test_category_without_units_is_rejected() -> None:
    with pytest.raises(
        RegistryError,
        match="^RegistryError: category 'z' has no unit with its base id 'a'.$",
    ):
        Registry([make_category(name="z")])


def test_base_unit_with_wrong_factor_is_rejected() -> None:
    category = make_category(make_unit(factor=2))
    with pytest.raises(
        RegistryError,
        match="^RegistryError: base unit 'a' of category 'x' must have factor 1 and offset 0.$",
    ):
        Registry([category])


def test_base_unit_with_an_offset_is_rejected() -> None:
    category = make_category(make_unit(offset=1.0))
    with pytest.raises(
        RegistryError,
        match="^RegistryError: base unit 'a' of category 'x' must have factor 1 and offset 0.$",
    ):
        Registry([category])


# --- Validation: units ----------------------------------------------------


def test_duplicate_unit_id_in_one_category_is_rejected() -> None:
    category = make_category(make_unit(), make_unit(name="b", symbol="b"))
    with pytest.raises(
        RegistryError,
        match="^RegistryError: duplicate unit id 'a' found in category 'x'.$",
    ):
        Registry([category])


def test_duplicate_unit_id_across_categories_is_rejected() -> None:
    first = make_category(make_unit(), name="first")
    second = make_category(make_unit(name="b", symbol="b"), name="second")
    with pytest.raises(
        RegistryError,
        match="^RegistryError: duplicate unit id 'a' found in categories ('first' and 'second'|'second' and 'first').$",
    ):
        Registry([first, second])


@pytest.mark.parametrize(
    "factor", [0, -1, -0.5, float("nan"), float("inf"), float("-inf")]
)
def test_invalid_factor_is_rejected(factor: float) -> None:
    category = make_category(
        make_unit(), make_unit(id="b", name="b", symbol="b", factor=factor)
    )
    with pytest.raises(
        RegistryError,
        match=f"^RegistryError: unit 'b' has an invalid factor '{factor}': it must be positive and finite.$",
    ):
        Registry([category])


@pytest.mark.parametrize("offset", [float("nan"), float("inf"), float("-inf")])
def test_invalid_offset_is_rejected(offset: float) -> None:
    category = make_category(
        make_unit(), make_unit(id="b", name="b", symbol="b", offset=offset)
    )
    with pytest.raises(
        RegistryError,
        match=f"^RegistryError: unit 'b' has an invalid offset '{offset}': it must be finite.$",
    ):
        Registry([category])


# --- Validation: names, symbols and aliases -------------------------------


def test_empty_name_is_rejected() -> None:
    category = make_category(make_unit(name=" "))
    with pytest.raises(
        RegistryError,
        match=f"^RegistryError: unit 'a' has an empty name.$",
    ):
        Registry([category])


def test_empty_symbol_is_rejected() -> None:
    category = make_category(make_unit(symbol=""))
    with pytest.raises(
        RegistryError,
        match=f"^RegistryError: unit 'a' has an empty symbol.$",
    ):
        Registry([category])


def test_empty_alias_is_rejected() -> None:
    category = make_category(make_unit(aliases=("ok", "  ")))
    with pytest.raises(
        RegistryError,
        match=f"^RegistryError: unit 'a' has an empty alias.$",
    ):
        Registry([category])


def test_alias_shared_by_two_units_in_one_category_is_rejected() -> None:
    second = make_unit(id="b", name="b", symbol="b", aliases=("A",))
    with pytest.raises(
        RegistryError,
        match="^RegistryError: key 'a' is used by both unit ('a' and unit 'b'|'b' and unit 'a').$",
    ):
        Registry([make_category(make_unit(), second)])


def test_alias_shared_across_categories_is_rejected() -> None:
    first = make_category(make_unit(), name="first")
    other_base = make_unit(id="b", name="b", symbol="b", aliases=("a",))
    second = make_category(other_base, base_id="b", name="second")
    with pytest.raises(
        RegistryError,
        match="^RegistryError: key 'a' is used by both unit ('a' and unit 'b'|'b' and unit 'a').$",
    ):
        Registry([first, second])


def test_name_colliding_with_another_units_symbol_is_rejected() -> None:
    second = make_unit(id="b", name="a", symbol="b")
    with pytest.raises(
        RegistryError,
        match="^RegistryError: .*is used by both unit",
    ):
        Registry([make_category(make_unit(), second)])


def test_symbols_differing_only_by_case_are_rejected() -> None:
    first = make_unit(id="m1", name="m1", symbol="mm")
    second = make_unit(id="m2", name="m2", symbol="Mm")
    with pytest.raises(
        RegistryError,
        match="^RegistryError: key 'mm' is used by both unit ('m1' and unit 'm2'|'m2' and unit 'm1').$",
    ):
        Registry([make_category(first, second, base_id="m1")])
