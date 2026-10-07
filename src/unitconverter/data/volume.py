"""Volume units. Base unit: liter.

Only units with a single worldwide definition are included. Gallons, pints,
fluid ounces, cups and spoons are excluded on purpose: their size differs
between countries.

Sources: SI Brochure (BIPM) for the metric units. The cubic inch and cubic
foot follow from the exact inch (0.0254 m) and foot (0.3048 m):
0.0254 ** 3 m3 = 0.016387064 L and 0.3048 ** 3 m3 = 28.316846592 L.
"""

from unitconverter.data.factors import FACTORS
from unitconverter.engine.models import Category, Unit

VOLUME = Category(
    name="volume",
    base_unit_id="liter",
    units=(
        Unit(
            id="milliliter",
            name="milliliter",
            symbol="ml",
            factor=FACTORS["milli"],
            aliases=("milliliters", "millilitre", "millilitres"),
        ),
        Unit(
            id="cubic_centimeter",
            name="cubic centimeter",
            symbol="cm3",
            factor=FACTORS["milli"],  # 1 cm3 = 1 mL
            aliases=(
                "cubic centimeters",
                "cubic centimetre",
                "cubic centimetres",
                "cc",
            ),
        ),
        Unit(
            id="liter",
            name="liter",
            symbol="l",
            factor=1,
            aliases=("liters", "litre", "litres"),
        ),
        Unit(
            id="cubic_meter",
            name="cubic meter",
            symbol="m3",
            factor=FACTORS["kilo"],  # 1 m3 = 1000 L
            aliases=("cubic meters", "cubic metre", "cubic metres"),
        ),
        Unit(
            id="cubic_inch",
            name="cubic inch",
            symbol="in3",
            factor=0.016387064,  # 0.0254 ** 3 m3, in liters
            aliases=("cubic inches",),
        ),
        Unit(
            id="cubic_foot",
            name="cubic foot",
            symbol="ft3",
            factor=28.316846592,  # 0.3048 ** 3 m3, in liters
            aliases=("cubic feet",),
        ),
    ),
)
