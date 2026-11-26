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

NS428_QPP_CONTRIBUTIONS_LINE_22 = AmountKind.declare(
    CATALOG, "ns428_qpp_contributions_line_22", non_negative=True
)
"""Quebec Pension Plan contributions, NS428 line 22 "Amount from line 31000 of your return": a
record total of the T1's export (`ca/self_employment_cpp_qpp_contributions_line_31000`), 0 for a
salary-only caller."""

NS428_EI_PREMIUMS_LINE_23 = AmountKind.declare(
    CATALOG, "ns428_ei_premiums_line_23", non_negative=True
)
"""EI premiums credit amount, NS428 line 23 (line 58300) "Amount from line 31200 of your return": a
copy of T2204 line 16, the EI premiums credit amount."""

NS428_EI_PREMIUMS_LINE_24 = AmountKind.declare(
    CATALOG, "ns428_ei_premiums_line_24", non_negative=True
)
"""Employment insurance premiums, NS428 line 24 "Amount from line 31217 of your return": a record
total of the T1's export (`ca/ei_premiums_on_self_employment_line_31217`), 0 for a salary-only
caller."""

NS428_CPP_EI_AND_OTHER_LINE_25 = AmountKind.declare(
    CATALOG, "ns428_cpp_ei_and_other_line_25", non_negative=True
)
"""CPP or QPP, EI and other credit amounts, NS428 line 25 "Add lines 21 to 24.": the sum of the CPP
or QPP contributions, the QPP contributions and the EI premiums on lines 21 to 24."""

NS428_CREDITS_SUBTOTAL_LINE_26 = AmountKind.declare(
    CATALOG, "ns428_credits_subtotal_line_26", non_negative=True
)
"""Nova Scotia credits subtotal, NS428 line 26 "Line 20 plus line 25": line 20, a copy of line 19,
plus line 25, read by the next line of the credits."""
