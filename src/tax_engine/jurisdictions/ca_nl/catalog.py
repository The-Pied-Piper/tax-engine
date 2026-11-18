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

NL428_NEWFOUNDLAND_AND_LABRADOR_TAX_LINE_105 = AmountKind.declare(
    CATALOG, "nl428_newfoundland_and_labrador_tax_line_105", non_negative=True
)
"""Newfoundland and Labrador tax, NL428 line 105 "Line 105: Line 94 minus line 104 (if negative,
enter "0") Enter this amount on line 42800 of your return.": line 94 less line 104, not below 0,
entered on T1 line 42800."""
