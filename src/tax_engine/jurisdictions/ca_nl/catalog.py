"""The Newfoundland and Labrador artifact catalog: Newfoundland and Labrador's own kinds, named
from the Newfoundland and Labrador forms.

Amounts are `Decimal`, non-negative unless the form prints no floor. Federal kinds come from
`tax_engine.jurisdictions.ca.catalog`; identifiers are stable.
"""

from __future__ import annotations

from tax_engine.domain.artifact import ArtifactCatalog
from tax_engine.domain.kinds import AmountKind, CountKind
from tax_engine.domain.registry import Namespace
from tax_engine.jurisdictions.ca_nl import NAMESPACE

CATALOG = ArtifactCatalog(Namespace(NAMESPACE))

WORKSHEET_NL428_AGE_AMOUNT_NET_INCOME_LINE_2 = AmountKind.declare(
    CATALOG, "worksheet_nl428_age_amount_net_income_line_2", non_negative=True
)
"""Net income, Worksheet NL428 line 2 "Line 2: Amount from line 23600 of your return": the net
income of the return."""

WORKSHEET_NL428_AGE_AMOUNT_INCOME_THRESHOLD_LINE_3 = AmountKind.declare(
    CATALOG, "worksheet_nl428_age_amount_income_threshold_line_3", non_negative=True
)
"""Income threshold, Worksheet NL428 line 3 "Line 3: Income threshold 38,712.00": the printed
threshold."""

WORKSHEET_NL428_AGE_AMOUNT_LINE_4 = AmountKind.declare(
    CATALOG, "worksheet_nl428_age_amount_line_4", non_negative=True
)
"""Line 2 minus line 3, Worksheet NL428 line 4 "Line 4: Line 2 minus line 3 (if negative, enter "0")
": the net income above the threshold, not below 0."""

WORKSHEET_NL428_AGE_AMOUNT_LINE_7 = AmountKind.declare(
    CATALOG, "worksheet_nl428_age_amount_line_7", non_negative=True
)
"""Age amount, Worksheet NL428 line 7 "Line 7: Line 1 minus line 6 (if negative, enter "0") Enter
this amount on line 58080 of your Form NL428.": the amount entered on line 58080 of Form NL428."""

NL428_BRACKET_RATE_LINE_5 = AmountKind.declare(
    CATALOG, "nl428_bracket_rate_line_5", non_negative=True
)
"""Bracket column rate, NL428 line 5 (each column prints "Line 5: Rate" with 8.7%, 14.5%, 15.8% or
17.8%): the printed rate of the column that line 1 falls in, blank when line 1 is outside the
table."""

NL428_TAX_ON_TAXABLE_INCOME_LINE_8 = AmountKind.declare(
    CATALOG, "nl428_tax_on_taxable_income_line_8", non_negative=True
)
"""Newfoundland and Labrador tax on taxable income, NL428 line 8 "Line 6 plus line 7 Newfoundland
and Labrador tax on taxable income =": line 6 plus line 7 of the column that line 1 falls in, read
by line 63 on the tax form."""

NL428_BRACKET_RATE_LINE_12 = AmountKind.declare(
    CATALOG, "nl428_bracket_rate_line_12", non_negative=True
)
"""Bracket column rate, NL428 line 12 (each column prints "Line 12: Rate" with 19.8%, 20.8%, 21.3%
or 21.8%): the printed rate of the column that line 1 falls in, blank when line 1 is outside the
table."""

NL428_TAX_ON_TAXABLE_INCOME_LINE_15 = AmountKind.declare(
    CATALOG, "nl428_tax_on_taxable_income_line_15", non_negative=True
)
"""Newfoundland and Labrador tax on taxable income, NL428 line 15 "Line 13 plus line 14
Newfoundland and Labrador tax on taxable income =": line 13 plus line 14 of the column that line 1
falls in, read by line 63 on the tax form."""

NL428_SPOUSE_NET_INCOME_LINE_19 = AmountKind.declare(
    CATALOG, "nl428_spouse_net_income_line_19", non_negative=False
)
"""Spouse or common-law partner's net income, NL428 line 19 "Line 19: Your spouse's or common-law
partner's net income from line 23600 of their return": the amount as the filer gives it, an
optional input. It is signed because a spouse's net income can be a loss, and the form prints no
floor; a blank input is read as blank."""

NL428_ELIGIBLE_DEPENDANT_NET_INCOME_LINE_22 = AmountKind.declare(
    CATALOG, "nl428_eligible_dependant_net_income_line_22", non_negative=False
)
"""Eligible dependant's net income, NL428 line 22 "Line 22: Your eligible dependant's net income
from line 23600 of their return": the amount as the filer gives it, an optional input. It is signed
because a dependant's net income can be a loss, and the form prints no floor; a blank input is read
as blank."""

NL428_INFIRM_DEPENDANTS_AMOUNT_LINE_24 = AmountKind.declare(
    CATALOG, "nl428_infirm_dependants_amount_line_24", non_negative=True
)
"""Amount for infirm dependants age 18 or older, NL428 line 24 "Line 24 and line 58200: Amount for
infirm dependants age 18 or older (use Worksheet NL428)": the amount as the filer gives it, an
optional input; a blank input is read as blank."""

NL428_NON_REFUNDABLE_CREDITS_LINE_62 = AmountKind.declare(
    CATALOG, "nl428_non_refundable_credits_line_62", non_negative=True
)
"""Newfoundland and Labrador non-refundable tax credits, NL428 line 62 "Line 62 and line 61500:
Line 58 plus line 61 Enter this amount on line 66.": line 58 plus line 61, read by line 66 on the
tax form."""

NL428_NEWFOUNDLAND_AND_LABRADOR_TAX_LINE_105 = AmountKind.declare(
    CATALOG, "nl428_newfoundland_and_labrador_tax_line_105", non_negative=True
)
"""Newfoundland and Labrador tax, NL428 line 105 "Line 105: Line 94 minus line 104 (if negative,
enter "0") Enter this amount on line 42800 of your return.": line 94 less line 104, not below 0,
entered on T1 line 42800."""

NL428_DISABILITY_AMOUNT_SELF_CLAIMED_LINE_40 = CountKind.declare(
    CATALOG, "nl428_disability_amount_self_claimed_line_40", non_negative=True
)
"""Disability amount for self claimed, NL428 line 40 "Line 40 and line 58440: Disability amount for
self (claim $7,467 or, if you were under 18 years of age, use Worksheet NL428)": the eligibility
claim, 1 when the disability tax credit is approved and the amount is claimed, read as blank when
left out."""

NL428_DISABILITY_AMOUNT_SELF_CLAIMED_CHECKED_LINE_40 = CountKind.declare(
    CATALOG, "nl428_disability_amount_self_claimed_checked_line_40", non_negative=True
)
"""Disability amount for self claim, checked, NL428 line 40 "Line 40 and line 58440: Disability
amount for self (claim $7,467 or, if you were under 18 years of age, use Worksheet NL428)": the
claim with a blank read as 0, refused above 1 so the amount cannot be claimed twice."""

DISABILITY_AMOUNT_SELF = AmountKind.declare(CATALOG, "disability_amount_self", non_negative=True)
"""Disability amount for self, NL428 line 40 "Line 40 and line 58440: Disability amount for self
(claim $7,467 or, if you were under 18 years of age, use Worksheet NL428)": the printed $7,467, the
amount claimed when the disability tax credit is approved."""

NL428_DISABILITY_AMOUNT_SELF_LINE_40 = AmountKind.declare(
    CATALOG, "nl428_disability_amount_self_line_40", non_negative=True
)
"""Disability amount for self, NL428 line 40 "Line 40 and line 58440: Disability amount for self
(claim $7,467 or, if you were under 18 years of age, use Worksheet NL428)": the printed $7,467 when
the claim is 1, 0 when the claim is blank or 0."""

BASIC_PERSONAL_AMOUNT = AmountKind.declare(CATALOG, "basic_personal_amount", non_negative=True)
"""Basic personal amount, NL428 line 16 "Line 16 and line 58040: Basic personal amount Claim
$11,067": the printed $11,067, claimed whole and not income-tested."""
