"""English text for the Alberta trace lines: one renderer class per line class.

Each module renders the lines of the same-named module in `tax_engine.jurisdictions.ca_ab.trace`;
this package imports them all.
"""

from __future__ import annotations

from tax_engine.jurisdictions.ca_ab.trace_english import tax_on_taxable_income

__all__ = ["tax_on_taxable_income"]
