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

NB428_CPP_CONTRIBUTIONS_LINE_19 = AmountKind.declare(
    CATALOG, "nb428_cpp_contributions_line_19", non_negative=True
)
"""CPP or QPP contributions, NB428 line 19 and line 58240 "Amount from line 30800 of your return": a
copy of Schedule 8 line 25, the CPP base contributions on the return."""

NB428_EI_PREMIUMS_LINE_21 = AmountKind.declare(
    CATALOG, "nb428_ei_premiums_line_21", non_negative=True
)
"""EI premiums credit amount, NB428 line 21 (line 58300) "Amount from line 31200 of your return": a
copy of T2204 line 16, the EI premiums credit amount."""
