"""The New Brunswick artifact catalog: New Brunswick's own kinds, named from its forms.

Amounts are `Decimal`, non-negative unless the form prints no floor. Federal kinds come from
`tax_engine.jurisdictions.ca.catalog`; identifiers are stable.
"""

from __future__ import annotations

from tax_engine.domain.artifact import ArtifactCatalog
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.registry import Namespace
from tax_engine.jurisdictions.ca_nb import NAMESPACE

CATALOG = ArtifactCatalog(Namespace(NAMESPACE))

BASIC_PERSONAL_AMOUNT = AmountKind.declare(CATALOG, "basic_personal_amount", non_negative=True)
"""Basic personal amount, NB428 line 9 and line 58040 "Basic personal amount Claim $13,396": the
amount claimed, one of the credit amounts that the New Brunswick credits subtotal is built from."""

NB428_CREDITS_SUBTOTAL_LINE_18 = AmountKind.declare(
    CATALOG, "nb428_credits_subtotal_line_18", non_negative=True
)
"""New Brunswick credits subtotal, NB428 line 18 "Add lines 9, 10, 13, 16, and 17.": the sum of the
personal amounts claimed, here the basic personal amount alone."""
