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

WORKSHEET_MB428_BASIC_PERSONAL_AMOUNT_LINE_9 = AmountKind.declare(
    CATALOG, "worksheet_mb428_basic_personal_amount_line_9", non_negative=True
)
"""Manitoba basic personal amount, Worksheet MB428 line 9 "Line 9: Line 1 minus line 8 (if negative,
enter "0") Enter this amount on line 58040 of your Form MB428.": the basic personal amount entered
on line 58040 of Form MB428."""
