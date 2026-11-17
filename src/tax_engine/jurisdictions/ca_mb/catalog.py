"""The Manitoba artifact catalog: Manitoba's own kinds, named from the Manitoba forms.

Amounts are `Decimal`, non-negative unless the form prints no floor. Federal kinds come from
`tax_engine.jurisdictions.ca.catalog`; identifiers are stable.
"""

from __future__ import annotations

from tax_engine.domain.artifact import ArtifactCatalog
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.registry import Namespace
from tax_engine.jurisdictions.ca_mb import NAMESPACE

CATALOG = ArtifactCatalog(Namespace(NAMESPACE))

MB428_TAX_ON_TAXABLE_INCOME_LINE_8 = AmountKind.declare(
    CATALOG, "mb428_tax_on_taxable_income_line_8", non_negative=True
)
"""Manitoba tax on taxable income, MB428 line 8 "Line 6 plus line 7 Manitoba tax on taxable income
=": line 6 plus line 7 of the column that line 1 falls in, read by line 58 on the tax form."""

MB428_NON_REFUNDABLE_CREDITS_LINE_57 = AmountKind.declare(
    CATALOG, "mb428_non_refundable_credits_line_57", non_negative=True
)
"""Manitoba non-refundable tax credits, MB428 line 57 "Line 57 and line 61500: Line 53 plus line 56
Enter this amount on line 61. Manitoba non-refundable tax credits =": line 53 plus line 56, read by
line 61 on the tax form."""

MB428_MANITOBA_TAX_LINE_82 = AmountKind.declare(
    CATALOG, "mb428_manitoba_tax_line_82", non_negative=True
)
"""Manitoba tax, MB428 line 82 "Enter this amount on line 42800 of your return.": the Manitoba
tax, entered on T1 line 42800."""
