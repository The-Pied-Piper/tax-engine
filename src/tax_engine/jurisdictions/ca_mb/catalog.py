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

MB479_MANITOBA_CREDITS_LINE_81 = AmountKind.declare(
    CATALOG, "mb479_manitoba_credits_line_81", non_negative=True
)
"""Manitoba credits, MB479 line 81 "Add lines 78 to 80. Enter this amount on line 47900 of your
return.": the Manitoba credits, entered on T1 line 47900."""
