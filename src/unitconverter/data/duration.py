"""Time units. Base unit: second.

The module is called "duration" (the category is still named "time") so that
it cannot be confused with the standard-library module of the same name.
Months and years are excluded because their length varies.

All units are filed under METRIC (decision D39), although minute, hour, day
and week are not strictly metric: they are non-SI units accepted for use with
the SI (SI Brochure, BIPM).
"""

from unitconverter.engine.models import Category, Unit

DURATION = Category(
    name="time",
    base_unit_id="second",
    units=(
        Unit(
            id="millisecond",
            name="millisecond",
            symbol="ms",
            factor=0.001,
            aliases=("milliseconds",),
        ),
        Unit(
            id="second",
            name="second",
            symbol="s",
            factor=1,
            aliases=("seconds", "sec", "secs"),
        ),
        Unit(
            id="minute",
            name="minute",
            symbol="min",
            factor=60,  # 60 seconds
            aliases=("minutes", "mins"),
        ),
        Unit(
            id="hour",
            name="hour",
            symbol="h",
            factor=60 * 60,  # 60 minutes
            aliases=("hours", "hr", "hrs"),
        ),
        Unit(
            id="day",
            name="day",
            symbol="d",
            factor=60 * 60 * 24,  # 24 hours
            aliases=("days",),
        ),
        Unit(
            id="week",
            name="week",
            symbol="wk",
            factor=60 * 60 * 24 * 7,  # 7 days
            aliases=("weeks", "wks"),
        ),
    ),
)
