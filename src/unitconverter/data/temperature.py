"""Temperature units (absolute temperatures only). Base unit: kelvin.

A temperature converts to kelvin with ``value * factor + offset``.

Sources: SI Brochure (BIPM): 0 degrees Celsius = 273.15 K. Fahrenheit is
defined from Celsius: F = C * 9/5 + 32, so K = (F + 459.67) * 5/9.

Symbols are plain text (C, F, K), and input is plain text too (decision D43):
"celsius" works, the degree sign is not accepted.
"""

from unitconverter.engine.models import Category, Unit

TEMPERATURE = Category(
    name="temperature",
    base_unit_id="kelvin",
    units=(
        Unit(
            id="kelvin",
            name="kelvin",
            symbol="K",
            factor=1,
            aliases=("kelvins",),
        ),
        Unit(
            id="celsius",
            name="celsius",
            symbol="C",
            factor=1,
            offset=273.15,
            aliases=("degree celsius", "degrees celsius", "centigrade"),
        ),
        Unit(
            id="fahrenheit",
            name="fahrenheit",
            symbol="F",
            factor=5 / 9,
            offset=459.67 * 5 / 9,
            aliases=("degree fahrenheit", "degrees fahrenheit"),
        ),
    ),
)
