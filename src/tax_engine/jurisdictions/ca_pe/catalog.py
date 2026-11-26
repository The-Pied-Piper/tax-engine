"""The Prince Edward Island artifact catalog: Prince Edward Island's own kinds, named from the
Prince Edward Island forms.

Amounts are `Decimal`, non-negative unless the form prints no floor. Federal kinds come from
`tax_engine.jurisdictions.ca.catalog`; identifiers are stable.
"""

from __future__ import annotations

from tax_engine.domain.artifact import ArtifactCatalog
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.registry import Namespace
from tax_engine.jurisdictions.ca_pe import NAMESPACE

CATALOG = ArtifactCatalog(Namespace(NAMESPACE))

PE428_TAXABLE_INCOME_LINE_1 = AmountKind.declare(
    CATALOG, "pe428_taxable_income_line_1", non_negative=True
)
"""Taxable income, Form PE428 Line 1 "Enter your taxable income from line 26000 of your return": the
T1 taxable income, read directly by lines 3, 4, 5 and 7."""

PE428_BRACKET_LOWER_BOUND_LINE_3 = AmountKind.declare(
    CATALOG, "pe428_bracket_lower_bound_line_3", non_negative=True
)
"""Lower bound of the column, Form PE428 line 3 "Column 1: Line 1 is $33,328.00 or less / Line 3:
0.00" (33,328.00; 64,656.00; 105,000.00; 140,000.00): the printed lower bound of the column of
lines 2 to 8 that line 1 falls in."""
