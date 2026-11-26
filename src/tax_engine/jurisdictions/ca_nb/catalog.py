"""The New Brunswick artifact catalog: New Brunswick's own kinds, named from its forms.

Amounts are `Decimal`, non-negative unless the form prints no floor. Federal kinds come from
`tax_engine.jurisdictions.ca.catalog`; identifiers are stable.
"""

from __future__ import annotations

from tax_engine.domain.artifact import ArtifactCatalog
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.registry import Namespace
from tax_engine.jurisdictions.ca_nb import NAMESPACE

CATALOG = ArtifactCatalog(Namespace(NAMESPACE))

NB428_TAXABLE_INCOME_LINE_1 = AmountKind.declare(
    CATALOG, "nb428_taxable_income_line_1", non_negative=True
)
"""Taxable income, Form NB428 Line 1 "Enter your taxable income from line 26000 of your return": the
T1 taxable income, read directly by lines 3, 4, 5 and 7."""

NB428_BRACKET_LOWER_BOUND_LINE_3 = AmountKind.declare(
    CATALOG, "nb428_bracket_lower_bound_line_3", non_negative=True
)
"""Lower bound of the column, Form NB428 line 3 "Column 1: Line 1 is $51,306 or less / Line 3: 0.00"
(51,306.00; 102,614.00; 190,060.00): the printed lower bound of the column of lines 2 to 8 that
line 1 falls in."""

NB428_TAXABLE_INCOME_OVER_LOWER_BOUND_LINE_4 = AmountKind.declare(
    CATALOG, "nb428_taxable_income_over_lower_bound_line_4", non_negative=True
)
"""Taxable income over the lower bound, NB428 line 4 "Line 4: Line 2 minus line 3 (cannot be
negative) =": line 1 minus line 3, not below zero."""

NB428_BRACKET_RATE_LINE_5 = AmountKind.declare(
    CATALOG, "nb428_bracket_rate_line_5", non_negative=True
)
"""Rate of the column, Form NB428 line 5 "Column 1: Line 1 is $51,306 or less / Line 5: Rate 9.4%"
(14%; 16%; 19.5%): the printed rate of the column of lines 2 to 8 that line 1 falls in."""

NB428_TAX_ON_EXCESS_LINE_6 = AmountKind.declare(
    CATALOG, "nb428_tax_on_excess_line_6", non_negative=True
)
"""Tax on the excess, NB428 line 6 "Line 6: Line 4 multiplied by the percentage from line 5 =":
line 4 times the rate of line 5, rounded to the cent."""
