"""Federal Canada's units: the Canadian dollar, `ca/cad`."""

from tax_engine.domain.registry import Namespace
from tax_engine.domain.unit import UnitCatalog

UNITS = UnitCatalog(Namespace("ca"))

CAD = UNITS.declare("cad")
