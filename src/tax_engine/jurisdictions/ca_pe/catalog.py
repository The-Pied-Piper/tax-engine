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

PE428_TAXABLE_INCOME_OVER_LOWER_BOUND_LINE_4 = AmountKind.declare(
    CATALOG, "pe428_taxable_income_over_lower_bound_line_4", non_negative=True
)
"""Taxable income over the lower bound, PE428 line 4 "Line 4: Line 2 minus line 3 (cannot be
negative)": line 1 minus line 3, not below zero."""

PE428_BRACKET_RATE_LINE_5 = AmountKind.declare(
    CATALOG, "pe428_bracket_rate_line_5", non_negative=True
)
"""Rate of the column, Form PE428 line 5 "Column 1: Line 1 is $33,328.00 or less / Line 5: Rate
9.5%" (13.47%; 16.6%; 17.62%; 19%): the printed rate of the column of lines 2 to 8 that line 1
falls in."""

PE428_TAX_ON_EXCESS_LINE_6 = AmountKind.declare(
    CATALOG, "pe428_tax_on_excess_line_6", non_negative=True
)
"""Tax on the excess, PE428 line 6 "Line 6: Line 4 multiplied by the percentage from line 5": line 4
times the rate of line 5, rounded to the cent."""

PE428_BRACKET_TAX_AT_START_LINE_7 = AmountKind.declare(
    CATALOG, "pe428_bracket_tax_at_start_line_7", non_negative=True
)
"""Tax at the start of the column of lines 2 to 8 (the engine's description; the form prints no
title for line 7), Form PE428 line 7 "Column 1: Line 1 is $33,328.00 or less / Line 7: 0.00"
(3,166.16; 7,386.04; 14,083.15; 20,250.15): the figure printed on line 7 of the column that line 1
falls in."""

PE428_TAX_ON_TAXABLE_INCOME_LINE_8 = AmountKind.declare(
    CATALOG, "pe428_tax_on_taxable_income_line_8", non_negative=True
)
"""Prince Edward Island tax on taxable income, PE428 line 8 "Line 8: Line 6 plus line 7 Prince
Edward Island tax on taxable income": line 6 plus line 7, copied to line 55 and read by the lines
after it."""
