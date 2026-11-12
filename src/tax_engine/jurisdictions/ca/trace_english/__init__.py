"""English text for the federal Canada trace lines: one renderer class per line class.

Each module renders the lines of the same-named module in `tax_engine.jurisdictions.ca.trace`; this
package imports them all, and `units` registers the English text of the units `ca` declares.
"""

from __future__ import annotations

from tax_engine.jurisdictions.ca.trace_english import (
    amount_by_count,
    contribution_tier,
    given_amount,
    tapered_amount,
    units,
)

__all__ = ["amount_by_count", "contribution_tier", "given_amount", "tapered_amount", "units"]
