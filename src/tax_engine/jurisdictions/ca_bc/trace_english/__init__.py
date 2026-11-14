"""English text for the British Columbia trace lines: one renderer class per line class.

Each module renders the lines of the same-named module in `tax_engine.jurisdictions.ca_bc.trace`;
this package imports them all.
"""

from __future__ import annotations

from tax_engine.jurisdictions.ca_bc.trace_english import tax_on_taxable_income

__all__ = ["tax_on_taxable_income"]
