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
