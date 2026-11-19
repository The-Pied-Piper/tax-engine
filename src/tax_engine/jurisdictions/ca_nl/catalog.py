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

WORKSHEET_NL428_DISABILITY_SELF_BASE_AMOUNT_LINE_1 = AmountKind.declare(
    CATALOG, "worksheet_nl428_disability_self_base_amount_line_1", non_negative=True
)
"""Base amount, Worksheet NL428 line 58440 line 1 "Line 1: Base amount 7,467.00": the printed
base amount."""

WORKSHEET_NL428_DISABILITY_SELF_SUPPLEMENT_MAXIMUM_LINE_2 = AmountKind.declare(
    CATALOG, "worksheet_nl428_disability_self_supplement_maximum_line_2", non_negative=True
)
"""Maximum amount, Worksheet NL428 line 58440 line 2 "Line 2: Maximum amount 3,514.00": the printed
maximum."""

WORKSHEET_NL428_DISABILITY_SELF_CARE_THRESHOLD_LINE_4 = AmountKind.declare(
    CATALOG, "worksheet_nl428_disability_self_care_threshold_line_4", non_negative=True
)
"""Threshold for child and attendant care expenses, Worksheet NL428 line 58440 line 4 "Line 4:
Threshold for child and attendant care expenses 2,987.00": the printed threshold."""

WORKSHEET_NL428_DISABILITY_SELF_CARE_OVER_THRESHOLD_LINE_5 = AmountKind.declare(
    CATALOG, "worksheet_nl428_disability_self_care_over_threshold_line_5", non_negative=True
)
"""Care expenses over the threshold, Worksheet NL428 line 58440 line 5 "Line 5: Line 3 minus line 4
(if negative, enter "0")": the child care and attendant care expenses of line 3 above the line 4
threshold."""

WORKSHEET_NL428_DISABILITY_SELF_SUPPLEMENT_LINE_6 = AmountKind.declare(
    CATALOG, "worksheet_nl428_disability_self_supplement_line_6", non_negative=True
)
"""Supplement, Worksheet NL428 line 58440 line 6 "Line 6: Line 2 minus line 5 (if negative, enter
"0")": the maximum of line 2 less the care expenses over the threshold."""

WORKSHEET_NL428_DISABILITY_SELF_LINE_7 = AmountKind.declare(
    CATALOG, "worksheet_nl428_disability_self_line_7", non_negative=True
)
"""Disability amount for self, Worksheet NL428 line 58440 line 7 "Line 7: Line 1 plus line 6 Enter
this amount on line 58440 of your Form NL428. (maximum $10,981)": the amount entered on line 58440
of Form NL428, for a filer under 18 years of age on December 31, 2025."""

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

NL428_CREDITS_SUBTOTAL_LINE_36 = AmountKind.declare(
    CATALOG, "nl428_credits_subtotal_line_36", non_negative=True
)
"""Credits subtotal, NL428 line 36 "Line 36: Line 26 plus line 35 = ^": line 26 (a copy of line 25)
plus line 35."""

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

NL428_CREDITS_SUBTOTAL_LINE_39 = AmountKind.declare(
    CATALOG, "nl428_credits_subtotal_line_39", non_negative=True
)
"""Credits subtotal, NL428 line 39 "Line 39: Add lines 36 to 38. = ^": line 36 plus line 37 (the
pension income amount) plus line 38 (the caregiver amount), lines 37 and 38 being read as 0 when
blank."""

NL428_DISABILITY_AMOUNT_TRANSFERRED_FROM_A_DEPENDANT_LINE_41 = AmountKind.declare(
    CATALOG, "nl428_disability_amount_transferred_from_a_dependant_line_41", non_negative=True
)
"""Disability amount transferred from a dependant, NL428 line 41 "Line 41 and line 58480: Disability
amount transferred from a dependant (use Worksheet NL428)": the amount as the filer gives it, an
optional input; a blank input is read as blank."""

NL428_CREDITS_SUBTOTAL_LINE_42 = AmountKind.declare(
    CATALOG, "nl428_credits_subtotal_line_42", non_negative=True
)
"""Credits subtotal, NL428 line 42 "Line 42: Add lines 39 to 41. = ^": line 39 plus line 40 (the
disability amount for self) plus line 41 (the disability amount transferred from a dependant),
line 41 being read as 0 when blank."""

NL428_STUDENT_LOAN_INTEREST_LINE_43 = AmountKind.declare(
    CATALOG, "nl428_student_loan_interest_line_43", non_negative=True
)
"""Interest paid on your student loans, NL428 line 43 "Line 43 and line 58520: Interest paid on your
student loans (amount from line 31900 of your return)": the amount as the filer gives it, an
optional input; a blank input is read as blank."""

NL428_TUITION_AND_EDUCATION_AMOUNTS_LINE_44 = AmountKind.declare(
    CATALOG, "nl428_tuition_and_education_amounts_line_44", non_negative=True
)
"""Your tuition and education amounts, NL428 line 44 "Line 44 and line 58560: Your tuition and
education amounts (attach Schedule NL(S11))": the amount as the filer gives it, an optional input;
a blank input is read as blank."""

NL428_TUITION_AND_EDUCATION_AMOUNTS_TRANSFERRED_FROM_A_CHILD_OR_GRANDCHILD_LINE_45 = (
    AmountKind.declare(
        CATALOG,
        "nl428_tuition_and_education_amounts_transferred_from_a_child_or_grandchild_line_45",
        non_negative=True,
    )
)
"""Tuition and education amounts transferred from a child or grandchild, NL428 line 45 (line 58600)
"Tuition and education amounts transferred from a child or grandchild": the amount as the filer
gives it, an optional input; a blank input is read as blank."""

NL428_AMOUNTS_TRANSFERRED_FROM_YOUR_SPOUSE_OR_COMMON_LAW_PARTNER_LINE_46 = AmountKind.declare(
    CATALOG,
    "nl428_amounts_transferred_from_your_spouse_or_common_law_partner_line_46",
    non_negative=True,
)
"""Amounts transferred from your spouse or common-law partner, NL428 line 46 "Line 46 and line
58640: Amounts transferred from your spouse or common-law partner (attach Schedule NL(S2))": the
amount as the filer gives it, an optional input; a blank input is read as blank."""

NL428_CREDITS_SUBTOTAL_LINE_47 = AmountKind.declare(
    CATALOG, "nl428_credits_subtotal_line_47", non_negative=True
)
"""Credits subtotal, NL428 line 47 "Line 47: Add lines 42 to 46. = ^": line 42 plus line 43 (the
student loan interest) plus line 44 (the tuition and education amounts) plus line 45 (the tuition
and education amounts transferred from a child or grandchild) plus line 46 (the amounts transferred
from a spouse or common-law partner), lines 43 to 46 being read as 0 when blank."""

NL428_MEDICAL_EXPENSES_LINE_48 = AmountKind.declare(
    CATALOG, "nl428_medical_expenses_line_48", non_negative=True
)
"""Medical expenses, NL428 line 48 (line 58689) "Amount from line 33099 of your return": the amount
as the filer gives it, an optional input; a blank input is read as blank."""

NL428_ALLOWABLE_MEDICAL_EXPENSES_FOR_OTHER_DEPENDANTS_LINE_54 = AmountKind.declare(
    CATALOG, "nl428_allowable_medical_expenses_for_other_dependants_line_54", non_negative=True
)
"""Allowable amount of medical expenses for other dependants, NL428 line 54 "Line 54 and line
58729: Allowable amount of medical expenses for other dependants (use Worksheet NL428)": the amount
as the filer gives it, an optional input; a blank input is read as blank."""

NL428_DONATIONS_AND_GIFTS_CREDIT_LINE_61 = AmountKind.declare(
    CATALOG, "nl428_donations_and_gifts_credit_line_61", non_negative=True
)
"""Donations and gifts credit, NL428 line 61 "Line 61 and line 58969: Line 59 plus line 60 =": the
amount as the filer gives it, an optional input; lines 59 and 60 are not built, and a blank input
is read as blank."""

NL428_NON_REFUNDABLE_CREDITS_LINE_62 = AmountKind.declare(
    CATALOG, "nl428_non_refundable_credits_line_62", non_negative=True
)
"""Newfoundland and Labrador non-refundable tax credits, NL428 line 62 "Line 62 and line 61500:
Line 58 plus line 61 Enter this amount on line 66.": line 58 plus line 61, read by line 66 on the
tax form."""

NL428_NEWFOUNDLAND_AND_LABRADOR_TAX_ON_TAXABLE_INCOME_LINE_63 = AmountKind.declare(
    CATALOG, "nl428_newfoundland_and_labrador_tax_on_taxable_income_line_63", non_negative=True
)
"""Newfoundland and Labrador tax on taxable income, NL428 line 63 "Line 63: Newfoundland and
Labrador tax on taxable income from line 8 or 15 ^": the amount of line 8 or of line 15, whichever
the taxable income is in; the other is blank."""

NL428_TAX_ON_SPLIT_INCOME_LINE_64 = AmountKind.declare(
    CATALOG, "nl428_tax_on_split_income_line_64", non_negative=True
)
"""Newfoundland and Labrador tax on split income, NL428 line 64 "Line 64 and line 61510:
Newfoundland and Labrador tax on split income (complete Form T1206)": the amount as the filer gives
it, an optional input; a blank input is read as blank."""

NL428_TAX_BEFORE_CREDITS_LINE_65 = AmountKind.declare(
    CATALOG, "nl428_tax_before_credits_line_65", non_negative=True
)
"""Newfoundland and Labrador tax before credits, NL428 line 65 "Line 65: Line 63 plus line 64 =":
line 63 plus line 64 (the tax on split income, blank read as 0), rounded half-up to the cent."""

NL428_NON_REFUNDABLE_CREDITS_LINE_66 = AmountKind.declare(
    CATALOG, "nl428_non_refundable_credits_line_66", non_negative=True
)
"""Newfoundland and Labrador non-refundable tax credits, NL428 line 66 "Line 66: Newfoundland and
Labrador non-refundable tax credits from line 62 ^": line 62 of the credits form, read across the
forms."""

NL428_MINIMUM_TAX_CARRYOVER_AMOUNT_LINE_68 = AmountKind.declare(
    CATALOG, "nl428_minimum_tax_carryover_amount_line_68", non_negative=True
)
"""Newfoundland and Labrador minimum tax carryover, NL428 line 68 (line 61540) "Amount from line
40427 of your return": the amount from line 40427 of the T1 return, an optional input, box A of the
line, as the filer gives it; a blank input is read as blank."""

NL428_MINIMUM_TAX_CARRYOVER_LINE_68 = AmountKind.declare(
    CATALOG, "nl428_minimum_tax_carryover_line_68", non_negative=True
)
"""Newfoundland and Labrador minimum tax carryover, NL428 line 68 and line 61540 "Amount from line
40427 of your return multiplied by 60% =": calculated, the amount from line 40427 multiplied by
60%."""

NL428_CREDITS_TOTAL_LINE_69 = AmountKind.declare(
    CATALOG, "nl428_credits_total_line_69", non_negative=True
)
"""Newfoundland and Labrador credits total, NL428 line 69 "Line 69: Add lines 66 to 68. =": line 66
plus line 67 (the dividend tax credit, blank read as 0) plus line 68, rounded half-up to the
cent."""

NL428_PROVINCIAL_FOREIGN_TAX_CREDIT_LINE_73 = AmountKind.declare(
    CATALOG, "nl428_provincial_foreign_tax_credit_line_73", non_negative=True
)
"""Provincial foreign tax credit, NL428 line 73 "Line 73: Provincial foreign tax credit (complete
Form T2036)": the credit from Form T2036, an optional input that a salary-only caller leaves out;
a blank input is read as blank."""

NL428_RESORT_PROPERTY_INVESTMENT_TAX_CREDIT_LINE_80 = AmountKind.declare(
    CATALOG, "nl428_resort_property_investment_tax_credit_line_80", non_negative=True
)
"""Resort property investment tax credit, NL428 line 80 "Line 80: Resort property investment tax
credit (complete Form T1297)": the credit from Form T1297, an optional input that a salary-only
caller leaves out; a blank input is read as blank."""

NL428_POLITICAL_CONTRIBUTION_TAX_CREDIT_CLAIMED_LINE_76 = AmountKind.declare(
    CATALOG, "nl428_political_contribution_tax_credit_claimed_line_76", non_negative=True
)
"""Political contribution tax credit claimed, NL428 line 76 "Line 76: Newfoundland and Labrador
political contribution tax credit (use Worksheet NL428) (maximum $500)": the amount as the filer
gives it, an optional input; a blank input is read as blank, and the line 76 step checks it against
the printed maximum."""

NL428_POLITICAL_CONTRIBUTION_TAX_CREDIT_MAXIMUM = AmountKind.declare(
    CATALOG, "nl428_political_contribution_tax_credit_maximum", non_negative=True
)
"""Political contribution tax credit maximum, printed on NL428 line 76 "(maximum $500)": the printed
maximum, from the `ca-nl/political_contribution_tax_credit_maximum` dataset; the bound line 76
cannot pass."""

NL428_POLITICAL_CONTRIBUTION_TAX_CREDIT_LINE_76 = AmountKind.declare(
    CATALOG, "nl428_political_contribution_tax_credit_line_76", non_negative=True
)
"""Newfoundland and Labrador political contribution tax credit, NL428 line 76 "Line 76:
Newfoundland and Labrador political contribution tax credit (use Worksheet NL428) (maximum $500)":
the entered amount, passed on unchanged when it is at most the printed maximum, blank when left
out; above the maximum it is refused, not capped."""

NL428_DIRECT_EQUITY_TAX_CREDIT_LINE_78 = AmountKind.declare(
    CATALOG, "nl428_direct_equity_tax_credit_line_78", non_negative=True
)
"""Direct equity tax credit, NL428 line 78 "Line 78: Direct equity tax credit (complete Form
T1272)": the credit from Form T1272, an optional input that a salary-only caller leaves out; a
blank input is read as blank."""

NL428_UCCB_RDSP_REPAYMENTS_LINE_89 = AmountKind.declare(
    CATALOG, "nl428_uccb_rdsp_repayments_line_89", non_negative=True
)
"""UCCB and RDSP repayments, NL428 line 89 "Line 89: Total of the universal child care benefit
(UCCB) repayment (line 21300 of the return) and the registered disability savings plan (RDSP) income
repayment (included on line 23200 of the return)": the total of the two repayments as the filer
gives it, an optional input; a blank input is read as blank, column 1 (you) only."""

NL428_UCCB_RDSP_INCOME_LINE_91 = AmountKind.declare(
    CATALOG, "nl428_uccb_rdsp_income_line_91", non_negative=True
)
"""UCCB and RDSP income, NL428 line 91 "Line 91: Total of the UCCB income (line 11700 of the return)
and the RDSP income (line 12500 of the return)": the total of the two incomes as the filer gives it,
an optional input; a blank input is read as blank, column 1 (you) only."""

NL428_REDUCTION_FOR_SPOUSE_OR_COMMON_LAW_PARTNER_CLAIMED_LINE_96 = CountKind.declare(
    CATALOG,
    "nl428_reduction_for_spouse_or_common_law_partner_claimed_line_96",
    non_negative=True,
)
"""Reduction for spouse or common-law partner claimed, NL428 line 96 "Line 96 and line 61880:
Reduction for spouse or common-law partner Claim $557": the eligibility claim, 1 when the reduction
is claimed, read as blank when left out."""

NL428_REDUCTION_FOR_SPOUSE_OR_COMMON_LAW_PARTNER_CLAIMED_CHECKED_LINE_96 = CountKind.declare(
    CATALOG,
    "nl428_reduction_for_spouse_or_common_law_partner_claimed_checked_line_96",
    non_negative=True,
)
"""Reduction for spouse or common-law partner claim, checked, NL428 line 96 "Line 96 and line 61880:
Reduction for spouse or common-law partner Claim $557": the claim with a blank read as 0, refused
above 1 so the reduction cannot be claimed twice."""

LOW_INCOME_REDUCTION_SPOUSE = AmountKind.declare(
    CATALOG, "low_income_reduction_spouse", non_negative=True
)
"""Reduction for spouse or common-law partner, NL428 line 96 "Line 96 and line 61880: Reduction for
spouse or common-law partner Claim $557": the printed $557, the amount claimed when the reduction is
claimed."""

NL428_REDUCTION_FOR_SPOUSE_OR_COMMON_LAW_PARTNER_LINE_96 = AmountKind.declare(
    CATALOG, "nl428_reduction_for_spouse_or_common_law_partner_line_96", non_negative=True
)
"""Reduction for spouse or common-law partner, NL428 line 96 "Line 96 and line 61880: Reduction for
spouse or common-law partner Claim $557": the printed $557 when the claim is 1, 0 when the claim is
blank or 0."""

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

NL428_DISABILITY_AMOUNT_SELF_WORKSHEET_LINE_40 = AmountKind.declare(
    CATALOG, "nl428_disability_amount_self_worksheet_line_40", non_negative=True
)
"""Disability amount for self from the worksheet, NL428 line 40 and line 58440 "Disability amount
for self (claim $7,467 or, if you were under 18 years of age, use Worksheet NL428)": Worksheet NL428
line 58440 line 7, read from that form, before the under-18 answer and the claim are applied."""

NL428_DISABILITY_AMOUNT_SELF_BASIS_LINE_40 = AmountKind.declare(
    CATALOG, "nl428_disability_amount_self_basis_line_40", non_negative=True
)
"""Disability amount for self before the claim, NL428 line 40 and line 58440 "Disability amount for
self (claim $7,467 or, if you were under 18 years of age, use Worksheet NL428)": the printed $7,467
for a filer 18 or older (or blank), the worksheet amount for a filer under 18."""

NL428_AGE_AMOUNT_WORKSHEET_LINE_17 = AmountKind.declare(
    CATALOG, "nl428_age_amount_worksheet_line_17", non_negative=True
)
"""Age amount from the worksheet, NL428 line 17 and line 58080 "Age amount (if you were born in 1960
or earlier) (use Worksheet NL428) (maximum $7,064)": Worksheet NL428 line 7, read from that form,
before the born-in-1960-or-earlier claim is applied."""

NL428_AGE_AMOUNT_LINE_17 = AmountKind.declare(
    CATALOG, "nl428_age_amount_line_17", non_negative=True
)
"""Age amount, NL428 line 17 and line 58080 "Age amount (if you were born in 1960 or earlier) (use
Worksheet NL428) (maximum $7,064)": the worksheet amount when the filer was born in 1960 or
earlier, 0 when not."""

NL428_CREDITS_SUBTOTAL_LINE_25 = AmountKind.declare(
    CATALOG, "nl428_credits_subtotal_line_25", non_negative=True
)
"""Personal amounts subtotal, NL428 line 25 "Line 25: Add lines 16, 17, 20, 23, and 24. = ^": the
sum of lines 16, 17, 20, 23 and 24, lines 20, 23 and 24 being optional and read as 0 when blank."""

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

NL428_BRACKET_LOWER_BOUND_LINE_3 = AmountKind.declare(
    CATALOG, "nl428_bracket_lower_bound_line_3", non_negative=True
)
"""Lower bound of the column, NL428 line 3 "Line 3: 0.00" (44,192.00; 88,382.00; 157,792.00): the
printed lower bound of the column of lines 2 to 8 that line 1 falls in. It is blank when line 1 is
above 220,910, where lines 9 to 15 apply."""

NL428_TAXABLE_INCOME_OVER_LOWER_BOUND_LINE_4 = AmountKind.declare(
    CATALOG, "nl428_taxable_income_over_lower_bound_line_4", non_negative=True
)
"""Taxable income over the lower bound, NL428 line 4 "Line 4: Line 2 minus line 3 (cannot be
negative) =": line 1 minus line 3, not below zero. It is blank when line 3 is blank, above
220,910."""

NL428_TAX_ON_EXCESS_LINE_6 = AmountKind.declare(
    CATALOG, "nl428_tax_on_excess_line_6", non_negative=True
)
"""Tax on the taxable income over the lower bound, NL428 line 6 "Line 6: Line 4 multiplied by the
percentage from line 5 =": line 4 times the line 5 rate, rounded half-up to the cent. It is blank
when line 4 or line 5 is blank, above 220,910."""

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

NL428_MEDICAL_EXPENSES_LIMITED_AMOUNT_LINE_52 = AmountKind.declare(
    CATALOG, "nl428_medical_expenses_limited_amount_line_52", non_negative=True
)
"""Line 51 limited to $2,410, NL428 line 52 "Enter whichever is less: $2,410 or the amount on line
51": the lesser of the printed $2,410 and line 51."""

NL428_MEDICAL_EXPENSES_OVER_LIMIT_LINE_53 = AmountKind.declare(
    CATALOG, "nl428_medical_expenses_over_limit_line_53", non_negative=True
)
"""Medical expenses over the limit, NL428 line 53 "Line 48 minus line 52 (if negative, enter "0")":
line 48 less line 52, not below 0; a blank line 48 is read as 0."""

NL428_MEDICAL_EXPENSES_ALLOWABLE_LINE_55 = AmountKind.declare(
    CATALOG, "nl428_medical_expenses_allowable_line_55", non_negative=True
)
"""Allowable medical expenses, NL428 line 55 "Line 53 plus line 54": line 53 plus line 54, line 54
being an optional input read as 0 when blank."""

NL428_CREDITS_TOTAL_LINE_56 = AmountKind.declare(
    CATALOG, "nl428_credits_total_line_56", non_negative=True
)
"""Credits total, NL428 line 56 "Line 47 plus line 55": the credits subtotal of line 47 plus the
allowable medical expenses of line 55."""

NL428_CREDITS_AT_RATE_LINE_58 = AmountKind.declare(
    CATALOG, "nl428_credits_at_rate_line_58", non_negative=True
)
"""Credits at the credit rate, NL428 line 58 "Line 56 multiplied by the percentage from line 57":
line 56 times the printed 8.7% rate of line 57."""

NL428_BRACKET_LOWER_BOUND_LINE_10 = AmountKind.declare(
    CATALOG, "nl428_bracket_lower_bound_line_10", non_negative=True
)
"""Lower bound of the column, NL428 line 10 "Line 10: 220,910.00": the printed lower bound of the
column of lines 9 to 15 that line 1 falls in, blank when line 1 is 220,910 or less."""

NL428_TAXABLE_INCOME_OVER_LOWER_BOUND_LINE_11 = AmountKind.declare(
    CATALOG, "nl428_taxable_income_over_lower_bound_line_11", non_negative=True
)
"""Taxable income over the lower bound, NL428 line 11 "Line 11: Line 9 minus line 10 (cannot be
negative) =": line 1 minus the lower bound of line 10, not below 0; blank when line 1 is 220,910.00
or less, where line 10 is blank."""

NL428_BRACKET_TAX_AT_START_LINE_7 = AmountKind.declare(
    CATALOG, "nl428_bracket_tax_at_start_line_7", non_negative=True
)
"""Tax at the start of the column, NL428 line 7 "Line 7: 0.00": the printed tax at the start of the
column of lines 2 to 8 that line 1 falls in, blank when line 1 is above 220,910."""

NL428_TAX_ON_EXCESS_LINE_13 = AmountKind.declare(
    CATALOG, "nl428_tax_on_excess_line_13", non_negative=True
)
"""Tax on the taxable income over the lower bound, NL428 line 13 "Line 13: Line 11 multiplied by the
percentage from line 12 =": line 11 times the line 12 rate, rounded half-up to the cent. It is
blank when line 11 or line 12 is blank, at or below 220,910."""

NL428_BRACKET_TAX_AT_START_LINE_14 = AmountKind.declare(
    CATALOG, "nl428_bracket_tax_at_start_line_14", non_negative=True
)
"""Tax at the start of the column, NL428 line 14 "Line 14: 32,454.04": the printed tax at the start
of the column of lines 9 to 15 that line 1 falls in, blank when line 1 is 220,910 or less."""

NL428_DIVIDEND_TAX_CREDIT_LINE_67 = AmountKind.declare(
    CATALOG, "nl428_dividend_tax_credit_line_67", non_negative=True
)
"""Newfoundland and Labrador dividend tax credit, NL428 line 67 "Line 67 and line 61520:
Newfoundland and Labrador dividend tax credit (use Worksheet NL428)": the amount as the filer gives
it, an optional input; a blank input is read as blank."""

NL428_T691_AMOUNT_LINE_71 = AmountKind.declare(
    CATALOG, "nl428_t691_amount_line_71", non_negative=True
)
"""Form T691 amount, NL428 line 71 "Line 71: Amount from line 14 of Part 7 of Form T691 multiplied
by 60% =": the amount from line 14 of Part 7 of Form T691 as the filer gives it, an optional input;
a blank input is read as blank, and the 60% multiplication step reads it."""

NL428_ADDITIONAL_TAX_MINIMUM_TAX_LINE_71 = AmountKind.declare(
    CATALOG, "nl428_additional_tax_minimum_tax_line_71", non_negative=True
)
"""Newfoundland and Labrador additional tax for minimum tax purposes, NL428 line 71 "Amount from
line 14 of Part 7 of Form T691 multiplied by 60% =": calculated, the Form T691 amount multiplied by
60%."""

NL428_SPOUSE_NET_INCOME_LINE_88 = AmountKind.declare(
    CATALOG, "nl428_spouse_net_income_line_88", non_negative=False
)
"""Spouse or common-law partner's net income, NL428 line 88 column 2 "Line 88: Net income from line
23600 of the return (or the amount you would have entered if the instructions on line 23600 said
"if negative, show in brackets")": the amount as the filer gives it, an optional input. It is
signed because the line takes the amount as if negative were shown in brackets; a blank input is
read as blank."""

NL428_SPOUSE_UCCB_AND_RDSP_REPAYMENT_LINE_89 = AmountKind.declare(
    CATALOG, "nl428_spouse_uccb_and_rdsp_repayment_line_89", non_negative=True
)
"""Spouse or common-law partner's UCCB and RDSP repayment, NL428 line 89 column 2 "Line 89: Total of
the universal child care benefit (UCCB) repayment (line 21300 of the return) and the registered
disability savings plan (RDSP) income repayment (included on line 23200 of the return)": the amount
as the filer gives it, an optional input; a blank input is read as blank."""

NL428_SPOUSE_UCCB_RDSP_INCOME_LINE_91 = AmountKind.declare(
    CATALOG, "nl428_spouse_uccb_rdsp_income_line_91", non_negative=True
)
"""Spouse or common-law partner's UCCB and RDSP income, NL428 line 91 column 2 "Line 91: Total of
the UCCB income (line 11700 of the return) and the RDSP income (line 12500 of the return)": the
total of the two incomes as the filer gives it, an optional input; a blank input is read as
blank."""

NL428_NET_INCOME_LINE_88 = AmountKind.declare(
    CATALOG, "nl428_net_income_line_88", non_negative=False
)
"""Net income, NL428 line 88 column 1 "Line 88: Net income from line 23600 of the return (or the
amount you would have entered if the instructions on line 23600 said "if negative, show in
brackets")": the net income of the T1 return before its floor, read from the signed T1 net income
export (`ca/net_income_signed`). The form shows a negative net income in brackets, so the kind is
signed."""

NL428_FAMILY_INCOME_LINE_90 = AmountKind.declare(
    CATALOG, "nl428_family_income_line_90", non_negative=False
)
"""Line 88 plus line 89, NL428 line 90 "Line 88 plus line 89", column 1 (you): the net income of
line 88 plus the UCCB and RDSP repayments of line 89. Line 88 can be negative, so the kind is
signed."""

NL428_SPOUSE_FAMILY_INCOME_LINE_90 = AmountKind.declare(
    CATALOG, "nl428_spouse_family_income_line_90", non_negative=False
)
"""Line 88 plus line 89, NL428 line 90 "Line 90: Line 88 plus line 89", column 2 (your spouse or
common-law partner): the spouse's net income of line 88 plus the spouse's UCCB and RDSP repayments
of line 89. Line 88 can be negative, so the kind is signed; both lines are optional inputs, so the
result is blank when line 88 is."""

NL428_ELIGIBLE_DEPENDANT_CLAIMED_LINE_97 = AmountKind.declare(
    CATALOG, "nl428_eligible_dependant_claimed_line_97", non_negative=True
)
"""Amount claimed on line 58160, read by NL428 line 97 "Line 97 and line 61890: Reduction for an
eligible dependant claimed on line 58160 Claim $557": line 23 of the credits form, the amount for
an eligible dependant, read across the forms. A blank line 23 is read as 0."""

NL428_LOW_INCOME_REDUCTION_DEPENDANT_LINE_97 = AmountKind.declare(
    CATALOG, "nl428_low_income_reduction_dependant_line_97", non_negative=True
)
"""Reduction for an eligible dependant, NL428 line 97 and line 61890 "Reduction for an eligible
dependant claimed on line 58160 Claim $557": the printed 557 where an amount is claimed on line
58160, and 0 where line 23 is 0 or blank."""

NL428_SPOUSE_FAMILY_INCOME_LESS_UCCB_RDSP_LINE_92 = AmountKind.declare(
    CATALOG, "nl428_spouse_family_income_less_uccb_rdsp_line_92", non_negative=True
)
"""Line 90 minus line 91, NL428 line 92 "Line 92: Line 90 minus line 91 (if negative, enter "0")",
column 2 (your spouse or common-law partner): the spouse's family income of line 90 less the
spouse's UCCB and RDSP income of line 91, not below 0, so the kind is non-negative. The result is
blank when line 90 is."""
