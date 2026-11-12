"""Core's units: the generic `core/months`, `core/years` and `core/percent`."""

from tax_engine.domain.registry import Namespace
from tax_engine.domain.unit import UnitCatalog

UNITS = UnitCatalog(Namespace("core"))

MONTHS = UNITS.declare("months")
YEARS = UNITS.declare("years")
PERCENT = UNITS.declare("percent")
