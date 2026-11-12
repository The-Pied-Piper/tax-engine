"""The Alberta artifact catalog: Alberta's own kinds, named from the Alberta forms.

Amounts are `Decimal`, non-negative unless the form prints no floor. Federal kinds come from
`tax_engine.jurisdictions.ca.catalog`; identifiers are stable.
"""

from __future__ import annotations

from tax_engine.domain.artifact import ArtifactCatalog
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.registry import Namespace
from tax_engine.jurisdictions.ca_ab import NAMESPACE

CATALOG = ArtifactCatalog(Namespace(NAMESPACE))

AB428_TAX_ON_TAXABLE_INCOME_LINE_8 = AmountKind.declare(
    CATALOG, "ab428_tax_on_taxable_income_line_8", non_negative=True
)
"""Alberta tax on taxable income, AB428 line 8 "Line 6 plus line 7 Alberta tax on taxable income =":
line 6 plus line 7, the tax of the first column, read by line 59 on the tax form."""

AB428_TAX_ON_TAXABLE_INCOME_LINE_15 = AmountKind.declare(
    CATALOG, "ab428_tax_on_taxable_income_line_15", non_negative=True
)
"""Alberta tax on taxable income, AB428 line 15 "Line 13 plus line 14 Alberta tax on taxable income
=": line 13 plus line 14, the tax of the second column, read by line 59 on the tax form."""

AB428_UNUSED_TUITION_LINE_41 = AmountKind.declare(
    CATALOG, "ab428_unused_tuition_line_41", non_negative=True
)
"""Unused tuition and education amounts, AB428 line 41 (line 58560) "Your unused tuition and
education amounts": the unused tuition and education amounts from Schedule AB(S11), read by line 2
of Worksheet AB428."""

AB428_CREDITS_TOTAL_LINE_52 = AmountKind.declare(
    CATALOG, "ab428_credits_total_line_52", non_negative=True
)
"""Total of the credit amounts, AB428 line 52 (line 58800) "Line 43 plus line 51 =": line 43 plus
line 51, read by line 1 of Worksheet AB428."""

AB428_NON_REFUNDABLE_CREDITS_LINE_58 = AmountKind.declare(
    CATALOG, "ab428_non_refundable_credits_line_58", non_negative=True
)
"""Alberta non-refundable tax credits, AB428 line 58 (line 61500) "Line 54 plus line 57 Enter this
amount on line 62. Alberta non-refundable tax credits =": line 54 plus line 57, read by line 62 on
the tax form."""
