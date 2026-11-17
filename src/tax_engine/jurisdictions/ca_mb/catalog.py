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

MB428_A_FAMILY_TAX_BENEFIT_LINE_12 = AmountKind.declare(
    CATALOG, "mb428_a_family_tax_benefit_line_12", non_negative=True
)
"""Family tax benefit, Schedule MB428-A line 12 "Line 12: Line 10 minus line 11 (if negative, enter
"0") Enter this amount on line 61470 of your Form MB428.": the family tax benefit entered on line
61470 of Form MB428."""
