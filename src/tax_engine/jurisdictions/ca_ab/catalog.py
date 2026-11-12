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

AB428_ALBERTA_TAX_LINE_75 = AmountKind.declare(
    CATALOG, "ab428_alberta_tax_line_75", non_negative=True
)
"""Alberta tax, AB428 line 75 "Line 75: Line 73 minus line 74 (if negative, enter "0") Enter this
amount on line 42800 of your return. Alberta tax =": line 73 minus line 74, not below 0, entered on
T1 line 42800."""
