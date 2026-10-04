"""Turn a name typed by a user into a unit, or into a helpful error."""

from difflib import SequenceMatcher

from unitconverter.engine.errors import UnknownUnitError, UnsupportedUnitError
from unitconverter.engine.models import Unit
from unitconverter.engine.registry import Registry
from unitconverter.utils.normalize import normalize

# At most this many unit names are suggested...
MAX_SUGGESTIONS = 3

# ...and only names at least this similar (0 to 1) to what the user typed.
# Tuned on realistic typos: 0.6 suggested unrelated units ("kilomter" also
# gave millimeter and kilogram, "ouncs" gave hour), while 0.8 missed real
# typos ("feat" for foot). 0.7 was the best balance.
SUGGESTION_CUTOFF = 0.7


def resolve(name: str, registry: Registry) -> Unit:
    """Return the unit a name refers to, or raise a helpful error.

    Raises:
        UnsupportedUnitError: the name is recognized but deliberately not
            supported (for example "gallon").
        UnknownUnitError: the name matches nothing, with suggestions when
            some unit names are close to it.
    """
    unit = registry.find_unit(name)
    if unit is not None:
        return unit
    if registry.is_unsupported(name):
        raise UnsupportedUnitError(name)
    raise UnknownUnitError(name, list(suggest_units(name, registry)))


def suggest_units(name: str, registry: Registry) -> tuple[str, ...]:
    """Return the names of the units closest to a misspelled name.

    Close matches are found among every lookup key, then mapped back to unit
    names, so a unit with several spellings is suggested only once. The best
    match comes first.
    """
    keys = registry.aliases()

    # Get keys close to name.
    close_keys = {}
    normalized_name = normalize(name)
    for key in keys:
        proximity = SequenceMatcher(None, key, normalized_name).ratio()
        if proximity < SUGGESTION_CUTOFF:
            continue

        close_keys[key] = proximity

    # Sorted best match keys by their proximity with name.
    suggestions = [
        k for k, _ in sorted(close_keys.items(), key=lambda item: item[1], reverse=True)
    ]

    return tuple(suggestions[:MAX_SUGGESTIONS])
