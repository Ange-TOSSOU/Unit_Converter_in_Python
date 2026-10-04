"""Unit data: one module per category, gathered into a single tuple."""

from unitconverter.data.duration import DURATION
from unitconverter.data.length import LENGTH
from unitconverter.data.mass import MASS
from unitconverter.data.temperature import TEMPERATURE
from unitconverter.data.volume import VOLUME
from unitconverter.engine.models import Category

CATEGORIES: tuple[Category, ...] = (LENGTH, MASS, VOLUME, DURATION, TEMPERATURE)

__all__ = ["CATEGORIES"]
