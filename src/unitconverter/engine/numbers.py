"""Reading numbers typed by a user."""

import math

from unitconverter.engine.errors import InvalidNumberError


def parse_number(value: object) -> float:
    """Return ``value`` as a finite float, or raise InvalidNumberError.

    Accepts ints and floats, and text in Python's float syntax (``5``,
    ``-2.5``, ``1e3``) with surrounding spaces ignored. Text must be plain
    ASCII with a decimal point: a decimal comma, thousands separators,
    underscores and non-ASCII digits are rejected, as are ``nan``, ``inf``
    and values too large for a float. Anything that is not text or a number
    (``None``, booleans, lists) is rejected too.

    The parameter is typed ``object`` on purpose: interfaces hand over raw
    user input, and rejecting bad input is this function's job.
    """
    if isinstance(value, bool) or not isinstance(value, str | int | float):
        raise InvalidNumberError(value)

    candidate = value.strip() if isinstance(value, str) else value

    if isinstance(candidate, str) and (not candidate.isascii() or "_" in candidate):
        raise InvalidNumberError(value)

    # Try to convert the number in float.
    try:
        number = float(candidate)
    except (ValueError, OverflowError):
        raise InvalidNumberError(value) from None

    if not math.isfinite(number):
        raise InvalidNumberError(value)

    return number
