"""English text for the Quebec trace lines: one renderer class per line class.

Each module renders the lines of the same-named module in `tax_engine.jurisdictions.ca_qc.trace`;
this package imports them all.
"""

from __future__ import annotations

from tax_engine.jurisdictions.ca_qc.trace_english import lesser_of_counts

__all__ = ["lesser_of_counts"]
