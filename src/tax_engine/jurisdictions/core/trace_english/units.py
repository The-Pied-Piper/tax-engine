"""English text for the units of `tax_engine.jurisdictions.core.units`, registered with
`english_unit`.
"""

from __future__ import annotations

from tax_engine.adapters.inbound.trace_english.unit_text import english_unit
from tax_engine.adapters.inbound.unit_text import Placement
from tax_engine.jurisdictions.core.units import MONTHS, PERCENT, YEARS

english_unit(MONTHS.identifier, "month", "months", Placement.AFTER, spaced=True)
english_unit(YEARS.identifier, "year", "years", Placement.AFTER, spaced=True)
english_unit(PERCENT.identifier, "%", "%", Placement.AFTER, spaced=False, as_percentage=True)
