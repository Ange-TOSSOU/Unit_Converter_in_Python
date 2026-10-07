"""Mass units. Base unit: kilogram.

Sources: SI Brochure (BIPM) for the metric units; the international yard and
pound agreement (1959) for the pound, from which the ounce and the stone are
derived (1/16 and 14 pounds). The ounce is the avoirdupois ounce.
"""

from unitconverter.data.factors import FACTORS
from unitconverter.engine.models import Category, Unit

_POUND_IN_KG = 0.45359237
_SCALE = 1e-3

MASS = Category(
    name="mass",
    base_unit_id="kilogram",
    units=(
        Unit(
            id="milligram",
            name="milligram",
            symbol="mg",
            factor=FACTORS["milli"] * _SCALE,
            aliases=("milligrams", "milligramme", "milligrammes"),
        ),
        Unit(
            id="gram",
            name="gram",
            symbol="g",
            factor=_SCALE,
            aliases=("grams", "gramme", "grammes"),
        ),
        Unit(
            id="kilogram",
            name="kilogram",
            symbol="kg",
            factor=FACTORS["kilo"] * _SCALE,
            aliases=("kilograms", "kilogramme", "kilogrammes", "kilo", "kilos"),
        ),
        Unit(
            id="metric_ton",
            name="metric ton",
            symbol="t",
            factor=1000,
            aliases=("metric tons", "tonne", "tonnes"),
        ),
        Unit(
            id="ounce",
            name="ounce",
            symbol="oz",
            factor=_POUND_IN_KG / 16,
            aliases=("ounces",),
        ),
        Unit(
            id="pound",
            name="pound",
            symbol="lb",
            factor=_POUND_IN_KG,
            aliases=("pounds", "lbs"),
        ),
        Unit(
            id="stone",
            name="stone",
            symbol="st",
            factor=_POUND_IN_KG * 14,
            aliases=("stones",),
        ),
    ),
)
