"""Data types describing units, categories and conversion results."""

from dataclasses import dataclass
from enum import Enum


class System(Enum):
    """Unit system a unit belongs to."""

    METRIC = "metric"
    IMPERIAL = "imperial"


@dataclass
class Unit:
    """A unit of measurement, defined relative to its category's base unit.

    A value converts to the base unit with ``value * factor + offset``.
    For purely proportional units the offset is 0.
    """

    id: str
    name: str
    symbol: str
    factor: float
    system: System
    aliases: tuple[str, ...] = ()
    offset: float = 0.0


@dataclass
class Category:
    """A group of units that can be converted into one another."""

    name: str
    base_unit_id: str
    units: tuple[Unit, ...]


@dataclass
class Quantity:
    """A numeric value expressed in a given unit, at full precision."""

    value: float
    unit: Unit
