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

WORKSHEET_AB428_SUPPLEMENTAL_CREDIT_LINE_9 = AmountKind.declare(
    CATALOG, "worksheet_ab428_supplemental_credit_line_9", non_negative=True
)
"""Alberta supplemental tax credit, Worksheet AB428 line 9 "Line 9: Line 7 multiplied by the
percentage from line 8 enter this amount on line 61545 of your Form AB428.": the credit entered on
line 61545 of Form AB428."""
