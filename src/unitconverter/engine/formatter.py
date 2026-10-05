"""Turning numbers and quantities into display text."""

import math

from unitconverter.engine.models import Quantity

_SCIENTIFIC_FROM = 1e6  # at or above this, use scientific notation
_SCIENTIFIC_BELOW = 1e-4  # below this, use scientific notation
_MIN_DECIMALS = 4
_SIGNIFICANT_DIGITS = 4


def format_number(x: float) -> str:
    """Format a number for display.

    Rules:
    - zero is ``0``
    - at or above 1e6, or below 1e-4: scientific notation with 4 significant
      digits and no padding, such as ``1.235e9`` or ``1.234e-5``
    - otherwise: fixed notation with at least 4 decimals and at least 4
      significant digits (so ``0.000123456`` is ``0.0001235``), with trailing
      zeros removed
    - ``inf`` and ``nan`` are shown as such
    """
    if not math.isfinite(x):
        return str(x)
    if x == 0:
        return "0"
    magnitude = abs(x)
    if magnitude < _SCIENTIFIC_BELOW or magnitude >= _SCIENTIFIC_FROM:
        return _scientific(x)
    decimals = max(
        _MIN_DECIMALS,
        _SIGNIFICANT_DIGITS - 1 - math.floor(math.log10(magnitude)),
    )
    text = f"{x:.{decimals}f}"
    if abs(float(text)) >= _SCIENTIFIC_FROM:
        # Rounding pushed the value over the threshold (999999.99996 -> 1e6).
        return _scientific(x)
    return _strip_zeros(text)


def format_quantity(quantity: Quantity) -> str:
    """Format a quantity as its number followed by the unit symbol."""
    return f"{format_number(quantity.value)} {quantity.unit.symbol}"


def _scientific(x: float) -> str:
    mantissa, exponent = f"{x:.{_SIGNIFICANT_DIGITS - 1}e}".split("e")
    return f"{_strip_zeros(mantissa)}e{int(exponent)}"


def _strip_zeros(text: str) -> str:
    """Remove trailing zeros after the decimal point (the text has one)."""
    return text.rstrip("0").rstrip(".")
