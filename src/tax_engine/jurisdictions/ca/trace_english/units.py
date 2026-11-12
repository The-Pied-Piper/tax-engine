"""English text for the units of `tax_engine.jurisdictions.ca.units`, registered with
`english_unit`.
"""

from __future__ import annotations

from tax_engine.adapters.inbound.trace_english.unit_text import english_unit
from tax_engine.adapters.inbound.unit_text import Placement
from tax_engine.jurisdictions.ca.units import CAD

english_unit(CAD.identifier, "CA$", "CA$", Placement.BEFORE, spaced=False)
