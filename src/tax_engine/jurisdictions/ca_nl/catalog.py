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

WORKSHEET_NL428_AGE_AMOUNT_MAXIMUM_LINE_1 = AmountKind.declare(
    CATALOG, "worksheet_nl428_age_amount_maximum_line_1", non_negative=True
)
"""Maximum amount, Worksheet NL428 line 1 "Line 1: Maximum amount 7,064.00": the printed
maximum."""

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

WORKSHEET_NL428_AGE_AMOUNT_LINE_6 = AmountKind.declare(
    CATALOG, "worksheet_nl428_age_amount_line_6", non_negative=True
)
"""Line 4 multiplied by the line 5 rate, Worksheet NL428 line 6 "Line 6: Line 4 multiplied by the
percentage from line 5 =": the age amount reduction, 15% of the net income above the threshold."""

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

NL428_QPP_CONTRIBUTIONS_LINE_28 = AmountKind.declare(
    CATALOG, "nl428_qpp_contributions_line_28", non_negative=True
)
"""Quebec Pension Plan contributions, NL428 line 28 "Line 28 and line 58280: Amount from line 31000
of your return": the amount as the filer gives it, an optional input; a blank input is read as
blank."""

NL428_EI_PREMIUMS_LINE_29 = AmountKind.declare(
    CATALOG, "nl428_ei_premiums_line_29", non_negative=True
)
"""EI premiums credit amount, NL428 line 29 (line 58300) "Amount from line 31200 of your return": a
copy of T2204 line 16, the EI premiums credit amount."""

NL428_EI_PREMIUMS_LINE_30 = AmountKind.declare(
    CATALOG, "nl428_ei_premiums_line_30", non_negative=True
)
"""Employment insurance premiums, NL428 line 30 "Line 30 and line 58305: Amount from line 31217
of your return": the amount as the filer gives it, an optional input; a blank input is read as
blank."""

NL428_VOLUNTEER_FIREFIGHTERS_AMOUNT_LINE_31 = AmountKind.declare(
    CATALOG, "nl428_volunteer_firefighters_amount_line_31", non_negative=True
)
"""Volunteer firefighters' amount, NL428 line 31 "Line 31 and line 58315: Volunteer firefighters'
amount": the amount as the filer gives it, an optional input; a blank input is read as blank."""

NL428_SEARCH_AND_RESCUE_VOLUNTEERS_AMOUNT_LINE_32 = AmountKind.declare(
    CATALOG, "nl428_search_and_rescue_volunteers_amount_line_32", non_negative=True
)
"""Search and rescue volunteers' amount, NL428 line 32 "Line 32 and line 58316: Search and rescue
volunteers' amount": the amount as the filer gives it, an optional input; a blank input is read as
blank."""

NL428_CHILD_CARE_AMOUNT_LINE_33 = AmountKind.declare(
    CATALOG, "nl428_child_care_amount_line_33", non_negative=True
)
"""Child care amount, NL428 line 33 "Line 33 and line 58320: Child care amount": the amount as
the filer gives it, an optional input; a blank input is read as blank."""

NL428_ADOPTION_EXPENSES_LINE_34 = AmountKind.declare(
    CATALOG, "nl428_adoption_expenses_line_34", non_negative=True
)
"""Adoption expenses, NL428 line 34 "Line 34 and line 58330: Adoption expenses": the amount as the
filer gives it, an optional input; a blank input is read as blank."""

NL428_CPP_EI_AND_OTHER_LINE_35 = AmountKind.declare(
    CATALOG, "nl428_cpp_ei_and_other_line_35", non_negative=True
)
"""CPP, EI and other credit amounts subtotal, NL428 line 35 "Line 35: Add lines 27 to 34. = ^": the
sum of lines 27 to 34, lines 28, 30, 31, 32, 33 and 34 being optional inputs read as 0.
"""

NL428_CAREGIVER_AMOUNT_LINE_38 = AmountKind.declare(
    CATALOG, "nl428_caregiver_amount_line_38", non_negative=True
)
"""Caregiver amount, NL428 line 38 "Line 38 and line 58400: Caregiver amount (use Worksheet NL428)":
the amount as the filer gives it, an optional input; a blank input is read as blank."""

NL428_PENSION_INCOME_AMOUNT_CLAIMED_LINE_37 = AmountKind.declare(
    CATALOG, "nl428_pension_income_amount_claimed_line_37", non_negative=True
)
"""Pension income amount claimed, NL428 line 37 "Line 37 and line 58360: Pension income amount
(maximum $1,000)": the amount as the filer gives it, an optional input; a blank input is read as
blank, and the line 37 step checks it against the printed maximum."""

NL428_PENSION_INCOME_AMOUNT_MAXIMUM = AmountKind.declare(
    CATALOG, "nl428_pension_income_amount_maximum", non_negative=True
)
"""Pension income amount maximum, printed on NL428 line 37 "(maximum $1,000)": the printed maximum,
from the `ca-nl/pension_income_amount_maximum` dataset; the bound line 37 cannot pass."""

NL428_PENSION_INCOME_AMOUNT_LINE_37 = AmountKind.declare(
    CATALOG, "nl428_pension_income_amount_line_37", non_negative=True
)
"""Pension income amount, NL428 line 37 "Line 37 and line 58360: Pension income amount (maximum
$1,000)": the entered amount, passed on unchanged when it is at most the printed maximum, blank when
left out; above the maximum it is refused, not capped."""

NL428_DISABILITY_AMOUNT_TRANSFERRED_FROM_A_DEPENDANT_LINE_41 = AmountKind.declare(
    CATALOG, "nl428_disability_amount_transferred_from_a_dependant_line_41", non_negative=True
)
"""Disability amount transferred from a dependant, NL428 line 41 "Line 41 and line 58480: Disability
amount transferred from a dependant (use Worksheet NL428)": the amount as the filer gives it, an
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

NL428_CPP_CONTRIBUTIONS_LINE_27 = AmountKind.declare(
    CATALOG, "nl428_cpp_contributions_line_27", non_negative=True
)
"""CPP or QPP contributions, NL428 line 27 and line 58240 "Amount from line 30800 of your return": a
copy of Schedule 8 line 25, the CPP base contributions on the return."""

BASIC_PERSONAL_AMOUNT = AmountKind.declare(CATALOG, "basic_personal_amount", non_negative=True)
"""Basic personal amount, NL428 line 16 "Line 16 and line 58040: Basic personal amount Claim
$11,067": the printed $11,067, claimed whole and not income-tested."""

SPOUSE_AMOUNT_BASE = AmountKind.declare(CATALOG, "spouse_amount_base", non_negative=True)
"""Spouse or common-law partner amount, base amount, NL428 line 18 "Base amount 9,948.00": the
printed figure, from which line 20 takes line 19."""

SPOUSE_AMOUNT_MAXIMUM = AmountKind.declare(CATALOG, "spouse_amount_maximum", non_negative=True)
"""Spouse or common-law partner amount, maximum, NL428 line 20 "(maximum $9,043)": the printed
figure, the most line 20 can be."""

NL428_SPOUSE_AMOUNT_BEFORE_MAXIMUM_LINE_20 = AmountKind.declare(
    CATALOG, "nl428_spouse_amount_before_maximum_line_20", non_negative=True
)
"""Spouse or common-law partner amount before the maximum, NL428 line 20 "Line 20 and line 58120:
Line 18 minus line 19 (if negative, enter "0") (maximum $9,043) =": line 18 less line 19, not below
0, before the maximum is applied."""

NL428_SPOUSE_AMOUNT_LINE_20 = AmountKind.declare(
    CATALOG, "nl428_spouse_amount_line_20", non_negative=True
)
"""Spouse or common-law partner amount, NL428 line 20 "Line 20 and line 58120: Line 18 minus line 19
(if negative, enter "0") (maximum $9,043) =": line 18 less line 19, not below 0, at most the printed
maximum."""

ELIGIBLE_DEPENDANT_AMOUNT_BASE = AmountKind.declare(
    CATALOG, "eligible_dependant_amount_base", non_negative=True
)
"""Amount for an eligible dependant, base amount, NL428 line 21 "Base amount 9,948.00": the printed
figure, from which line 23 takes line 22."""

ELIGIBLE_DEPENDANT_AMOUNT_MAXIMUM = AmountKind.declare(
    CATALOG, "eligible_dependant_amount_maximum", non_negative=True
)
"""Amount for an eligible dependant, maximum, NL428 line 23 "(maximum $9,043)": the printed figure,
the most line 23 can be."""

NL428_ELIGIBLE_DEPENDANT_AMOUNT_BEFORE_MAXIMUM_LINE_23 = AmountKind.declare(
    CATALOG, "nl428_eligible_dependant_amount_before_maximum_line_23", non_negative=True
)
"""Amount for an eligible dependant before the maximum, NL428 line 23 "Line 23 and line 58160:
Line 21 minus line 22 (if negative, enter "0") (maximum $9,043) =": line 21 less line 22, not below
0, before the maximum is applied."""

NL428_ELIGIBLE_DEPENDANT_AMOUNT_LINE_23 = AmountKind.declare(
    CATALOG, "nl428_eligible_dependant_amount_line_23", non_negative=True
)
"""Amount for an eligible dependant, NL428 line 23 "Line 23 and line 58160: Line 21 minus line 22
(if negative, enter "0") (maximum $9,043) =": line 21 less line 22, not below 0, at most the printed
maximum."""

NL428_TAXABLE_INCOME_LINE_1 = AmountKind.declare(
    CATALOG, "nl428_taxable_income_line_1", non_negative=True
)
"""Taxable income, Form NL428 Line 1 "Enter your taxable income from line 26000 of your return": the
T1 taxable income, read directly by line 2."""

NL428_NET_INCOME_LINE_49 = AmountKind.declare(
    CATALOG, "nl428_net_income_line_49", non_negative=True
)
"""Net income, NL428 line 49 "Amount from line 23600 of your return": the T1 net income, read by
line 51 before it is multiplied by the line 50 rate."""

NL428_MEDICAL_EXPENSES_RATE_AMOUNT_LINE_51 = AmountKind.declare(
    CATALOG, "nl428_medical_expenses_rate_amount_line_51", non_negative=True
)
"""Net income multiplied by 3%, NL428 line 51 "Line 49 multiplied by the percentage from line 50":
line 49 times the printed line 50 rate, rounded half-up to the cent."""
