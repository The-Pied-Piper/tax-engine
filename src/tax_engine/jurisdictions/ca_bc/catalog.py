"""The British Columbia artifact catalog: British Columbia's own kinds, named from the British
Columbia forms.

Amounts are `Decimal`, non-negative unless the form prints no floor. Federal kinds come from
`tax_engine.jurisdictions.ca.catalog`; identifiers are stable.
"""

from __future__ import annotations

from tax_engine.domain.artifact import ArtifactCatalog
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.registry import Namespace
from tax_engine.jurisdictions.ca_bc import NAMESPACE

CATALOG = ArtifactCatalog(Namespace(NAMESPACE))

BC428_BRITISH_COLUMBIA_TAX_LINE_91 = AmountKind.declare(
    CATALOG, "bc428_british_columbia_tax_line_91", non_negative=True
)
"""British Columbia tax, BC428 line 91 "Enter this amount on line 42800 of your return.": the
British Columbia tax, entered on T1 line 42800."""

BC428_PENSION_INCOME_AMOUNT = AmountKind.declare(
    CATALOG, "bc428_pension_income_amount", non_negative=True
)
"""Pension income amount, BC428 line 36 "Line 36 and line 58360: Pension income amount (maximum
$1,000)": the amount the filer claims, a caller input that is read as blank when left out."""
