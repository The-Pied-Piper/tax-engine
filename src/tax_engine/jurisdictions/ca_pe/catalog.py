"""The Prince Edward Island artifact catalog: Prince Edward Island's own kinds, named from the
Prince Edward Island forms.

Amounts are `Decimal`, non-negative unless the form prints no floor. Federal kinds come from
`tax_engine.jurisdictions.ca.catalog`; identifiers are stable.
"""

from __future__ import annotations

from tax_engine.domain.artifact import ArtifactCatalog
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.registry import Namespace
from tax_engine.jurisdictions.ca_pe import NAMESPACE

CATALOG = ArtifactCatalog(Namespace(NAMESPACE))

BASIC_PERSONAL_AMOUNT = AmountKind.declare(CATALOG, "basic_personal_amount", non_negative=True)
"""Basic personal amount, PE428 line 9 "Line 9 and line 58040: Basic personal amount Claim
$14,650": the printed $14,650, claimed whole and not income-tested."""

PE428_AGE_AMOUNT_LINE_10 = AmountKind.declare(
    CATALOG, "pe428_age_amount_line_10", non_negative=True
)
"""Age amount (if you were born in 1960 or earlier) (use Worksheet PE428) (maximum $6,510), PE428
line 10 "Line 10 and line 58080: Age amount (if you were born in 1960 or earlier) (use Worksheet
PE428) (maximum $6,510)": the amount as the filer gives it, an optional input; a blank input is
read as blank."""

PE428_SPOUSE_OR_COMMON_LAW_PARTNER_AMOUNT_LINE_13 = AmountKind.declare(
    CATALOG, "pe428_spouse_or_common_law_partner_amount_line_13", non_negative=True
)
"""Spouse or common-law partner amount, PE428 line 13 "Line 13 and line 58120: Line 11 minus line
12 (if negative, enter "0") (maximum $12,443)": the amount as the filer gives it, an optional
input; a blank input is read as blank."""

PE428_ELIGIBLE_DEPENDANT_AMOUNT_LINE_16 = AmountKind.declare(
    CATALOG, "pe428_eligible_dependant_amount_line_16", non_negative=True
)
"""Amount for an eligible dependant, PE428 line 16 "Line 16 and line 58160: Line 14 minus line 15
(if negative, enter "0") (maximum $12,443)": the amount as the filer gives it, an optional input;
a blank input is read as blank."""

PE428_INFIRM_DEPENDANTS_AMOUNT_LINE_17 = AmountKind.declare(
    CATALOG, "pe428_infirm_dependants_amount_line_17", non_negative=True
)
"""Amount for infirm dependants age 18 or older (use Worksheet PE428), PE428 line 17 "Line 17 and
line 58200: Amount for infirm dependants age 18 or older (use Worksheet PE428)": the amount as the
filer gives it, an optional input; a blank input is read as blank."""

PE428_YOUNG_CHILDREN_AMOUNT_LINE_18 = AmountKind.declare(
    CATALOG, "pe428_young_children_amount_line_18", non_negative=True
)
"""Amount for young children (complete the chart at the end of page 2), PE428 line 18 "Line 18 and
line 58230: Amount for young children (complete the chart at the end of page 2)": the amount as
the filer gives it, an optional input; a blank input is read as blank."""

PE428_CREDITS_SUBTOTAL_LINE_19 = AmountKind.declare(
    CATALOG, "pe428_credits_subtotal_line_19", non_negative=True
)
"""Prince Edward Island credits subtotal, PE428 line 19 "Line 19: Add lines 9, 10, 13, and 16 to
18. = ^": the sum of the personal amounts claimed, the basic personal amount plus the optional
lines 10, 13, 16, 17 and 18 read as 0 when blank."""

PE428_CPP_CONTRIBUTIONS_LINE_20 = AmountKind.declare(
    CATALOG, "pe428_cpp_contributions_line_20", non_negative=True
)
"""CPP or QPP contributions, PE428 line 20 and line 58240 "Amount from line 30800 of your return":
a copy of Schedule 8 line 25, the CPP base contributions on the return."""

PE428_QPP_CONTRIBUTIONS_LINE_21 = AmountKind.declare(
    CATALOG, "pe428_qpp_contributions_line_21", non_negative=True
)
"""Contributions on self-employment, PE428 line 21 and line 58280 "Amount from line 31000 of your
return": a record total of the T1's export
(`ca/self_employment_cpp_qpp_contributions_line_31000`), 0 for a salary-only caller."""
