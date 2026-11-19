"""English text for the Newfoundland and Labrador trace lines: one renderer class per line class.

Each module renders the lines of the same-named module in `tax_engine.jurisdictions.ca_nl.trace`;
this package imports them all.
"""

from __future__ import annotations

from tax_engine.jurisdictions.ca_nl.trace_english import tax_on_taxable_income

__all__ = ["tax_on_taxable_income"]
