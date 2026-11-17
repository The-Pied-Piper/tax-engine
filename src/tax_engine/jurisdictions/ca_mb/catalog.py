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

MB428_MANITOBA_TAX_LINE_82 = AmountKind.declare(
    CATALOG, "mb428_manitoba_tax_line_82", non_negative=True
)
"""Manitoba tax, MB428 line 82 "Enter this amount on line 42800 of your return.": the Manitoba
tax, entered on T1 line 42800."""
