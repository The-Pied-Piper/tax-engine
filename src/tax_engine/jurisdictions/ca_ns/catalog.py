"""The Nova Scotia artifact catalog: Nova Scotia's own kinds, named
from the Nova Scotia forms.

Amounts are `Decimal`, non-negative unless the form prints no floor. Federal kinds come from
`tax_engine.jurisdictions.ca.catalog`; identifiers are stable.
"""

from __future__ import annotations

from tax_engine.domain.artifact import ArtifactCatalog
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.registry import Namespace
from tax_engine.jurisdictions.ca_ns import NAMESPACE

CATALOG = ArtifactCatalog(Namespace(NAMESPACE))

NS428_TAXABLE_INCOME_LINE_1 = AmountKind.declare(
    CATALOG, "ns428_taxable_income_line_1", non_negative=True
)
"""Taxable income, Form NS428 Line 1 "Enter your taxable income from line 26000 of your return": the
T1 taxable income, read directly by lines 3 and 4."""

NS428_TAX_ON_TAXABLE_INCOME_LINE_8 = AmountKind.declare(
    CATALOG, "ns428_tax_on_taxable_income_line_8", non_negative=True
)
"""Nova Scotia tax on taxable income, NS428 line 8 "Line 6 plus line 7 Nova Scotia tax on taxable
income =": line 6 plus line 7, copied to line 53 and read by the tax after credits."""

NS428_BRACKET_LOWER_BOUND_LINE_3 = AmountKind.declare(
    CATALOG, "ns428_bracket_lower_bound_line_3", non_negative=True
)
"""Lower bound of the column, Form NS428 line 3 "Column 1: Line 1 is $30,507 or less / Line 3: 0.00"
(30,507.00; 61,015.00; 95,883.00; 154,650.00): the printed lower bound of the column of lines 2 to
8 that line 1 falls in."""

NS428_TAXABLE_INCOME_OVER_LOWER_BOUND_LINE_4 = AmountKind.declare(
    CATALOG, "ns428_taxable_income_over_lower_bound_line_4", non_negative=True
)
"""Taxable income over the lower bound, NS428 line 4 "Line 4: Line 2 minus line 3 (cannot be
negative) =": line 1 minus line 3, not below zero."""

NS428_BRACKET_RATE_LINE_5 = AmountKind.declare(
    CATALOG, "ns428_bracket_rate_line_5", non_negative=True
)
"""Rate of the column, Form NS428 line 5 "Column 1: Line 1 is $30,507 or less / Line 5: Rate 8.79%"
(14.95%; 16.67%; 17.5%; 21%): the printed rate of the column of lines 2 to 8 that line 1 falls
in."""

NS428_TAX_ON_EXCESS_LINE_6 = AmountKind.declare(
    CATALOG, "ns428_tax_on_excess_line_6", non_negative=True
)
"""Tax on the excess, NS428 line 6 "Line 6: Line 4 multiplied by the percentage from line 5 =":
line 4 times the rate of line 5, rounded to the cent."""

NS428_BRACKET_TAX_AT_START_LINE_7 = AmountKind.declare(
    CATALOG, "ns428_bracket_tax_at_start_line_7", non_negative=True
)
"""Tax at the start of the column of lines 2 to 8 (the engine's description; the form prints no
title for line 7), Form NS428 line 7 "Column 1: Line 1 is $30,507 or less / Line 7: 0.00"
(2,681.57; 7,242.51; 13,055.01; 23,339.23): the figure printed on line 7 of the column that line 1
falls in."""
