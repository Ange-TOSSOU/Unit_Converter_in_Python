"""Length units. Base unit: meter.

Sources: SI Brochure (BIPM) for the metric units; the international yard and
pound agreement (1959) for inch, foot, yard and mile; the International
Hydrographic Conference (1929) for the nautical mile.
"""

from unitconverter.data.factors import FACTORS
from unitconverter.engine.models import Category, Unit

LENGTH = Category(
    name="length",
    base_unit_id="meter",
    units=(
        Unit(
            id="millimeter",
            name="millimeter",
            symbol="mm",
            factor=FACTORS["milli"],
            aliases=("millimeters", "millimetre", "millimetres"),
        ),
        Unit(
            id="centimeter",
            name="centimeter",
            symbol="cm",
            factor=FACTORS["centi"],
            aliases=("centimeters", "centimetre", "centimetres"),
        ),
        Unit(
            id="decimeter",
            name="decimeter",
            symbol="dm",
            factor=FACTORS["deci"],
            aliases=("decimeters", "decimetre", "decimetres"),
        ),
        Unit(
            id="meter",
            name="meter",
            symbol="m",
            factor=1,
            aliases=("meters", "metre", "metres"),
        ),
        Unit(
            id="kilometer",
            name="kilometer",
            symbol="km",
            factor=FACTORS["kilo"],
            aliases=("kilometers", "kilometre", "kilometres"),
        ),
        Unit(
            id="inch",
            name="inch",
            symbol="in",
            factor=0.0254,
            aliases=("inches",),
        ),
        Unit(
            id="foot",
            name="foot",
            symbol="ft",
            factor=0.3048006096,
            aliases=("feet",),
        ),
        Unit(
            id="yard",
            name="yard",
            symbol="yd",
            factor=0.91440183,
            aliases=("yards",),
        ),
        Unit(
            id="mile",
            name="mile",
            symbol="mi",
            factor=1609.344,  # exact by definition (international mile)
            aliases=("miles",),
        ),
        Unit(
            id="nautical_mile",
            name="nautical mile",
            symbol="nmi",
            factor=1852,
            aliases=("nautical miles",),
        ),
    ),
)
