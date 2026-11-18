"""The Saskatchewan artifact catalog: Saskatchewan's own kinds, named from the Saskatchewan forms.

Amounts are `Decimal`, non-negative unless the form prints no floor. Federal kinds come from
`tax_engine.jurisdictions.ca.catalog`; identifiers are stable.
"""

from __future__ import annotations

from tax_engine.domain.artifact import ArtifactCatalog
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.registry import Namespace
from tax_engine.jurisdictions.ca_sk import NAMESPACE

CATALOG = ArtifactCatalog(Namespace(NAMESPACE))

SK428_TAX_ON_TAXABLE_INCOME_LINE_8 = AmountKind.declare(
    CATALOG, "sk428_tax_on_taxable_income_line_8", non_negative=True
)
"""Saskatchewan tax on taxable income, SK428 line 8 "Line 6 plus line 7 Saskatchewan tax on taxable
income =": line 6 plus line 7, read by line 58 on the tax form."""

SK428_EI_PREMIUMS_LINE_24 = AmountKind.declare(
    CATALOG, "sk428_ei_premiums_line_24", non_negative=True
)
"""EI premiums credit amount, SK428 line 24 (line 58300) "Amount from line 31200 of your return": a
copy of T2204 line 16, the EI premiums credit amount."""

SK428_NON_REFUNDABLE_CREDITS_LINE_57 = AmountKind.declare(
    CATALOG, "sk428_non_refundable_credits_line_57", non_negative=True
)
"""Saskatchewan non-refundable tax credits, SK428 line 57 "Line 57 and line 61500: Line 53 plus line
56 Enter this amount on line 63. Saskatchewan non-refundable tax credits =": line 53 plus line 56,
read by line 63 on the tax form."""

SK428_SASKATCHEWAN_TAX_LINE_82 = AmountKind.declare(
    CATALOG, "sk428_saskatchewan_tax_line_82", non_negative=True
)
"""Saskatchewan tax, SK428 line 82 "Enter this amount on line 42800 of your return.": the
Saskatchewan tax, entered on T1 line 42800."""

BASIC_PERSONAL_AMOUNT = AmountKind.declare(CATALOG, "basic_personal_amount", non_negative=True)
"""Basic personal amount, SK428 line 9 and line 58040 "Basic personal amount Claim $19,491": the
amount claimed, one of the credit amounts that the Saskatchewan non-refundable credits total is
built from."""
