"""English text for the federal Canada trace lines: one renderer class per line class.

Each module renders the lines of the module of the same name in
`tax_engine.jurisdictions.ca.trace`,
registering its renderers with `@english_renderer`; this package imports every one of them.
"""

from __future__ import annotations

from tax_engine.jurisdictions.ca.trace_english import (
    amount_by_count,
    contribution_tier,
    tapered_amount,
)

__all__ = ["amount_by_count", "contribution_tier", "tapered_amount"]
