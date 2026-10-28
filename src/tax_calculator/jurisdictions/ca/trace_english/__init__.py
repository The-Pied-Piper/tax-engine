"""English text for the federal Canada trace lines: one renderer class per line class.

Each module renders the lines of the module of the same name in `tax_calculator.jurisdictions.ca.trace`,
registering its renderers with `@english_renderer`; this package imports every one of them.
"""

from __future__ import annotations

from tax_calculator.jurisdictions.ca.trace_english import (
    apprenticeship,
    capital_cost,
    dependants,
    farm_chart,
    foreign_tax,
    gains,
    home_renovation,
    logging_tax_credit,
    rentals,
    vehicles,
)

__all__ = [
    "apprenticeship",
    "capital_cost",
    "dependants",
    "farm_chart",
    "foreign_tax",
    "gains",
    "home_renovation",
    "logging_tax_credit",
    "rentals",
    "vehicles",
]
