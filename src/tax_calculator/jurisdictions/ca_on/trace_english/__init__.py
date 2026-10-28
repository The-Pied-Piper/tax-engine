"""English text for the Ontario trace lines: one renderer class per line class.

Each module renders the lines of the module of the same name in `tax_calculator.jurisdictions.ca_on.trace`,
registering its renderers with `@english_renderer`; this package imports every one of them.
"""

from __future__ import annotations

from tax_calculator.jurisdictions.ca_on.trace_english import (
    capped_records,
    dependants,
    foreign_tax,
    placement_credit,
)

__all__ = ["capped_records", "dependants", "foreign_tax", "placement_credit"]
