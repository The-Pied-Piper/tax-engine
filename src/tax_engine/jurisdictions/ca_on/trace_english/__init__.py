"""English text for the Ontario trace lines: one renderer class per line class.

Each module renders the lines of the same-named module in `tax_engine.jurisdictions.ca_on.trace`;
this package imports them all.
"""

from __future__ import annotations

from tax_engine.jurisdictions.ca_on.trace_english import surtax_factor

__all__ = ["surtax_factor"]
