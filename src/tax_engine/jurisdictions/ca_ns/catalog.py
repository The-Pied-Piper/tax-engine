"""The Nova Scotia artifact catalog: Nova Scotia's own kinds, named
from the Nova Scotia forms.

Amounts are `Decimal`, non-negative unless the form prints no floor. Federal kinds come from
`tax_engine.jurisdictions.ca.catalog`; identifiers are stable.
"""

from __future__ import annotations

from tax_engine.domain.artifact import ArtifactCatalog
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.registry import Namespace
from tax_engine.jurisdictions.ca_ns import NAMESPACE

CATALOG = ArtifactCatalog(Namespace(NAMESPACE))

BASIC_PERSONAL_AMOUNT = AmountKind.declare(CATALOG, "basic_personal_amount", non_negative=True)
"""Basic personal amount, NS428 line 9 "Line 9 and line 58040: Basic personal amount Claim
$11,744": the printed $11,744, claimed whole and not income-tested."""

NS428_CREDITS_SUBTOTAL_LINE_19 = AmountKind.declare(
    CATALOG, "ns428_credits_subtotal_line_19", non_negative=True
)
"""Nova Scotia credits subtotal, NS428 line 19 "Add lines 9 to 18.": the sum of the personal amounts
claimed, here the basic personal amount alone."""

NS428_CPP_CONTRIBUTIONS_LINE_21 = AmountKind.declare(
    CATALOG, "ns428_cpp_contributions_line_21", non_negative=True
)
"""CPP or QPP contributions, NS428 line 21 and line 58240 "Amount from line 30800 of your return": a
copy of Schedule 8 line 25, the CPP base contributions on the return."""
