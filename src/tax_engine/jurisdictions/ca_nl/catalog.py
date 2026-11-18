"""The Newfoundland and Labrador artifact catalog: Newfoundland and Labrador's own kinds, named
from the Newfoundland and Labrador forms.

Amounts are `Decimal`, non-negative unless the form prints no floor. Federal kinds come from
`tax_engine.jurisdictions.ca.catalog`; identifiers are stable.
"""

from __future__ import annotations

from tax_engine.domain.artifact import ArtifactCatalog
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.registry import Namespace
from tax_engine.jurisdictions.ca_nl import NAMESPACE

CATALOG = ArtifactCatalog(Namespace(NAMESPACE))

WORKSHEET_NL428_AGE_AMOUNT_LINE_7 = AmountKind.declare(
    CATALOG, "worksheet_nl428_age_amount_line_7", non_negative=True
)
"""Age amount, Worksheet NL428 line 7 "Line 7: Line 1 minus line 6 (if negative, enter "0") Enter
this amount on line 58080 of your Form NL428.": the amount entered on line 58080 of Form NL428."""
