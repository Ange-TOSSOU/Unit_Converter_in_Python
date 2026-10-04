"""Mass units. Base unit: kilogram.

Sources: SI Brochure (BIPM) for the metric units; the international yard and
pound agreement (1959) for the pound, from which the ounce and the stone are
derived (1/16 and 14 pounds). The ounce is the avoirdupois ounce.
"""

from unitconverter.engine.models import Category, Unit

POUND_IN_KG = 0.45359237

MASS = Category(
    name="mass",
    base_unit_id="kilogram",
    units=(
        Unit(
            id="milligram",
            name="milligram",
            symbol="mg",
            factor=1e-6,
            aliases=("milligrams", "milligramme", "milligrammes"),
        ),
        Unit(
            id="gram",
            name="gram",
            symbol="g",
            factor=0.001,
            aliases=("grams", "gramme", "grammes"),
        ),
        Unit(
            id="kilogram",
            name="kilogram",
            symbol="kg",
            factor=1,
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
            factor=POUND_IN_KG / 16,
            aliases=("ounces",),
        ),
        Unit(
            id="pound",
            name="pound",
            symbol="lb",
            factor=POUND_IN_KG,
            aliases=("pounds", "lbs"),
        ),
        Unit(
            id="stone",
            name="stone",
            symbol="st",
            factor=POUND_IN_KG * 14,
            aliases=("stones",),
        ),
    ),
)
