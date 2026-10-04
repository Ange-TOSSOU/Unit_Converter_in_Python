"""Unit names that are recognized but deliberately not supported.

These units have no single worldwide definition: their size differs between
countries (gallon, pint, ton, fluid ounce, cup, tablespoon, teaspoon) or
varies over time (month, year). A user who types one of them gets a clear
message, not a generic "unknown unit" error.

Plurals and common abbreviations are listed explicitly. The registry checks
that none of these names is also a supported name.
"""

UNSUPPORTED: tuple[str, ...] = (
    # Size differs between countries
    "gallon",
    "gallons",
    "gal",
    "pint",
    "pints",
    "ton",
    "tons",
    "fluid ounce",
    "fluid ounces",
    "fl oz",
    "cup",
    "cups",
    "tablespoon",
    "tablespoons",
    "tbsp",
    "teaspoon",
    "teaspoons",
    "tsp",
    # Length varies
    "month",
    "months",
    "year",
    "years",
)
