"""The Ontario artifact catalog: Ontario's own kinds, named from Forms ON428 (§2, §8), ON479,
Schedule ON479-A, T1221, ON-BEN and T1206 Part 3.

Only the kinds in use are declared. Amounts are Decimal, non-negative except the Form T1206 Part 3
lines that print no "(if negative, enter "0")" (lines 39, 47 and 50), which are signed, as no other
ON428, ON479 or ON479-A amount here can be negative; the counts of dependent children and
dependants are int, the T1221 slips and the co-operative education work placements record lists,
the ON479 line 63270 business number digits, and the ON479-A line 7 percentage a Rate. Federal
kinds come from `tax_calculator.jurisdictions.ca.catalog`. Identifiers are stable:
`tests/jurisdictions/ca_on/test_catalog.py` snapshots them.
"""

from __future__ import annotations

from decimal import Decimal

from tax_calculator.domain.artifact import ArtifactCatalog
from tax_calculator.domain.digits import DigitsKind
from tax_calculator.domain.parameters.rate import Rate
from tax_calculator.domain.record_list import RecordListKind
from tax_calculator.domain.registry import Namespace
from tax_calculator.jurisdictions.ca.catalog import (
    DEPENDANT_CARE_EXPENSES,
    DEPENDANT_NET_INCOME,
    DEPENDANT_TAXABLE_INCOME,
    DEPENDANT_UNDER_18,
)
from tax_calculator.jurisdictions.ca_on import NAMESPACE

CATALOG = ArtifactCatalog(Namespace(NAMESPACE))

ONTARIO_BASIC_TAX = CATALOG.declare("ontario_basic_tax", Decimal, non_negative=True)
"""Ontario tax on taxable income, 2025 ON428 line 8 (Part A), before non-refundable credits."""

BASIC_PERSONAL_AMOUNT = CATALOG.declare("basic_personal_amount", Decimal, non_negative=True)
"""Basic personal amount, ON428 line 9 (line 58040) "Basic personal amount Claim $12,747": the
amount claimed, the first part of the total of the Ontario credit amounts."""

AGE_MAXIMUM = CATALOG.declare("age_maximum", Decimal, non_negative=True)
"""Maximum Ontario age amount, Worksheet ON428 (form 5006-D), "Line 58080 - Age amount", line 1
"Maximum amount 6,223.00": the dataset as an artifact."""

AGE_INCOME_THRESHOLD = CATALOG.declare("age_income_threshold", Decimal, non_negative=True)
"""Income threshold of the Ontario age amount, Worksheet ON428 (form 5006-D), "Line 58080 - Age
amount", line 3 "Income threshold 46,330.00": the dataset as an artifact."""

AGE_INCOME_OVER_THRESHOLD = CATALOG.declare("age_income_over_threshold", Decimal, non_negative=True)
"""Net income over the income threshold, Worksheet ON428 (form 5006-D), "Line 58080 - Age amount",
line 4 "Line 2 minus line 3 (if negative, enter "0")": line 2 "Amount from line 23600 of your
return" less the income threshold of line 3, not below zero."""

AGE_REDUCTION = CATALOG.declare("age_reduction", Decimal, non_negative=True)
"""Reduction of the Ontario age amount, Worksheet ON428 (form 5006-D), "Line 58080 - Age amount",
line 6 "Line 4 multiplied by the percentage from line 5": line 4 at the applicable rate of line 5
"15%"."""

AGE_AMOUNT_BEFORE_COUNT = CATALOG.declare("age_amount_before_count", Decimal, non_negative=True)
"""Ontario age amount before it is claimed, Worksheet ON428 (form 5006-D), "Line 58080 - Age
amount", line 7 "Line 1 minus line 6 (if negative, enter "0") Enter this amount on line 58080 of
your Form ON428.": the maximum amount less the reduction, not below zero."""

AGE_AMOUNT = CATALOG.declare("age_amount", Decimal, non_negative=True)
"""Age amount, ON428 line 10 (line 58080) "Age amount (if you were born in 1960 or earlier) (use
Worksheet ON428) (maximum $6,223)": the worksheet's line 7 once if the filer was born in 1960 or
earlier, else 0, the T1 line 30100 count; a part of the total of the Ontario credit amounts."""

SPOUSE_BASE = CATALOG.declare("spouse_base", Decimal, non_negative=True)
"""Base amount for a spouse or common-law partner, ON428 line 11 "Base amount 11,905.00": the
amount claimed, before the spouse's net income comes off it."""

SPOUSE_AMOUNT_BEFORE_MAXIMUM = CATALOG.declare(
    "spouse_amount_before_maximum", Decimal, non_negative=True
)
"""Spouse or common-law partner amount before its maximum, ON428 line 13 "Line 11 minus line 12 (if
negative, enter "0")": the base amount less line 12 "Your spouse's or common-law partner's net
income from line 23600 of their return", the federal Schedule 5 line 4 figure, not below zero."""

SPOUSE_AMOUNT_BEFORE_COUNT = CATALOG.declare(
    "spouse_amount_before_count", Decimal, non_negative=True
)
"""Spouse or common-law partner amount before it is claimed, ON428 line 13's "(maximum $10,823)":
the amount before its maximum, at most it."""

SPOUSE_AMOUNT = CATALOG.declare("spouse_amount", Decimal, non_negative=True)
"""Spouse or common-law partner amount, ON428 line 13 (line 58120) "Line 11 minus line 12 (if
negative, enter "0") (maximum $10,823)": the capped amount once if the filer claims it, else 0,
the T1 line 30300 count; a part of the total of the Ontario credit amounts."""

ELIGIBLE_DEPENDANT_BASE = CATALOG.declare("eligible_dependant_base", Decimal, non_negative=True)
"""Base amount for an eligible dependant, ON428 line 14 "Base amount 11,905.00": the amount
claimed, before the dependant's net income comes off it."""

ELIGIBLE_DEPENDANT_AMOUNT_BEFORE_MAXIMUM = CATALOG.declare(
    "eligible_dependant_amount_before_maximum", Decimal, non_negative=True
)
"""Amount for an eligible dependant before its maximum, ON428 line 16 "Line 14 minus line 15 (if
negative, enter "0")": the base amount less line 15 "Your eligible dependant's net income from
line 23600 of their return", the federal Schedule 5 line 4 figure, not below zero."""

ELIGIBLE_DEPENDANT_AMOUNT_BEFORE_COUNT = CATALOG.declare(
    "eligible_dependant_amount_before_count", Decimal, non_negative=True
)
"""Amount for an eligible dependant before it is claimed, ON428 line 16's "(maximum $10,823)": the
amount before its maximum, at most it."""

ELIGIBLE_DEPENDANT_AMOUNT = CATALOG.declare("eligible_dependant_amount", Decimal, non_negative=True)
"""Amount for an eligible dependant, ON428 line 16 (line 58160): the capped amount for each
eligible dependant claimed for, the T1 line 30400 count, a part of the total of the Ontario credit
amounts."""

MEDICAL_NET_INCOME_SHARE = CATALOG.declare("medical_net_income_share", Decimal, non_negative=True)
"""Share of the net income for medical expenses, ON428 line 39 "Line 37 multiplied by the percentage
from line 38" (line 37 "Amount from line 23600 of your return", line 38 "Applicable rate 3%"): 3%
of the net income."""

MEDICAL_THRESHOLD = CATALOG.declare("medical_threshold", Decimal, non_negative=True)
"""Threshold for medical expenses, ON428 line 40 "Enter whichever is less: $2,885 or the amount on
line 39.": the lesser of the ceiling and the share of the net income."""

MEDICAL_EXPENSES_OVER_THRESHOLD = CATALOG.declare(
    "medical_expenses_over_threshold", Decimal, non_negative=True
)
"""Medical expenses over the threshold, ON428 line 41 "Line 36 minus line 40 (if negative, enter
"0")": the filer's own group, not below zero."""

OTHER_DEPENDANTS_MEDICAL = CATALOG.declare("other_dependants_medical", Decimal, non_negative=True)
"""Allowable medical expenses for other dependants, ON428 line 42 and line 58729 "Allowable amount
of medical expenses for other dependants (use Worksheet ON428)": line 4 "Add the amounts from
line 3 of columns 1, 2, and 3 (and others, if any)", each line 3 being "Line 1 minus line 2 (if
negative, enter "0") (maximum $15,551 per dependant)"."""

MEDICAL_CLAIM = CATALOG.declare("medical_claim", Decimal, non_negative=True)
"""Allowable medical expenses, ON428 line 43 and line 58769 "Line 41 plus line 42": the filer's own
group plus the allowable amount for other dependants, a part of the total of the Ontario credit
amounts (line 58800)."""

CLAIMED_AS_ELIGIBLE_DEPENDANT = CATALOG.declare(
    "claimed_as_eligible_dependant", int, non_negative=True
)
"""Whether a dependant is the one claimed on line 58160, Worksheet ON428 "Line 58185 - Ontario
caregiver amount" line 4 "Amount claimed for this dependant on line 58160 of your Form ON428, if
any": 1 for the dependant claimed there, 0 for any other (a flag above 1 is refused, and so is a
flag beyond the line 30400 count of eligible dependants), a field of each record of the caregiver
dependants."""

CAREGIVER_DEPENDANTS = RecordListKind.declare(
    CATALOG, "caregiver_dependants", fields=(DEPENDANT_NET_INCOME, CLAIMED_AS_ELIGIBLE_DEPENDANT)
)
"""Dependants for the Ontario caregiver amount, Worksheet ON428 "Line 58185 - Ontario caregiver
amount" "Complete one column for each dependant": a starting list with one record for each
dependant, holding line 2 "Dependant's net income from line 23600 of their return" and whether it
is the dependant claimed on line 58160 (line 4). The caller lists only the dependants who
qualify."""

CAREGIVER_AMOUNT = CATALOG.declare("caregiver_amount", Decimal, non_negative=True)
"""Ontario caregiver amount, ON428 line 17 and line 58185 "Ontario caregiver amount (use Worksheet
ON428)": Worksheet ON428 line 6 "Add the amounts from line 5 of columns 1, 2, and 3 (and others, if
any)", each line 5 "Allowable amount for this dependant: line 3 minus line 4 (if negative, enter
"0")", a part of the total of the Ontario credit amounts."""

ADOPTION_CREDIT = CATALOG.declare("adoption_credit", Decimal, non_negative=True)
"""Ontario adoption expenses, ON428 line 23 and line 58330 "Adoption expenses": the total of each
child's eligible expenses, each capped at the Ontario maximum for one child, a part of the total of
the Ontario credit amounts."""

PENSION_INCOME_CREDIT = CATALOG.declare("pension_income_credit", Decimal, non_negative=True)
"""Ontario pension income amount, ON428 line 27 and line 58360 "Pension income amount (maximum
$1,762)": the lesser of that maximum and the federal line 31400 amount, a part of the total of the
Ontario credit amounts."""

DEPENDANT_ON428_LINE_28 = CATALOG.declare("dependant_on428_line_28", Decimal, non_negative=True)
"""Amount from line 28 of the dependant's Form ON428, Worksheet ON428 "Line 58480 - Disability
amount transferred from a dependant", line 8 "Enter the amount from line 28 of the dependant's
Form ON428.", where ON428 line 28 is "Line 26 plus line 27 =": a starting amount from another
person's return, a field of each record of the dependants with a disability."""

DISABILITY_DEPENDANTS = RecordListKind.declare(
    CATALOG,
    "disability_dependants",
    fields=(
        DEPENDANT_UNDER_18,
        DEPENDANT_CARE_EXPENSES,
        DEPENDANT_ON428_LINE_28,
        DEPENDANT_TAXABLE_INCOME,
    ),
)
"""Dependants with a disability for the Ontario worksheet, Worksheet ON428 "Line 58480 - Disability
amount transferred from a dependant" "Complete this calculation for each dependant": a starting
list with one record for each such dependant, holding whether they were under 18 on December 31,
2025, line 3 the child care and attendant care expenses, line 8 the amount from line 28 of their
Form ON428 and line 10 their taxable income. The caller lists only the dependants who qualify."""

DISABILITY_TRANSFERRED_AMOUNT = CATALOG.declare(
    "disability_transferred_amount", Decimal, non_negative=True
)
"""Ontario disability amount transferred from a dependant, ON428 line 30 and line 58480 "Disability
amount transferred from a dependant (use Worksheet ON428)": "the total of allowable amounts
claimed for all dependants", each line 12 "Enter whichever is less: amount from line 7 or line
11. Allowable amount for this dependant", a part of the total of the Ontario credit amounts."""

DISABILITY_SELF_BASE_AMOUNT = CATALOG.declare(
    "disability_self_base_amount", Decimal, non_negative=True
)
"""Base amount for self, Worksheet ON428 (form 5006-D), "Line 58440 - Disability amount for self",
line 1 "Base amount 10,298.00": the dataset as an artifact."""

DISABILITY_SELF_SUPPLEMENT_MAXIMUM = CATALOG.declare(
    "disability_self_supplement_maximum", Decimal, non_negative=True
)
"""Maximum amount for self, Worksheet ON428 (form 5006-D), "Line 58440 - Disability amount for
self", line 2 "Maximum amount 6,007.00": the dataset as an artifact."""

DISABILITY_SELF_CARE_THRESHOLD = CATALOG.declare(
    "disability_self_care_threshold", Decimal, non_negative=True
)
"""Threshold for child and attendant care expenses for self, Worksheet ON428 (form 5006-D), "Line
58440 - Disability amount for self", line 4 "Threshold for child and attendant care expenses
3,518.00": the dataset as an artifact."""

DISABILITY_SELF_CARE_OVER_THRESHOLD = CATALOG.declare(
    "disability_self_care_over_threshold", Decimal, non_negative=True
)
"""Care expenses over the threshold for self, Worksheet ON428 (form 5006-D), "Line 58440 -
Disability amount for self", line 5 "Line 3 minus line 4 (if negative, enter "0") =": line 3 less
the threshold of line 4, not below zero."""

DISABILITY_SELF_SUPPLEMENT = CATALOG.declare(
    "disability_self_supplement", Decimal, non_negative=True
)
"""Supplement for self, Worksheet ON428 (form 5006-D), "Line 58440 - Disability amount for self",
line 6 "Line 2 minus line 5 (if negative, enter "0") =": the maximum amount less the care expenses
over the threshold, not below zero."""

DISABILITY_SELF_WORKSHEET_AMOUNT = CATALOG.declare(
    "disability_self_worksheet_amount", Decimal, non_negative=True
)
"""Disability amount for self under 18, Worksheet ON428 (form 5006-D), "Line 58440 - Disability
amount for self", line 7 "Line 1 plus line 6 Enter this amount on line 58440 of your Form ON428.
(maximum $16,305) =": the base amount plus the supplement; the printed maximum is met without a cap,
as the supplement is at most the maximum amount."""

DISABILITY_AMOUNT_FOR_SELF_IF_ELIGIBLE = CATALOG.declare(
    "disability_amount_for_self_if_eligible", Decimal, non_negative=True
)
"""Disability amount for self before the qualification, ON428 line 29 and line 58440 "Disability
amount for self (claim $10,298 or, if you were under 18 years of age, use Worksheet ON428)": the
base amount for a filer 18 or older on December 31, 2025, and the worksheet amount of line 7 for a
filer under 18."""

DISABILITY_AMOUNT_FOR_SELF = CATALOG.declare(
    "disability_amount_for_self", Decimal, non_negative=True
)
"""Ontario disability amount for self, ON428 line 29 and line 58440 "Disability amount for self
(claim $10,298 or, if you were under 18 years of age, use Worksheet ON428)": the amount once if the
filer qualifies, else 0; a part of the total of the Ontario credit amounts. Read by Form T1206
Part 3 line 34 "DTC from line 58440 of your provincial or territorial Form 428"."""

UNUSED_TUITION_AMOUNTS_BROUGHT_FORWARD = CATALOG.declare(
    "unused_tuition_amounts_brought_forward", Decimal, non_negative=True
)
"""Unused Ontario tuition and education amounts, Schedule ON(S11) line 1 "Enter your unused Ontario
tuition and education amounts from your 2024 notice of assessment or reassessment": a caller input,
the figure on that notice, not a calculation on this return."""

UNUSED_TUITION_INCOME_CAP = CATALOG.declare("unused_tuition_income_cap", Decimal, non_negative=True)
"""Income for the unused tuition limit, Schedule ON(S11) line 2 "Enter the amount from line 26000 of
your return on line 2 if it is $52,886 or less. If it is more than $52,886, enter the result of the
following calculation:" "Line 2: Amount from line 8 of your Form ON428" "divided by 5.05% =": the
taxable income at or below $52,886, else the Ontario tax on taxable income (ON428 line 8) divided by
5.05%, rounded half-up to the cent."""

CREDIT_AMOUNTS_THROUGH_DISABILITY_TRANSFER = CATALOG.declare(
    "credit_amounts_through_disability_transfer", Decimal, non_negative=True
)
"""Ontario credit amounts through the disability transfer, ON428 line 31 "Line 31: Add lines 28 to
30. =": the credit amounts before the medical expenses, the amounts on lines 9 to 25 (the basic
personal, age, spouse, eligible dependant and caregiver amounts, and the base CPP and EI
contributions) and line 30 "Disability amount transferred from a dependant (use Worksheet ON428)".
Schedule ON(S11) line 3 "Enter the amount from line 31 of your Form ON428." takes it."""

UNUSED_TUITION_ROOM = CATALOG.declare("unused_tuition_room", Decimal, non_negative=True)
"""Room for the unused tuition and education amounts, Schedule ON(S11) line 4 "Line 4: Line 2 minus
line 3 (if negative, enter "0") =": the income for the limit less the credit amounts through the
disability transfer, not below zero."""

UNUSED_TUITION_CLAIMED = CATALOG.declare("unused_tuition_claimed", Decimal, non_negative=True)
"""Unused Ontario tuition and education amounts claimed for 2025, Schedule ON(S11) line 5 "Line 5:
Enter whichever is less: amount from line 1 or line 4. Enter this amount on line 58560 of your Form
ON428.": the lesser of line 1 and line 4, the amount of ON428 line 33 and line 58560 "Your unused
tuition and education amounts (attach Schedule ON(S11))", a part of the total of the Ontario credit
amounts."""

UNUSED_TUITION_CARRIED_FORWARD = CATALOG.declare(
    "unused_tuition_carried_forward", Decimal, non_negative=True
)
"""Unused Ontario tuition and education amounts carried forward, Schedule ON(S11) line 8 "Line 8:
Line 6 minus line 7 Unused provincial tuition and education amounts available to carry forward to a
future year =": line 1 (line 6) less the amount claimed (line 7, from line 5), for a future year.
Lines 6 and 7 are copies of lines 1 and 5."""

SPOUSE_RETURN_ONTARIO_AGE_AMOUNT = CATALOG.declare(
    "spouse_return_ontario_age_amount", Decimal, non_negative=True
)
"""Their Ontario age amount, Schedule ON(S2) line 1 and line 59020 "Enter the amount from line 58080
of their Form ON428.": a figure from another person's return, a caller input, one for the one
spouse."""

SPOUSE_RETURN_ONTARIO_PENSION_INCOME_AMOUNT = CATALOG.declare(
    "spouse_return_ontario_pension_income_amount", Decimal, non_negative=True
)
"""Their Ontario pension income amount, Schedule ON(S2) line 2 and line 59050 "Enter the amount from
line 58360 of their Form ON428.": a figure from another person's return, a caller input."""

SPOUSE_RETURN_ONTARIO_DISABILITY_AMOUNT = CATALOG.declare(
    "spouse_return_ontario_disability_amount", Decimal, non_negative=True
)
"""Their Ontario disability amount, Schedule ON(S2) line 3 and line 59070 "Enter the amount from
line 58440 of their Form ON428.": a figure from another person's return, a caller input."""

SPOUSE_RETURN_ONTARIO_BASIC_TAX = CATALOG.declare(
    "spouse_return_ontario_basic_tax", Decimal, non_negative=True
)
"""Their Ontario tax on taxable income, Schedule ON(S2) line 5 "Amount from line 8 of their Form
ON428" "divided by 5.05% =": a figure from another person's return, a caller input."""

SPOUSE_RETURN_ONTARIO_BASIC_PERSONAL_AMOUNT = CATALOG.declare(
    "spouse_return_ontario_basic_personal_amount", Decimal, non_negative=True
)
"""Their Ontario basic personal amount, Schedule ON(S2) line 6 "Amount from line 58040 of their Form
ON428": a figure from another person's return, a caller input."""

SPOUSE_RETURN_ONTARIO_PENSION_INCOME_AMOUNT_MAXIMUM = CATALOG.declare(
    "spouse_return_ontario_pension_income_amount_maximum", Decimal, non_negative=True
)
"""Largest pension income amount transferred from a spouse, Schedule ON(S2) line 2 and line 59050
"Enter the amount from line 58360 of their Form ON428. (maximum $1,762)": the dataset as an
artifact, the maximum printed on the spouse's Form ON428 line 58360."""

SPOUSE_RETURN_ONTARIO_PENSION_INCOME_AMOUNT_CHECKED = CATALOG.declare(
    "spouse_return_ontario_pension_income_amount_checked", Decimal, non_negative=True
)
"""Their Ontario pension income amount after the check, Schedule ON(S2) line 2 and line 59050
"Enter the amount from line 58360 of their Form ON428. (maximum $1,762)": the amount
`ca-on/spouse_return_ontario_pension_income_amount` once it is at most its maximum
(`core/at_most`), which line 4 adds."""

SPOUSE_RETURN_ONTARIO_DISABILITY_AMOUNT_MAXIMUM = CATALOG.declare(
    "spouse_return_ontario_disability_amount_maximum", Decimal, non_negative=True
)
"""Largest disability amount transferred from a spouse, Worksheet ON428 (form 5006-D), "Line 58440 -
Disability amount for self", line 7 "Line 1 plus line 6 Enter this amount on line 58440 of your Form
ON428. (maximum $16,305)": the dataset as an artifact."""

SPOUSE_RETURN_ONTARIO_DISABILITY_AMOUNT_CHECKED = CATALOG.declare(
    "spouse_return_ontario_disability_amount_checked", Decimal, non_negative=True
)
"""Their Ontario disability amount after the check, Schedule ON(S2) line 3 and line 59070 "Enter the
amount from line 58440 of their Form ON428.": the amount
`ca-on/spouse_return_ontario_disability_amount` once it is at most
`ca-on/spouse_return_ontario_disability_amount_maximum` (`core/at_most`), which line 4 adds."""

SPOUSE_RETURN_ONTARIO_AGE_AMOUNT_CHECKED = CATALOG.declare(
    "spouse_return_ontario_age_amount_checked", Decimal, non_negative=True
)
"""Their Ontario age amount after the check, Schedule ON(S2) line 1 and line 59020 "Enter the amount
from line 58080 of their Form ON428.": the amount `ca-on/spouse_return_ontario_age_amount` once it
is at most the maximum age amount `ca-on/age_maximum` (`core/at_most`, "maximum $6,223"), which
line 4 adds."""

SPOUSE_RETURN_ONTARIO_BASIC_PERSONAL_AMOUNT_CHECKED = CATALOG.declare(
    "spouse_return_ontario_basic_personal_amount_checked", Decimal, non_negative=True
)
"""Their Ontario basic personal amount after the check, Schedule ON(S2) line 6 "Amount from line
58040 of their Form ON428": the amount `ca-on/spouse_return_ontario_basic_personal_amount` once it
is at most `ca-on/basic_personal_amount` (`core/at_most`, "Claim $12,747"), which line 9 adds."""

SPOUSE_RETURN_ONTARIO_LINE_24 = CATALOG.declare(
    "spouse_return_ontario_line_24", Decimal, non_negative=True
)
"""Their ON428 line 24, Schedule ON(S2) line 7 "Amount from line 24 of their Form ON428": a figure
from another person's return, a caller input."""

SPOUSE_RETURN_ONTARIO_UNUSED_TUITION_AMOUNT = CATALOG.declare(
    "spouse_return_ontario_unused_tuition_amount", Decimal, non_negative=True
)
"""Their unused Ontario tuition and education amounts claimed, Schedule ON(S2) line 8 "Amount from
line 58560 of their Form ON428": a figure from another person's return, a caller input."""

SPOUSE_TRANSFERABLE_AMOUNTS = CATALOG.declare(
    "spouse_transferable_amounts", Decimal, non_negative=True
)
"""Their transferable Ontario amounts, Schedule ON(S2) line 4 "Add lines 1 to 3. =": the sum of
their age, pension income and disability amounts (lines 1 to 3)."""

SPOUSE_INCOME_FOR_TRANSFER = CATALOG.declare(
    "spouse_income_for_transfer", Decimal, non_negative=True
)
"""Their income for the transfer, Schedule ON(S2) line 5 "Enter the amount from line 26000 of their
return on line 5 if it is $52,886 or less. If it is more than $52,886, enter the result of the
following calculation: Amount from line 8 of their Form ON428 divided by 5.05% =": their taxable
income at or below $52,886, else their Ontario tax (ON428 line 8) divided by 5.05%, rounded
half-up to the cent."""

SPOUSE_CREDITS_USED = CATALOG.declare("spouse_credits_used", Decimal, non_negative=True)
"""Their credit amounts used, Schedule ON(S2) line 9 "Add lines 6 to 8. =": the sum of their basic
personal amount, ON428 line 24 and unused tuition and education amounts claimed (lines 6 to 8)."""

SPOUSE_ADJUSTED_TAXABLE_INCOME = CATALOG.declare(
    "spouse_adjusted_taxable_income", Decimal, non_negative=True
)
"""Their taxable income left after their own credits, Schedule ON(S2) line 10 and line 59120 "Line 5
minus line 9 (if negative, enter "0") =": line 5 less line 9, not below zero."""

SPOUSE_UNUSED_AMOUNTS = CATALOG.declare("spouse_unused_amounts", Decimal, non_negative=True)
"""Their unused amounts, Schedule ON(S2) line 11 "Line 4 minus line 10 (if negative, enter "0")":
line 4 less line 10, not below zero."""

AMOUNTS_TRANSFERRED_FROM_SPOUSE = CATALOG.declare(
    "amounts_transferred_from_spouse", Decimal, non_negative=True
)
"""Provincial amounts transferred from your spouse or common-law partner, Schedule ON(S2) line 11
"Enter this amount on line 58640 of your Form ON428. Provincial amounts transferred from your
spouse or common-law partner", ON428 line 34 and line 58640 "Amounts transferred from your spouse
or common-law partner (attach Schedule ON(S2))", a part of line 35 "Add lines 31 to 34. =": line 11,
or zero when separated for 90 days or more including December 31, 2025."""

NON_REFUNDABLE_CREDIT_AMOUNTS = CATALOG.declare(
    "non_refundable_credit_amounts", Decimal, non_negative=True
)
"""Total of the Ontario non-refundable credit amounts, ON428 line 44 (line 58800) "Line 35 plus
line 43": the sum of the credit amounts the rate is applied to once, here, in line order, the
basic personal amount (line 58040), the age amount (line 58080), the spouse or common-law
partner amount (line 58120), the amount for an eligible dependant (line 58160), the Ontario
caregiver amount (line 58185), the base CPP contributions (line 58240), the base CPP
contributions on self-employment income (line 58280), the EI premiums (line 58300), the EI
premiums on self-employment (line 58305), the disability amount transferred from a dependant
(line 58480), the unused tuition and education amounts claimed (line 58560) and the allowable
medical expenses (line 58769)."""

CREDIT_AMOUNTS_AT_CREDIT_RATE = CATALOG.declare(
    "credit_amounts_at_credit_rate", Decimal, non_negative=True
)
"""Ontario credit amounts at the credit rate, ON428 line 46 (line 58840) "Line 44 multiplied by the
percentage from line 45": the total of the credit amounts times the credit rate, the first of the
two lines that line 50 adds."""

DONATIONS_FIRST_TIER_CREDIT = CATALOG.declare(
    "donations_first_tier_credit", Decimal, non_negative=True
)
"""Ontario donations credit at the first tier, ON428 line 47 "Amount from line 13 of your federal
Schedule 9" "multiplied by 5.05%": 5.05% of Schedule 9 line 13."""

DONATIONS_OVER_FIRST_TIER_CREDIT = CATALOG.declare(
    "donations_over_first_tier_credit", Decimal, non_negative=True
)
"""Ontario donations credit over the first tier, ON428 line 48 "Amount from line 14 of your federal
Schedule 9" "multiplied by 11.16%": 11.16% of Schedule 9 line 14."""

DONATIONS_AND_GIFTS_CREDIT = CATALOG.declare(
    "donations_and_gifts_credit", Decimal, non_negative=True
)
"""Ontario donations and gifts credit, ON428 line 49 (line 58969) "Line 47 plus line 48": the sum of
the two tiers."""

NON_REFUNDABLE_TAX_CREDITS = CATALOG.declare(
    "non_refundable_tax_credits", Decimal, non_negative=True
)
"""Ontario non-refundable tax credits, ON428 line 50 (line 61500) "Line 46 plus line 49 Enter this
amount on line 52. Ontario non-refundable tax credits": line 46 (line 58840), the total of the
Ontario credit amounts times the credit rate, plus line 49 (line 58969), the donations and gifts
credit."""

ONTARIO_TAX_AFTER_CREDITS = CATALOG.declare("ontario_tax_after_credits", Decimal, non_negative=True)
"""Ontario tax after non-refundable tax credits, not below zero: 2025 ON428 line 53."""

ONTARIO_TAX_ON_SPLIT_INCOME = CATALOG.declare(
    "ontario_tax_on_split_income", Decimal, non_negative=True
)
"""Ontario tax on split income, ON428 line 54 and line 61510 "Ontario tax on split income (complete
Form T1206)", Form T1206 Part 3 line 33 "The amount from line 31 multiplied by the tax rate you
entered on line 32": the total split income (line 31, the T1206 line 4) at the Ontario high tax rate
of Chart C column 2."""

TOSI_ADJUSTED_TAXABLE_INCOME = CATALOG.declare(
    "tosi_adjusted_taxable_income", Decimal, non_negative=True
)
"""Ontario TOSI-adjusted taxable income, Form T1206 Part 3 line 33C "Amount from line 33A divided by
the tax rate you entered on line 33B": the Ontario tax on split income (line 33A, the T1206 line
33) divided by the Chart C column 3 rate, 5.05%. A declared output: with the exception of Ontario,
a provincial Schedule adds it, and nothing else on the Ontario return reads it."""

SPLIT_INCOME_LINE_36 = CATALOG.declare("split_income_line_36", Decimal, non_negative=True)
"""Disability amounts on split income, Form T1206 Part 3 line 36 "Line 34 plus line 35", line 34
being "DTC from line 58440 of your provincial or territorial Form 428" and line 35 "DTC transferred
from a dependant from line 58480 of your provincial or territorial Form 428": the Ontario disability
amount for self plus the amount transferred from a dependant."""

SPLIT_INCOME_LINE_38 = CATALOG.declare("split_income_line_38", Decimal, non_negative=True)
"""Disability credit on split income, Form T1206 Part 3 line 38 "Amount from line 36 multiplied by
the tax rate you entered on line 37": line 36 at the Ontario low tax rate of Chart C column 3."""

SPLIT_INCOME_LINE_39 = CATALOG.declare("split_income_line_39", Decimal)
"""Ontario tax on split income less the disability credit, Form T1206 Part 3 line 39 "Line 33 minus
line 38": the Ontario tax on split income less the disability credit.

The form prints no "(if negative, enter "0")", so the kind is signed.
"""

SPLIT_INCOME_LINE_42 = CATALOG.declare("split_income_line_42", Decimal, non_negative=True)
"""Ontario dividend tax credit on split income, eligible, Form T1206 Part 3 line 42 "Amount from
line 40 multiplied by the rate you entered on line 41", line 40 being "Amount from line 18": the
eligible dividends on split income at the eligible dividend tax credit rate of Chart C column 5."""

SPLIT_INCOME_LINE_45 = CATALOG.declare("split_income_line_45", Decimal, non_negative=True)
"""Ontario dividend tax credit on split income, other than eligible, Form T1206 Part 3 line 45
"Amount from line 43 multiplied by the rate you entered on line 44", line 43 being "Amount from line
17": the dividends other than eligible on split income at the dividend other than eligible dividend
tax credit rate of Chart C column 6."""

SPLIT_INCOME_LINE_46 = CATALOG.declare("split_income_line_46", Decimal, non_negative=True)
"""Ontario dividend tax credit on split income, Form T1206 Part 3 line 46 "Line 42 plus line 45":
the Ontario dividend tax credit on split income."""

SPLIT_INCOME_LINE_47 = CATALOG.declare("split_income_line_47", Decimal)
"""Ontario tax on split income after the credits, Form T1206 Part 3 line 47 "Line 39 minus line
46": line 39 less the dividend tax credit.

The form prints no "(if negative, enter "0")", so the kind is signed.
"""

SPLIT_INCOME_LINE_49 = CATALOG.declare("split_income_line_49", Decimal, non_negative=True)
"""Provincial foreign tax credit on split income, Form T1206 Part 3 line 49 "Part of the amount
from line 68370 on page 8 that is non-business income" over "Part of the amount from line 68380 on
page 8 that is non-business income", "× Amount from line number of your Form 428 shown in column 7
in Chart C on page 5" (ON428 line 82): the provincial foreign tax credit times the share of the
split income that is non-business income from foreign sources, 0 when there is no such income."""

SPLIT_INCOME_LINE_50 = CATALOG.declare("split_income_line_50", Decimal)
"""Ontario tax on split income after the foreign tax credit, Form T1206 Part 3 line 50 "Line 48
minus line 49", line 48 being "Amount from line 47 on the previous page": line 47 less the
provincial foreign tax credit of line 49.

The form prints no "(if negative, enter "0")", so the kind is signed.
"""

ONTARIO_TAX_WITH_SPLIT_INCOME = CATALOG.declare(
    "ontario_tax_with_split_income", Decimal, non_negative=True
)
"""Ontario tax with the tax on split income, ON428 line 55 "Line 53 plus line 54": the Ontario tax
after credits (line 53) plus the Ontario tax on split income (line 54)."""

ONTARIO_TAX_ON_SPLIT_INCOME_FOR_SURTAX = CATALOG.declare(
    "ontario_tax_on_split_income_for_surtax", Decimal, non_negative=True
)
"""Ontario tax on split income taken out of the surtax base, ON428 line 64 "Ontario tax on split
income from line 54": the Ontario tax on split income, carried."""

ONTARIO_SURTAX_BASE = CATALOG.declare("ontario_surtax_base", Decimal, non_negative=True)
"""Ontario surtax base, ON428 line 65 "Line 63 minus line 64 (if negative, enter "0")": line 63
(the Ontario tax with the tax on split income, lines 62 and 63 carrying line 61) less line 64
(the Ontario tax on split income), not below zero."""

ONTARIO_SURTAX = CATALOG.declare("ontario_surtax", Decimal, non_negative=True)
"""Ontario surtax, 2025 ON428 line 68 "Line 66 plus line 67": the 20% tier over $5,710 (line 66)
plus the 36% tier over $7,307 (line 67), each on line 65, the surtax base.

Line 65 is "Line 63 minus line 64 (if negative, enter "0")", with line 64 the Ontario tax on split
income (`ontario_surtax_base`). Lines 62 and 63 carry line 61, the Ontario tax with the tax on split
income less the minimum tax carryover (line 60).
"""

ONTARIO_TAX_WITH_SURTAX = CATALOG.declare("ontario_tax_with_surtax", Decimal, non_negative=True)
"""Ontario tax with surtax, 2025 ON428 line 69 "Line 62 plus line 68": the Ontario tax with the tax
on split income less the minimum tax carryover (line 62, which carries line 61) plus the Ontario
surtax."""

DIVIDENDS_AMOUNT_A = CATALOG.declare("dividends_amount_a", Decimal, non_negative=True)
"""Dividends amount A, Worksheet ON428 line 61520 line A "Amount from line 12000 of your
return": the whole line 12000, as the worksheet has no Note 1."""

DIVIDENDS_AMOUNT_B = CATALOG.declare("dividends_amount_b", Decimal, non_negative=True)
"""Dividends amount B, Worksheet ON428 line 61520 line 1 "Amount from line 12010 of your return Line
B": the whole line 12010."""

OTHER_DIVIDENDS_CREDIT = CATALOG.declare("other_dividends_credit", Decimal, non_negative=True)
"""Ontario credit on dividends other than eligible, Worksheet ON428 line 61520 line 1 "multiplied by
2.9863%": amount B times the rate."""

DIVIDENDS_AMOUNT_A_LESS_B = CATALOG.declare("dividends_amount_a_less_b", Decimal, non_negative=True)
"""Dividends amount A less amount B, Worksheet ON428 line 61520 line 2 "Amount A minus amount B Line
C": the eligible dividends."""

ELIGIBLE_DIVIDENDS_CREDIT = CATALOG.declare("eligible_dividends_credit", Decimal, non_negative=True)
"""Ontario credit on eligible dividends, Worksheet ON428 line 61520 line 2 "multiplied by 10%": line
C times the rate."""

DIVIDEND_TAX_CREDIT = CATALOG.declare("dividend_tax_credit", Decimal, non_negative=True)
"""Ontario dividend tax credit, Worksheet ON428 line 61520 line 3 "Line 1 plus line 2 Enter this
amount on line 61520 of your Form ON428.": the credit on dividends other than eligible plus the
credit on eligible dividends, which is ON428 line 57."""

ONTARIO_TAX_BEFORE_DIVIDEND_CREDIT = CATALOG.declare(
    "ontario_tax_before_dividend_credit", Decimal, non_negative=True
)
"""Ontario tax before the dividend tax credit, ON428 line 56 "Enter the amount from line 53 above.":
the Ontario tax after non-refundable tax credits."""

ONTARIO_TAX_LESS_DIVIDEND_CREDIT = CATALOG.declare(
    "ontario_tax_less_dividend_credit", Decimal, non_negative=True
)
"""Ontario tax less the dividend tax credit, ON428 line 58 "Line 56 minus line 57 (if negative,
enter "0")": the Ontario tax after credits less the Ontario dividend tax credit (line 57), not
below zero. Line 60 reads it, and the manifest also returns it."""

DIVIDEND_CREDIT_FROM_LINE_57 = CATALOG.declare(
    "dividend_credit_from_line_57", Decimal, non_negative=True
)
"""Ontario dividend tax credit from line 57, ON428 line 70 "Ontario dividend tax credit from line
57": the credit of line 57 again."""

ONTARIO_TAX_AFTER_DIVIDEND_CREDIT = CATALOG.declare(
    "ontario_tax_after_dividend_credit", Decimal, non_negative=True
)
"""Ontario tax after the dividend tax credit, ON428 line 71 "Line 69 minus line 70 (if negative,
enter "0")": the Ontario tax with surtax less the dividend tax credit, not below zero. Line 73 adds
line 72 to it."""

TAX_REDUCTION_BASIC = CATALOG.declare("tax_reduction_basic", Decimal, non_negative=True)
"""Basic reduction, ON428 line 74 "Basic reduction 294.00": the amount claimed, the first part of
the Ontario tax reduction amounts."""

DEPENDENT_CHILDREN = CATALOG.declare("dependent_children", int, non_negative=True)
"""Number of dependent children, ON428 line 75 (line 60969) "Number of dependent children
multiplied by $544", the children "born in 2007 or later": a starting count."""

TAX_REDUCTION_FOR_CHILDREN = CATALOG.declare(
    "tax_reduction_for_children", Decimal, non_negative=True
)
"""Reduction for dependent children, ON428 line 75 (line 60969) "Number of dependent children
multiplied by $544": the amount claimed, 0 where the rule that "only the individual with the higher
net income can claim the amounts on lines 75 and 76" leaves it to the spouse or common-law
partner."""

DEPENDANTS = CATALOG.declare("dependants", int, non_negative=True)
"""Number of dependants, ON428 line 76 (line 60970) "Number of dependants multiplied by $544", the
dependants "with a mental or physical impairment": a starting count."""

TAX_REDUCTION_FOR_DEPENDANTS = CATALOG.declare(
    "tax_reduction_for_dependants", Decimal, non_negative=True
)
"""Reduction for dependants, ON428 line 76 (line 60970) "Number of dependants multiplied by
$544": the amount claimed, 0 where the rule that "only the individual with the higher net income
can claim the amounts on lines 75 and 76" leaves it to the spouse or common-law partner."""

TAX_REDUCTION_AMOUNTS = CATALOG.declare("tax_reduction_amounts", Decimal, non_negative=True)
"""Ontario tax reduction amounts, ON428 line 77 "Add lines 74 to 76.": the basic reduction plus
the reductions for dependent children and for dependants."""

ONTARIO_TAX_REDUCTION = CATALOG.declare("ontario_tax_reduction", Decimal, non_negative=True)
"""Ontario tax reduction, ON428 line 80 "Line 78 minus line 79 (if negative, enter "0") Ontario
tax reduction": line 78 "Amount from line 77 above multiplied by 2", less line 79 "Amount from
line 73 above", or "0" where any of the six conditions after "Enter "0" on line 80 if any of the
following applies to you" applies.

Line 73 is "Line 71 plus line 72" and line 71 "Line 69 minus line 70 (if negative, enter "0")".
The rule that only the spouse or common-law partner with the higher net income claims lines 75
and 76 is applied in lines 75 and 76.
"""

ONTARIO_MINIMUM_TAX = CATALOG.declare("ontario_minimum_tax", Decimal, non_negative=True)
"""Ontario additional tax for minimum tax purposes, ON428 line 72 "If you entered an amount on line
11 of Part 5 of Form T691, use Worksheet ON428 to calculate your additional tax for minimum tax
purposes": Worksheet ON428 line 9 "Line 1 plus line 8 Enter this amount on line 72 of your Form
ON428."."""

MINIMUM_TAX_CARRYOVER_CREDIT = CATALOG.declare(
    "minimum_tax_carryover_credit", Decimal, non_negative=True
)
"""Ontario minimum tax carryover credit, ON428 line 59 "Amount from line 40427 of your return
multiplied by 24.63% =": the minimum tax carryover applied on the T1, at the Ontario minimum tax
rate."""

ONTARIO_MINIMUM_TAX_CARRYOVER_APPLIED = CATALOG.declare(
    "ontario_minimum_tax_carryover_applied", Decimal, non_negative=True
)
"""Ontario minimum tax carryover applied, ON428 line 60 and line 61540 "Enter whichever is less:
amount from line 58 or line 59.": the lesser of the Ontario tax after the dividend tax credit and
the carryover credit."""

ONTARIO_TAX_AFTER_MINIMUM_TAX_CARRYOVER = CATALOG.declare(
    "ontario_tax_after_minimum_tax_carryover", Decimal, non_negative=True
)
"""Ontario tax after the minimum tax carryover, ON428 line 61 "Line 55 minus line 60 (if negative,
enter "0")", the amount on lines 62 and 63."""

WORKSHEET_ON428_LINE_1 = CATALOG.declare("worksheet_on428_line_1", Decimal, non_negative=True)
"""Worksheet ON428 "Line 72 - Ontario additional tax for minimum tax purposes" line 1 "Amount from
line 11 of Part 5 of your Form T691 multiplied by 24.63% =": the Ontario share of the additional
federal minimum tax."""

WORKSHEET_ON428_LINE_2 = CATALOG.declare("worksheet_on428_line_2", Decimal, non_negative=True)
"""Worksheet ON428 line 72 line 2 "Amount from line 65 of your Form ON428": the base of the
surtax."""

WORKSHEET_ON428_LINE_3 = CATALOG.declare("worksheet_on428_line_3", Decimal, non_negative=True)
"""Worksheet ON428 line 72 line 3 "Line 1 plus line 2 =": the surtax base with the additional
tax."""

WORKSHEET_ON428_LINE_6 = CATALOG.declare("worksheet_on428_line_6", Decimal, non_negative=True)
"""Worksheet ON428 line 72 line 6 "Line 4 plus line 5 =": the surtax on line 3, lines 4 and 5 being
each tier "if negative, enter "0"" (line 4 on the amount over $5,710 at 20%, line 5 on the amount
over $7,307 at 36%)."""

WORKSHEET_ON428_LINE_7 = CATALOG.declare("worksheet_on428_line_7", Decimal, non_negative=True)
"""Worksheet ON428 line 72 line 7 "Amount from line 68 of your Form ON428": the Ontario surtax."""

WORKSHEET_ON428_LINE_8 = CATALOG.declare("worksheet_on428_line_8", Decimal)
"""Worksheet ON428 line 72 line 8 "Line 6 minus line 7 =": the surtax on the additional tax. The
form prints no "(if negative, enter "0")", so it is signed (it is never negative, as line 65 is at
most line 3)."""

ONTARIO_TAX_BEFORE_REDUCTION = CATALOG.declare(
    "ontario_tax_before_reduction", Decimal, non_negative=True
)
"""Ontario tax before the reduction, ON428 line 73 "Line 71 plus line 72 =": the Ontario tax after
the dividend tax credit plus the additional tax for minimum tax purposes."""

NOT_RESIDENT_OF_CANADA_AT_START_OF_YEAR = CATALOG.declare(
    "not_resident_of_canada_at_start_of_year", int, non_negative=True
)
"""Not a resident of Canada at the beginning of the year, ON428 "Enter "0" on line 80 if any of the
following applies to you" "You were not a resident of Canada at the beginning of the year": the
caller's count, 1 when it applies and 0 when it does not."""

NOT_RESIDENT_OF_CANADA_AT_START_OF_YEAR_CHECKED = CATALOG.declare(
    "not_resident_of_canada_at_start_of_year_checked", int, non_negative=True
)
"""Not a resident of Canada at the beginning of the year, ON428 "Enter "0" on line 80 if any of the
following applies to you" "You were not a resident of Canada at the beginning of the year": the
answer of `ca-on/not_resident_of_canada_at_start_of_year` after the check that it is 0 or 1
(`ca/yes_or_no_count`), a count of 1 or 0. A count of 2 or more is refused, not capped."""

NOT_RESIDENT_OF_ONTARIO_AT_YEAR_END = CATALOG.declare(
    "not_resident_of_ontario_at_year_end", int, non_negative=True
)
"""Not a resident of Ontario on December 31, 2025, ON428 "Enter "0" on line 80 if any of the
following applies to you" "You were not a resident of Ontario on December 31, 2025": the caller's
count, 1 when it applies and 0 when it does not. Form T1221 "You must be a resident of Ontario on
the last day of the tax year to claim this credit." reads the same count."""

NOT_RESIDENT_OF_ONTARIO_AT_YEAR_END_CHECKED = CATALOG.declare(
    "not_resident_of_ontario_at_year_end_checked", int, non_negative=True
)
"""Not a resident of Ontario on December 31, 2025, ON428 "Enter "0" on line 80 if any of the
following applies to you" "You were not a resident of Ontario on December 31, 2025": the answer of
`ca-on/not_resident_of_ontario_at_year_end` after the check that it is 0 or 1
(`ca/yes_or_no_count`), a count of 1 or 0. A count of 2 or more is refused, not capped."""

BANKRUPT_IN_YEAR = CATALOG.declare("bankrupt_in_year", int, non_negative=True)
"""Bankrupt at any time in 2025, ON428 "Enter "0" on line 80 if any of the following applies to
you" "You were bankrupt at any time in 2025": the caller's count, 1 when it applies and 0 when it
does not."""

BANKRUPT_IN_YEAR_CHECKED = CATALOG.declare("bankrupt_in_year_checked", int, non_negative=True)
"""Bankrupt at any time in 2025, ON428 "Enter "0" on line 80 if any of the following applies to
you" "You were bankrupt at any time in 2025": the answer of `ca-on/bankrupt_in_year` after the
check that it is 0 or 1 (`ca/yes_or_no_count`), a count of 1 or 0. A count of 2 or more is
refused, not capped."""

RETURN_FILED_BY_TRUSTEE_IN_BANKRUPTCY = CATALOG.declare(
    "return_filed_by_trustee_in_bankruptcy", int, non_negative=True
)
"""Return filed by a trustee in bankruptcy, ON428 "Enter "0" on line 80 if any of the following
applies to you" "Your return is filed for you by a trustee in bankruptcy": the caller's count, 1
when it applies and 0 when it does not."""

RETURN_FILED_BY_TRUSTEE_IN_BANKRUPTCY_CHECKED = CATALOG.declare(
    "return_filed_by_trustee_in_bankruptcy_checked", int, non_negative=True
)
"""Return filed by a trustee in bankruptcy, ON428 "Enter "0" on line 80 if any of the following
applies to you" "Your return is filed for you by a trustee in bankruptcy": the answer of
`ca-on/return_filed_by_trustee_in_bankruptcy` after the check that it is 0 or 1
(`ca/yes_or_no_count`), a count of 1 or 0. A count of 2 or more is refused, not capped."""

NOT_CLAIMING_ONTARIO_TAX_REDUCTION = CATALOG.declare(
    "not_claiming_ontario_tax_reduction", int, non_negative=True
)
"""Choosing not to claim an Ontario tax reduction, ON428 "Enter "0" on line 80 if any of the
following applies to you" "You are choosing not to claim an Ontario tax reduction": the filer's
election, the caller's count, 1 when it applies and 0 when it does not."""

NOT_CLAIMING_ONTARIO_TAX_REDUCTION_CHECKED = CATALOG.declare(
    "not_claiming_ontario_tax_reduction_checked", int, non_negative=True
)
"""Choosing not to claim an Ontario tax reduction, ON428 "Enter "0" on line 80 if any of the
following applies to you" "You are choosing not to claim an Ontario tax reduction": the answer of
`ca-on/not_claiming_ontario_tax_reduction` after the check that it is 0 or 1
(`ca/yes_or_no_count`), a count of 1 or 0. A count of 2 or more is refused, not capped."""

TAX_REDUCTION_CLAIMABLE = CATALOG.declare("tax_reduction_claimable", int, non_negative=True)
"""Whether line 80 is completed, ON428 "Enter "0" on line 80 if any of the following applies to
you" "If none of the above applies to you, complete lines 74 to 80": 0 when any of the six printed
conditions applies, else 1."""

CLAIMS_TAX_REDUCTION_AMOUNTS_AT_EQUAL_NET_INCOME = CATALOG.declare(
    "claims_tax_reduction_amounts_at_equal_net_income", int, non_negative=True
)
"""Whether this return claims lines 75 and 76 when the two net incomes are equal, ON428 "only the
individual with the higher net income can claim the amounts on lines 75 and 76": the form names no
claimant at a tie, so the caller's count, 1 when this return claims them and 0 when it does not."""

CLAIMS_TAX_REDUCTION_AMOUNTS_AT_EQUAL_NET_INCOME_CHECKED = CATALOG.declare(
    "claims_tax_reduction_amounts_at_equal_net_income_checked", int, non_negative=True
)
"""Whether this return claims lines 75 and 76 when the two net incomes are equal, ON428 "only the
individual with the higher net income can claim the amounts on lines 75 and 76": the answer of
`ca-on/claims_tax_reduction_amounts_at_equal_net_income` after the check that it is 0 or 1
(`ca/yes_or_no_count`), a count of 1 or 0. A count of 2 or more is refused, not capped."""

TAX_REDUCTION_AMOUNTS_CLAIMABLE = CATALOG.declare(
    "tax_reduction_amounts_claimable", int, non_negative=True
)
"""Whether this return claims lines 75 and 76, ON428 "If you had a spouse or common-law partner on
December 31, 2025, only the individual with the higher net income can claim the amounts on lines 75
and 76": 1 or 0."""

TAX_REDUCTION_FOR_CHILDREN_BEFORE_SPOUSE_RULE = CATALOG.declare(
    "tax_reduction_for_children_before_spouse_rule", Decimal, non_negative=True
)
"""Reduction for dependent children before the spouse rule, ON428 line 75 (line 60969) "Number of
dependent children multiplied by $544": the amount before the rule that "only the individual with
the higher net income can claim the amounts on lines 75 and 76"."""

TAX_REDUCTION_FOR_DEPENDANTS_BEFORE_SPOUSE_RULE = CATALOG.declare(
    "tax_reduction_for_dependants_before_spouse_rule", Decimal, non_negative=True
)
"""Reduction for dependants before the spouse rule, ON428 line 76 (line 60970) "Number of
dependants multiplied by $544": the amount before the rule that "only the individual with the
higher net income can claim the amounts on lines 75 and 76"."""

ONTARIO_TAX_REDUCTION_BEFORE_CONDITIONS = CATALOG.declare(
    "ontario_tax_reduction_before_conditions", Decimal, non_negative=True
)
"""Ontario tax reduction before the conditions, ON428 line 80 "Line 78 minus line 79 (if negative,
enter "0") Ontario tax reduction": line 78 less line 79, before the conditions on which the form
enters "0" on line 80."""

ONTARIO_TAX_AFTER_REDUCTION = CATALOG.declare(
    "ontario_tax_after_reduction", Decimal, non_negative=True
)
"""Ontario tax after the Ontario tax reduction, ON428 line 81 "Line 73 minus line 80 (if negative,
enter "0")": the Ontario tax after the dividend tax credit (line 73) less the Ontario tax
reduction."""

TAX_OTHERWISE_PAYABLE_LINE_71 = CATALOG.declare(
    "tax_otherwise_payable_line_71", Decimal, non_negative=True
)
"""Line 71 for the tax otherwise payable, ON428 line 71 "Line 69 minus line 70 (if negative, enter
"0")" with "0" on line 70, as Form T2036 note (4) directs: line 69."""

TAX_OTHERWISE_PAYABLE_LINE_73 = CATALOG.declare(
    "tax_otherwise_payable_line_73", Decimal, non_negative=True
)
"""Line 73 for the tax otherwise payable, ON428 line 73 "Line 71 plus line 72 =" with "0" on line
72, as Form T2036 note (4) directs: line 71."""

TAX_OTHERWISE_PAYABLE_REDUCTION_BEFORE_CONDITIONS = CATALOG.declare(
    "tax_otherwise_payable_reduction_before_conditions", Decimal, non_negative=True
)
"""Ontario tax reduction before the conditions for the tax otherwise payable, ON428 line 80 "Line 78
minus line 79 (if negative, enter "0") Ontario tax reduction": line 78 less line 79, the latter
being the line 73 of the tax otherwise payable, before the conditions on which the form enters "0"
on line 80."""

TAX_OTHERWISE_PAYABLE_REDUCTION_CLAIMABLE = CATALOG.declare(
    "tax_otherwise_payable_reduction_claimable", int, non_negative=True
)
"""Whether line 80 is completed for the tax otherwise payable, ON428 "Enter "0" on line 80 if any of
the following applies to you" "If none of the above applies to you, complete lines 74 to 80", with
"0" on line 72 so that "There is an amount on line 72" cannot apply: 0 when any of the other five
printed conditions applies, else 1."""

TAX_OTHERWISE_PAYABLE_REDUCTION = CATALOG.declare(
    "tax_otherwise_payable_reduction", Decimal, non_negative=True
)
"""Ontario tax reduction for the tax otherwise payable, ON428 line 80 "Ontario tax reduction" with
"0" on lines 70 and 72: line 78 less line 79 when none of the five conditions applies, else "0"."""

TAX_OTHERWISE_PAYABLE = CATALOG.declare("tax_otherwise_payable", Decimal, non_negative=True)
"""Provincial tax otherwise payable, Form T2036 note (4) "Provincial or territorial tax otherwise
payable": for a resident of Ontario, ON428 line 81 "Line 73 minus line 80 (if negative, enter
"0")" calculated by entering "0" on lines 70 and 72."""

PROVINCIAL_FOREIGN_TAX_CREDIT_BEFORE_LIMIT = CATALOG.declare(
    "provincial_foreign_tax_credit_before_limit", Decimal, non_negative=True
)
"""Provincial foreign tax credit before its limit, Form T2036 line 5 "Provincial or territorial
foreign tax credit" and "Enter the total from line 5 (for each country if applicable)": the total of
the sheets' line 5, before "should not be more than" the tax otherwise payable."""

PROVINCIAL_FOREIGN_TAX_CREDIT = CATALOG.declare(
    "provincial_foreign_tax_credit", Decimal, non_negative=True
)
"""Provincial foreign tax credit, ON428 line 82 "Provincial foreign tax credit (complete Form
T2036)": the total of Form T2036 line 5, which "should not be more than the amount entered on the
line for provincial or territorial tax otherwise payable"."""

ONTARIO_TAX_AFTER_FOREIGN_TAX_CREDIT = CATALOG.declare(
    "ontario_tax_after_foreign_tax_credit", Decimal, non_negative=True
)
"""Ontario tax after the provincial foreign tax credit, ON428 line 83 "Line 81 minus line 82 (if
negative, enter "0")": the Ontario tax after the Ontario tax reduction less the provincial foreign
tax credit."""

LIFT_EMPLOYMENT_INCOME = CATALOG.declare("lift_employment_income", Decimal, non_negative=True)
"""LIFT employment income, Schedule ON428-A line 3 "Line 1 plus line 2": line 1 "Amount from line
10100 of your return" (employment income) plus line 2 "Amount from line 10400 of your return"
(other employment income), in line order, the base of the LIFT rate on line 5."""

LIFT_CREDIT_BEFORE_MAXIMUM = CATALOG.declare(
    "lift_credit_before_maximum", Decimal, non_negative=True
)
"""LIFT credit before its maximum, Schedule ON428-A line 5 "Line 3 multiplied by the percentage
from line 4 (maximum $875)" before the maximum: line 4 "Applicable rate 5.05%" on line 3 "Line 1
plus line 2", the sum of employment income (line 1 "Amount from line 10100 of your return") and
other employment income (line 2 "Amount from line 10400 of your return")."""

LIFT_MAXIMUM_CREDIT = CATALOG.declare("lift_maximum_credit", Decimal, non_negative=True)
"""LIFT credit at most its maximum, Schedule ON428-A line 5's "(maximum $875)", Part A line 14
"Amount from line 5 above (maximum $875)" and Part B line 29 "Amount from line 5 of the previous
page (maximum $875)"."""

LIFT_NET_INCOME_AND_REPAYMENTS = CATALOG.declare(
    "lift_net_income_and_repayments", Decimal, non_negative=False
)
"""Net income and repayments, Schedule ON428-A line 9 "Add lines 6 to 8.": line 6 "Net income from
line 23600 of your return (or the amount you would have entered if the instructions on line 23600
said "if negative, show in brackets")", line 7 "Amount from line 21300 of your return" and line 8
"Amount of registered disability savings plan (RDSP) income repayment included on line 23200 of
your return". Line 9 prints no floor and line 6 may be negative, so the kind is signed."""

LIFT_UCCB_AND_RDSP_INCOME = CATALOG.declare("lift_uccb_and_rdsp_income", Decimal, non_negative=True)
"""UCCB and RDSP income, Schedule ON428-A line 12 "Line 10 plus line 11": line 10 "Amount from line
11700 of your return" and line 11 "Amount of RDSP income included on line 12500 of your return"."""

LIFT_ADJUSTED_NET_INCOME = CATALOG.declare("lift_adjusted_net_income", Decimal, non_negative=True)
"""Adjusted net income, Schedule ON428-A line 13 "Line 9 minus line 12 (if negative, enter "0")
Your adjusted net income", which Part A line 15 "Amount from line 13 above" and Part B line 30
"Amount from line 13 of the previous page" take."""

LIFT_REDUCTION = CATALOG.declare("lift_reduction", Decimal, non_negative=True)
"""LIFT credit reduction, Schedule ON428-A Part A line 19 "Line 17 multiplied by the percentage
from line 18": line 18 "Applicable rate 5%" on line 17 "Line 15 minus line 16 (if negative, enter
"0")", line 16 "Individual income threshold 32,500.00".

Line 15 is "Amount from line 13 above", the adjusted net income (line 13). The schedule states no
eligibility rules of its own ("To find out if you are eligible for the low-income individuals and
families tax (LIFT) credit, go to canada.ca/on-tax-info.").
"""

LIFT_CREDIT_SINGLE = CATALOG.declare("lift_credit_single", Decimal, non_negative=True)
"""LIFT credit for a single individual, Schedule ON428-A Part A line 20 "Line 14 minus line 19 (if
negative, enter "0") Enter this amount on line 62140 of your Form ON428.": the maximum credit less
the reduction."""

LIFT_SPOUSE_NET_INCOME_AND_REPAYMENTS = CATALOG.declare(
    "lift_spouse_net_income_and_repayments", Decimal, non_negative=False
)
"""Spouse's net income and repayments, Schedule ON428-A Part B line 24 "Add lines 21 to 23.", the
sum of the caller's existing spouse inputs (`ca/spouse_net_income_before_adjustments`,
`ca/spouse_uccb_repayment`, `ca/spouse_rdsp_income_repayment`). Line 24 prints no floor and line 21
may be negative, so the kind is signed."""

LIFT_SPOUSE_UCCB_AND_RDSP_INCOME = CATALOG.declare(
    "lift_spouse_uccb_and_rdsp_income", Decimal, non_negative=True
)
"""Spouse's UCCB and RDSP income, Schedule ON428-A Part B line 27 "Line 25 plus line 26", the sum of
the caller's existing spouse inputs (`ca/spouse_universal_child_care_benefit`,
`ca/spouse_rdsp_income`)."""

LIFT_SPOUSE_ADJUSTED_NET_INCOME = CATALOG.declare(
    "lift_spouse_adjusted_net_income", Decimal, non_negative=True
)
"""Spouse's adjusted net income, Schedule ON428-A Part B line 28 "Line 24 minus line 27 (if
negative, enter "0") Your spouse's or common-law partner's adjusted net income"."""

LIFT_INDIVIDUAL_INCOME_THRESHOLD = CATALOG.declare(
    "lift_individual_income_threshold", Decimal, non_negative=True
)
"""Individual income threshold, Schedule ON428-A Part B line 31 "Individual income threshold
32,500.00": a printed amount, taken whole."""

LIFT_EXCESS_OVER_INDIVIDUAL_THRESHOLD = CATALOG.declare(
    "lift_excess_over_individual_threshold", Decimal, non_negative=True
)
"""Excess over the individual threshold, Schedule ON428-A Part B line 32 "Line 30 minus line 31 (if
negative, enter "0")", line 30 being "Amount from line 13 of the previous page"."""

LIFT_FAMILY_NET_INCOME = CATALOG.declare("lift_family_net_income", Decimal, non_negative=True)
"""Adjusted family net income, Schedule ON428-A Part B line 35 "Line 33 plus line 34 Adjusted
family net income": line 33 "Amount from line 30 above" and line 34 "Amount from line 28 above"."""

LIFT_FAMILY_INCOME_THRESHOLD = CATALOG.declare(
    "lift_family_income_threshold", Decimal, non_negative=True
)
"""Family income threshold, Schedule ON428-A Part B line 36 "Family income threshold 65,0000.00":
a printed amount, taken whole. The text prints a typo; the threshold is 65,000.00."""

LIFT_EXCESS_OVER_FAMILY_THRESHOLD = CATALOG.declare(
    "lift_excess_over_family_threshold", Decimal, non_negative=True
)
"""Excess over the family threshold, Schedule ON428-A Part B line 37 "Line 35 minus line 36 (if
negative, enter "0")"."""

LIFT_GREATER_EXCESS = CATALOG.declare("lift_greater_excess", Decimal, non_negative=True)
"""Greater excess, Schedule ON428-A Part B line 38 "Enter whichever is more: amount from line 32 or
line 37."."""

LIFT_FAMILY_REDUCTION = CATALOG.declare("lift_family_reduction", Decimal, non_negative=True)
"""LIFT credit reduction for a family, Schedule ON428-A Part B line 40 "Line 38 multiplied by the
percentage from line 39", line 39 being "Applicable rate 5%"."""

LIFT_CREDIT_WITH_SPOUSE = CATALOG.declare("lift_credit_with_spouse", Decimal, non_negative=True)
"""LIFT credit for an individual with a spouse or common-law partner, Schedule ON428-A Part B line
41 "Line 29 minus line 40 (if negative, enter "0") Enter this amount on line 62140 of your Form
ON428.": line 29 "Amount from line 5 of the previous page (maximum $875)" less the reduction."""

LIFT_CREDIT = CATALOG.declare("lift_credit", Decimal, non_negative=True)
"""LIFT credit, ON428 line 85 (62140) "Low-income individuals and families tax (LIFT) credit
(complete Schedule ON428-A)": Part A line 20 for a single individual, or Part B line 41 when there
was a spouse or common-law partner at the end of the year."""

ONTARIO_TAX_AFTER_LIFT_CREDIT = CATALOG.declare(
    "ontario_tax_after_lift_credit", Decimal, non_negative=True
)
"""Ontario tax after the LIFT credit, ON428 line 86 "Line 84 minus line 85 (if negative, enter
"0")": the Ontario tax after the reduction less the LIFT credit, as line 84 "Amount from line 83
of the previous page" carries line 83 "Line 81 minus line 82 (if negative, enter "0")", which is
line 81 less the provincial foreign tax credit (line 82, Form T2036)."""

COMMUNITY_FOOD_PROGRAM_DONATIONS = CATALOG.declare(
    "community_food_program_donations", Decimal, non_negative=True
)
"""Qualifying community food program donations, ON428 line 87 and line 62150 "Enter the amount of
qualifying donations that have also been claimed as a charitable donation.": a starting amount,
taken as entered, and checked against the gifts claimed (Schedule 9 line 12 "Line 10 plus line 11")
before the rate applies."""

COMMUNITY_FOOD_PROGRAM_DONATIONS_APPLIED = CATALOG.declare(
    "community_food_program_donations_applied", Decimal, non_negative=True
)
"""Community food program donations applied, ON428 line 87 "Enter the amount of qualifying donations
that have also been claimed as a charitable donation.": the donations, refused when above the gifts
claimed (Schedule 9 line 12, which is line 13 plus line 14), not capped."""

COMMUNITY_FOOD_PROGRAM_CREDIT = CATALOG.declare(
    "community_food_program_credit", Decimal, non_negative=True
)
"""Community food program donation tax credit for farmers, ON428 line 87 "multiplied by 25%": the
donations applied (line 62150) at the rate."""

ONTARIO_TAX_AFTER_FOOD_CREDIT = CATALOG.declare(
    "ontario_tax_after_food_credit", Decimal, non_negative=True
)
"""Ontario tax after the community food program donation tax credit for farmers, ON428 line 88
"Line 86 minus line 87 (if negative, enter "0")": the Ontario tax after the LIFT credit less the
credit."""

SPLIT_INCOME_LINE_52 = CATALOG.declare("split_income_line_52", Decimal, non_negative=True)
"""Ontario tax after the split income floor, Form T1206 Part 3 line 52 "Enter whichever is more: the
amount from line 50 or line 51", line 51 being "Amount from the line number of your Form 428 shown
in column 8 of Chart C" (ON428 line 88): the more of line 50 and line 88, which the form enters on
ON428 line 88 and which line 90 adds the health premium to."""

HEALTH_PREMIUM_INCOME = CATALOG.declare("health_premium_income", Decimal, non_negative=True)
"""Taxable income for the Ontario health premium, ON428 line 89 chart line 1 "Enter your taxable
income from line 26000 of your return" with Form T1206 Part 1 "add the amount from line 4 of this
form to your taxable income when calculating your Ontario health premium on Form ON428": the
taxable income plus the total split income."""

ONTARIO_HEALTH_PREMIUM = CATALOG.declare("ontario_health_premium", Decimal, non_negative=True)
"""Ontario health premium, ON428 line 89 "Ontario health premium (complete the chart below)": the
chart on the taxable income with the split income added (its line 1 "Enter your taxable income from
line 26000 of your return"),
each sloped row the previous plateau plus a rate on the income over the row's threshold, at most
the next plateau."""

ONTARIO_TAX = CATALOG.declare("ontario_tax", Decimal, non_negative=True)
"""Ontario tax, ON428 line 90 "Line 88 plus line 89 Enter this amount on line 42800 of your
return. Ontario tax": line 88, which Form T1206 Part 3 line 52 sets to the more of its line 50 and
the Ontario tax after the community food program donation tax credit for farmers, plus the Ontario
health premium."""

FERTILITY_EXPENSES = CATALOG.declare("fertility_expenses", Decimal, non_negative=True)
"""Eligible medical expenses for fertility treatment, Form ON479 line 1 and line 61268 "Eligible
medical expenses for fertility treatment": a starting amount, from the receipts the form asks for.

The form prints no eligibility rules for the line; eligibility is to be confirmed."""

FERTILITY_CREDIT_BEFORE_MAXIMUM = CATALOG.declare(
    "fertility_credit_before_maximum", Decimal, non_negative=True
)
"""Fertility treatment credit before its maximum, Form ON479 line 1 "Eligible medical expenses for
fertility treatment multiplied by 25% (maximum $5,000) =" before the maximum: the 25% on the
expenses."""

FERTILITY_CREDIT = CATALOG.declare("fertility_credit", Decimal, non_negative=True)
"""Fertility treatment credit, Form ON479 line 1 and line 61268 "Eligible medical expenses for
fertility treatment multiplied by 25% (maximum $5,000) =": the 25% on the expenses, at most
$5,000, the maximum being printed after the percentage."""

CARE_ADJUSTED_INCOME = CATALOG.declare("care_adjusted_income", Decimal, non_negative=True)
"""Ontario CARE credit adjusted income, Schedule ON479-A column 1 "You", line 4 "Add lines 1 to 3
(if negative, enter "0"). Adjusted income": line 1 (net income from line 23600 of the return, before
the floor at 0, or the amount you would have entered if the instructions on line 23600 said "if
negative, show in brackets") plus line 2 (the child care expenses deduction from line 21400) plus
line 3 (the social benefits repayment from line 23500), not below zero."""

CARE_SUPPORTING_PERSONS_ADJUSTED_INCOME = CATALOG.declare(
    "care_supporting_persons_adjusted_income", Decimal, non_negative=True
)
"""Ontario CARE credit supporting persons' adjusted income, Schedule ON479-A column 2 "Supporting
person(s)", line 4 (line 63047) "Add lines 1 to 3 (if negative, enter "0"). Adjusted income": a
starting amount, as it comes from other people's returns, not below zero as the form floors it."""

CARE_FAMILY_ADJUSTED_INCOME = CATALOG.declare(
    "care_family_adjusted_income", Decimal, non_negative=True
)
"""Ontario CARE credit family adjusted income, Schedule ON479-A line 5 "Add the amounts from line 4
of columns 1 and 2. Family adjusted income": your adjusted income plus the supporting persons'."""

CARE_CREDIT_PERCENTAGE = CATALOG.declare("care_credit_percentage", Rate)
"""Ontario CARE credit rate, Schedule ON479-A line 7 "If your family adjusted income on line 5 is
"0", enter 75%. If not, enter the tax credit rate that applies to your family adjusted income from
the table below.": the rate of the table's row the family adjusted income falls in, a rate, not
money."""

CARE_CREDIT = CATALOG.declare("care_credit", Decimal, non_negative=True)
"""Ontario CARE credit, Schedule ON479-A line 8 "Line 6 multiplied by the percentage from line 7
Enter this amount on line 63050 of your Form ON479." and Form ON479 line 2 (line 63050): the child
care expenses deduction (line 6) at the rate of line 7."""

CLAIMS_SENIORS_CARE_CREDIT = CATALOG.declare("claims_seniors_care_credit", int, non_negative=True)
"""Whether the filer claims the Ontario seniors care at home tax credit, Form ON479 line 13 and line
63095: a starting count, 0 or 1, that multiplies line 13, so 1 if the filer claims it, else 0.

The form prints no eligibility rules for the credit; the caller claims it only for a filer who
qualifies."""

CLAIMS_SENIORS_CARE_CREDIT_CHECKED = CATALOG.declare(
    "claims_seniors_care_credit_checked", int, non_negative=True
)
"""Claiming the Ontario seniors care at home tax credit, Form ON479 line 13 and line 63095: the
answer of `ca-on/claims_seniors_care_credit` after the check that it is 0 or 1
(`ca/yes_or_no_count`), a count of 1 or 0. A count of 2 or more is refused, not capped."""

SENIORS_CARE_BEFORE_MAXIMUM = CATALOG.declare(
    "seniors_care_before_maximum", Decimal, non_negative=True
)
"""Seniors care at home credit before its maximum, Form ON479 line 5 "Line 3 multiplied by the
percentage from line 4 (maximum $1,500) =" before the maximum: line 4 "Allowable percentage 25%" on
line 3 "Medical expenses from line 58769 of your Form ON428"."""

SENIORS_CARE_AMOUNT = CATALOG.declare("seniors_care_amount", Decimal, non_negative=True)
"""Seniors care at home credit amount, Form ON479 line 5 "Line 3 multiplied by the percentage from
line 4 (maximum $1,500) =": the 25% on the medical expenses, at most $1,500, the maximum being
printed after the percentage."""

SENIORS_CARE_FAMILY_NET_INCOME = CATALOG.declare(
    "seniors_care_family_net_income", Decimal, non_negative=True
)
"""Family net income, Form ON479 line 8 "Line 6 plus line 7 Family net income =": line 6 "Your net
income from line 23600 of your return" plus line 7 "Your spouse's or common-law partner's net
income from line 23600 of their return (if applicable)", 0 with no spouse."""

SENIORS_CARE_BASE_AMOUNT = CATALOG.declare("seniors_care_base_amount", Decimal, non_negative=True)
"""Form ON479 line 9 "Base amount 35,000.00": the dataset's amount as an artifact."""

SENIORS_CARE_INCOME_OVER_BASE = CATALOG.declare(
    "seniors_care_income_over_base", Decimal, non_negative=True
)
"""Family net income over the base amount, Form ON479 line 10 "Line 8 minus line 9 (if negative,
enter "0") =": not below zero."""

SENIORS_CARE_REDUCTION = CATALOG.declare("seniors_care_reduction", Decimal, non_negative=True)
"""Seniors care at home credit reduction, Form ON479 line 12 "Line 10 multiplied by the percentage
from line 11 =": line 11 "Applicable rate 5%" on the family net income over the base amount."""

SENIORS_CARE_BEFORE_CLAIM = CATALOG.declare("seniors_care_before_claim", Decimal, non_negative=True)
"""Seniors care at home credit before the claim, Form ON479 line 13 "Line 5 minus line 12 (if
negative, enter "0") =": the amount less the reduction, not below zero. The form's rules for a
family net income of $35,000 or less and of more than $65,000 follow from lines 9 to 12."""

SENIORS_CARE_CREDIT = CATALOG.declare("seniors_care_credit", Decimal, non_negative=True)
"""Ontario seniors care at home tax credit, Form ON479 line 13 and line 63095 "Line 5 minus line 12
(if negative, enter "0") =": line 13 once if the filer claims the credit, else 0."""

SENIORS_TRANSIT_PAID = CATALOG.declare("seniors_transit_paid", Decimal, non_negative=True)
"""Amount paid for eligible seniors' use of Ontario public transit services, Form ON479 line 14
"Amount paid in the year for eligible seniors' use of Ontario public transit services (maximum
$3,000) Line 63100": a starting amount, from the receipts the form asks for.

The form prints no eligibility rules for the line; eligibility is to be confirmed."""

SENIORS_TRANSIT_MAXIMUM = CATALOG.declare("seniors_transit_maximum", Decimal, non_negative=True)
"""Seniors' public transit maximum, Form ON479 line 14 "Amount paid in the year for eligible
seniors' use of Ontario public transit services (maximum $3,000)": the $3,000, the most the amount
paid can be, the maximum being printed before the percentage."""

SENIORS_TRANSIT_AMOUNT_PAID_CHECKED = CATALOG.declare(
    "seniors_transit_amount_paid_checked", Decimal, non_negative=True
)
"""Amount paid for seniors' transit, not above its maximum, Form ON479 line 14 "Amount paid in the
year for eligible seniors' use of Ontario public transit services (maximum $3,000)": the amount
paid, refused above $3,000, the maximum being printed before the percentage."""

SENIORS_TRANSIT_CREDIT = CATALOG.declare("seniors_transit_credit", Decimal, non_negative=True)
"""Seniors' public transit credit, Form ON479 line 14 "Amount paid in the year for eligible
seniors' use of Ontario public transit services (maximum $3,000) Line 63100 multiplied by 15% =":
15% of the amount paid, at most $3,000."""

POLITICAL_CONTRIBUTIONS = CATALOG.declare("political_contributions", Decimal, non_negative=True)
"""Ontario political contributions, Form ON479 line 15 and line 63100 "Ontario political
contributions made in 2025": a starting amount, taken as the form takes it. Worksheet ON479 line 1
of each column "Enter your total political contributions from line 63110 of your Form ON479." reads
it.

The form gives no eligibility conditions beyond "Ontario political contributions"."""

POLITICAL_CREDIT_COLUMN_1_LINE_2 = CATALOG.declare(
    "political_credit_column_1_line_2", Decimal, non_negative=True
)
"""Political contribution credit column 1 line 2, Worksheet ON479 "Column 1: Line 63110 is $500.05
or less", line 2 "0.00": a printed constant."""

POLITICAL_CREDIT_COLUMN_1_LINE_3 = CATALOG.declare(
    "political_credit_column_1_line_3", Decimal, non_negative=True
)
"""Political contribution credit column 1 line 3, Worksheet ON479 "Column 1: Line 63110 is $500.05
or less", line 3 "Line 1 minus line 2 (cannot be negative)": the contributions less line 2, not
below zero."""

POLITICAL_CREDIT_COLUMN_1_LINE_5 = CATALOG.declare(
    "political_credit_column_1_line_5", Decimal, non_negative=True
)
"""Political contribution credit column 1 line 5, Worksheet ON479 "Column 1: Line 63110 is $500.05
or less", line 5 "Line 3 multiplied by the percentage from line 4": line 3 at the line 4 rate of
75%."""

POLITICAL_CREDIT_COLUMN_1_LINE_6 = CATALOG.declare(
    "political_credit_column_1_line_6", Decimal, non_negative=True
)
"""Political contribution credit column 1 line 6, Worksheet ON479 "Column 1: Line 63110 is $500.05
or less", line 6 "0.00": a printed constant."""

POLITICAL_CREDIT_COLUMN_1_LINE_7 = CATALOG.declare(
    "political_credit_column_1_line_7", Decimal, non_negative=True
)
"""Political contribution credit column 1 line 7, Worksheet ON479 "Column 1: Line 63110 is $500.05
or less", line 7 "Line 5 plus line 6 Enter this amount on line 16 of your Form ON479.": line 5
plus line 6."""

POLITICAL_CREDIT_COLUMN_2_LINE_2 = CATALOG.declare(
    "political_credit_column_2_line_2", Decimal, non_negative=True
)
"""Political contribution credit column 2 line 2, Worksheet ON479 "Column 2: Line 63110 is more than
$500.05 but not more than $1,666.82", line 2 "500.05": a printed constant."""

POLITICAL_CREDIT_COLUMN_2_LINE_3 = CATALOG.declare(
    "political_credit_column_2_line_3", Decimal, non_negative=True
)
"""Political contribution credit column 2 line 3, Worksheet ON479 "Column 2: Line 63110 is more than
$500.05 but not more than $1,666.82", line 3 "Line 1 minus line 2 (cannot be negative)": the
contributions less line 2, not below zero."""

POLITICAL_CREDIT_COLUMN_2_LINE_5 = CATALOG.declare(
    "political_credit_column_2_line_5", Decimal, non_negative=True
)
"""Political contribution credit column 2 line 5, Worksheet ON479 "Column 2: Line 63110 is more than
$500.05 but not more than $1,666.82", line 5 "Line 3 multiplied by the percentage from line 4":
line 3 at the line 4 rate of 50%."""

POLITICAL_CREDIT_COLUMN_2_LINE_6 = CATALOG.declare(
    "political_credit_column_2_line_6", Decimal, non_negative=True
)
"""Political contribution credit column 2 line 6, Worksheet ON479 "Column 2: Line 63110 is more than
$500.05 but not more than $1,666.82", line 6 "375.03": a printed constant."""

POLITICAL_CREDIT_COLUMN_2_LINE_7 = CATALOG.declare(
    "political_credit_column_2_line_7", Decimal, non_negative=True
)
"""Political contribution credit column 2 line 7, Worksheet ON479 "Column 2: Line 63110 is more than
$500.05 but not more than $1,666.82", line 7 "Line 5 plus line 6 Enter this amount on line 16 of
your Form ON479.": line 5 plus line 6."""

POLITICAL_CREDIT_COLUMN_3_LINE_2 = CATALOG.declare(
    "political_credit_column_3_line_2", Decimal, non_negative=True
)
"""Political contribution credit column 3 line 2, Worksheet ON479 "Column 3: Line 63110 is more than
$1,666.82", line 2 "1,666.82": a printed constant."""

POLITICAL_CREDIT_COLUMN_3_LINE_3 = CATALOG.declare(
    "political_credit_column_3_line_3", Decimal, non_negative=True
)
"""Political contribution credit column 3 line 3, Worksheet ON479 "Column 3: Line 63110 is more than
$1,666.82", line 3 "Line 1 minus line 2 (cannot be negative)": the contributions less line 2, not
below zero."""

POLITICAL_CREDIT_COLUMN_3_LINE_5 = CATALOG.declare(
    "political_credit_column_3_line_5", Decimal, non_negative=True
)
"""Political contribution credit column 3 line 5, Worksheet ON479 "Column 3: Line 63110 is more than
$1,666.82", line 5 "Line 3 multiplied by the percentage from line 4": line 3 at the line 4 rate
of 33.33%."""

POLITICAL_CREDIT_COLUMN_3_LINE_6 = CATALOG.declare(
    "political_credit_column_3_line_6", Decimal, non_negative=True
)
"""Political contribution credit column 3 line 6, Worksheet ON479 "Column 3: Line 63110 is more than
$1,666.82", line 6 "958.41": a printed constant."""

POLITICAL_CREDIT_COLUMN_3_LINE_7 = CATALOG.declare(
    "political_credit_column_3_line_7", Decimal, non_negative=True
)
"""Political contribution credit column 3 line 7, Worksheet ON479 "Column 3: Line 63110 is more than
$1,666.82", line 7 "Line 5 plus line 6 Enter this amount on line 16 of your Form ON479.": line 5
plus line 6."""

POLITICAL_CREDIT_BEFORE_MAXIMUM = CATALOG.declare(
    "political_credit_before_maximum", Decimal, non_negative=True
)
"""Political contribution credit before its maximum, Worksheet ON479 "Line 16 - Ontario political
contribution tax credit" line 7 "Enter this amount on line 16 of your Form ON479.": the line 7 of
the column that applies, column 1 if line 63110 is $500.05 or less, column 2 if it is more than
$500.05 but not more than $1,666.82, column 3 if it is more than $1,666.82."""

POLITICAL_CREDIT = CATALOG.declare("political_credit", Decimal, non_negative=True)
"""Ontario political contribution tax credit, Form ON479 line 16 "Enter $1,666.82 if your total
contributions are $3,793 or more. If not, use Worksheet ON479. (maximum $1,666.82)": the worksheet's
line 7, at most $1,666.82."""

FLOW_THROUGH_SHARE_SLIP_EXPENSES = CATALOG.declare(
    "flow_through_share_slip_expenses", Decimal, non_negative=True
)
"""Qualifying expenses of one slip, Form T1221 lines 1 to 3 "Enter the amount of qualifying
expenses.": the amounts from boxes 145 and 155 of a T101 slip or boxes 200 and 244 of a T5013 slip,
one line for each corporation or slip, taken as entered. The identification number the form asks
for beside it is not a field, as it feeds no calculation."""

FLOW_THROUGH_SHARE_SLIPS = RecordListKind.declare(
    CATALOG, "flow_through_share_slips", fields=(FLOW_THROUGH_SHARE_SLIP_EXPENSES,)
)
"""Slips for the focused flow-through share credit, Form T1221 lines 1 to 3 "Use a separate line to
enter the identification number for each corporation ... and the amounts from boxes 145 and 155 of
your T101 slips, or boxes 200 and 244 of your T5013 slips": one record for each slip, in the order
entered. A list may be empty."""

FLOW_THROUGH_SHARE_EXPENSES = CATALOG.declare(
    "flow_through_share_expenses", Decimal, non_negative=True
)
"""Total expenses of the flow-through share slips, Form T1221 line 4 "Add lines 1 to 3. Enter this
amount on line 63220 of your Form ON479.": the qualifying expenses of every slip, added."""

FLOW_THROUGH_SHARE_CLAIMABLE = CATALOG.declare(
    "flow_through_share_claimable", int, non_negative=True
)
"""Whether the focused flow-through share credit may be claimed, Form T1221 "You must be a resident
of Ontario on the last day of the tax year to claim this credit.": 0 when the filer was not a
resident of Ontario on the last day of the tax year, else 1."""

FLOW_THROUGH_SHARE_EXPENSES_CLAIMED = CATALOG.declare(
    "flow_through_share_expenses_claimed", Decimal, non_negative=True
)
"""Total expenses of the flow-through share slips entered on Form ON479 line 17 and line 63220, Form
T1221 line 4 for a filer who may claim the credit, else 0."""

FLOW_THROUGH_SHARE_CREDIT = CATALOG.declare("flow_through_share_credit", Decimal, non_negative=True)
"""Focused flow-through share credit, Form ON479 line 17 and line 63220 "Enter your total expenses
from your Form T1221. multiplied by 5% =": the 5% on the total expenses of the slips."""

COOP_EDUCATION_PAYROLL = CATALOG.declare("coop_education_payroll", Decimal, non_negative=True)
"""Total salaries and wages paid in the 2024 taxation year, Worksheet ON479 "Line 20 - Ontario
co-operative education tax credit" line 4: a starting amount, taken as entered."""

COOP_EDUCATION_PAYROLL_THRESHOLD = CATALOG.declare(
    "coop_education_payroll_threshold", Decimal, non_negative=True
)
"""Worksheet ON479 "Line 20" line 5 "400,000.00": the dataset's amount as an artifact."""

COOP_EDUCATION_PAYROLL_OVER_THRESHOLD = CATALOG.declare(
    "coop_education_payroll_over_threshold", Decimal, non_negative=True
)
"""Worksheet ON479 "Line 20" line 6 "Line 4 minus line 5 (if negative, enter "0") =": the payroll
over $400,000, not below zero."""

COOP_EDUCATION_PAYROLL_RANGE = CATALOG.declare(
    "coop_education_payroll_range", Decimal, non_negative=True
)
"""Worksheet ON479 "Line 20" line 7 "200,000.00": the dataset's amount as an artifact."""

COOP_EDUCATION_PHASE_OUT_SHARE = CATALOG.declare(
    "coop_education_phase_out_share", Decimal, non_negative=True
)
"""Worksheet ON479 "Line 20" line 8 "Line 6 divided by line 7 =", which line 10 "Amount from line 8
above" repeats: an exact fraction, never rounded."""

COOP_EDUCATION_FULL_SHARE = CATALOG.declare("coop_education_full_share", Decimal, non_negative=True)
"""Worksheet ON479 "Line 20" line 9 "1.00": the dataset's amount as an artifact."""

COOP_EDUCATION_REMAINING_SHARE = CATALOG.declare(
    "coop_education_remaining_share", Decimal, non_negative=True
)
"""Worksheet ON479 "Line 20" line 11 "Line 9 minus line 10 (if negative, enter "0") =": the share
of the 5% that remains."""

COOP_EDUCATION_PLACEMENT_EXPENDITURES = CATALOG.declare(
    "coop_education_placement_expenditures", Decimal, non_negative=True
)
"""Eligible expenditures of one work placement, Worksheet ON479 "Line 20" line 1 "Amount of
eligible expenditures (Note 1) incurred in 2025 Line A": already reduced by government assistance
as Note 1 asks, taken as entered."""

COOP_EDUCATION_PLACEMENTS = RecordListKind.declare(
    CATALOG, "coop_education_placements", fields=(COOP_EDUCATION_PLACEMENT_EXPENDITURES,)
)
"""Qualifying work placements, Worksheet ON479 "Line 20" "complete this chart for each qualifying
work placement": one record for each placement, in the order entered. A list may be empty."""

COOP_EDUCATION_PLACEMENT_COUNT = CATALOG.declare(
    "coop_education_placement_count", int, non_negative=True
)
"""Number of work placements, Form ON479 line 63260 "Number of eligible work placements your
business or partnership is claiming under the Ontario co-operative education tax credit program":
the placements in the list."""

COOP_CLAIMED_AS_PARTNERSHIP_MEMBER = CATALOG.declare(
    "coop_claimed_as_partnership_member", int, non_negative=True
)
"""Whether the credit is claimed as a member of a partnership, Form ON479 line 63265 "Are you
claiming this credit as a member of a partnership? 1 Yes or 2 No": a yes/no answer, taken as a
count, 0 for no and 1 for yes."""

COOP_PARTNERSHIP_BUSINESS_NUMBER = DigitsKind.declare(
    CATALOG, "coop_partnership_business_number", digits=9
)
"""Business number of the partnership, Form ON479 line 63270 "If yes, enter your nine-digit
business number. (enter 9 digits)": nine digits as entered, blank when the answer on line 63265 is
no."""

COOP_EDUCATION_CREDIT = CATALOG.declare("coop_education_credit", Decimal, non_negative=True)
"""Co-operative education credit, Form ON479 line 20 and line 63300 "Enter the total amount claimed
for all qualifying work placements. (maximum $3,000 per student)": the total of the placements'
Worksheet ON479 line 13, each at most $3,000."""

ONTARIO_CREDITS_SUBTOTAL = CATALOG.declare("ontario_credits_subtotal", Decimal, non_negative=True)
"""Ontario credits subtotal, Form ON479 line 18 "Add lines 1, 2, 13, 14, 16, and 17. =": here
lines 1, 2, 13, 14, 16 and 17, in line order. Line 19 "Amount from line 18 of the previous page"
carries it."""

ONTARIO_CREDITS = CATALOG.declare("ontario_credits", Decimal, non_negative=True)
"""Ontario credits, Form ON479 line 21 "Line 19 plus line 20 Enter this amount online 47900 of
your return. Ontario credits =": line 19 "Amount from line 18 of the previous page", which carries
line 18.

Line 20 is the co-operative education credit."""

REFUND_BEFORE_DONATION = CATALOG.declare("refund_before_donation", Decimal, non_negative=True)
"""Refund before the donation, Ontario opportunities fund line 1 "Amount from line 48400 above":
the refund."""

OPPORTUNITIES_FUND_DONATION = CATALOG.declare(
    "opportunities_fund_donation", Decimal, non_negative=True
)
"""Donation to the Ontario opportunities fund, line 2 and line 46500 "Your donation to the Ontario
opportunities fund": the part of the refund the filer gives, as entered."""

OPPORTUNITIES_FUND_DONATION_CHECKED = CATALOG.declare(
    "opportunities_fund_donation_checked", Decimal, non_negative=True
)
"""Donation after the check, Ontario opportunities fund line 2 and line 46500 "Your donation to the
Ontario opportunities fund": the donation as entered after the check that it is not more than
`ca-on/refund_before_donation` (line 1 "Amount from line 48400 above"; the form says "donate some or
all of your 2025 tax refund") (`core/at_most`). The subtraction reads this amount."""

NET_REFUND = CATALOG.declare("net_refund", Decimal, non_negative=True)
"""Net refund, Ontario opportunities fund line 3 and line 46600 "Net refund (line 1 minus line
2) =": line 1 less line 2."""

APPLIES_FOR_ENERGY_AND_PROPERTY_TAX_CREDIT = CATALOG.declare(
    "applies_for_energy_and_property_tax_credit", int, non_negative=True
)
"""Whether the filer applies for the 2026 Ontario energy and property tax credit, Form ON-BEN line
61020 "If you met any of these conditions and are applying for the 2026 OEPTC, tick this box and
complete Part A and Part B of this form.": a tick box, taken as a count, 0 or 1."""

APPLIES_FOR_NORTHERN_ENERGY_CREDIT = CATALOG.declare(
    "applies_for_northern_energy_credit", int, non_negative=True
)
"""Whether the filer applies for the 2026 Northern Ontario energy credit, Form ON-BEN line 61040 "If
you met any of these conditions and are applying for the 2026 NOEC, tick this box and complete Part
A and Part B of this form.": a tick box, taken as a count, 0 or 1."""

CHOOSES_SINGLE_BENEFIT_PAYMENT = CATALOG.declare(
    "chooses_single_benefit_payment", int, non_negative=True
)
"""Whether the filer chooses the delayed single payment, Form ON-BEN line 61060 "By ticking this
box, you are choosing to wait until June 2027 to get your 2026 OTB entitlement.": a tick box, taken
as a count, 0 or 1."""

APPLIES_FOR_SENIOR_HOMEOWNERS_GRANT = CATALOG.declare(
    "applies_for_senior_homeowners_grant", int, non_negative=True
)
"""Whether the filer applies for the 2026 Ontario senior homeowners' property tax grant, Form ON-BEN
line 61070 "If you met the conditions above and are applying for the 2026 OSHPTG, tick this box.":
a tick box, taken as a count, 0 or 1."""

SEPARATE_RESIDENCES_FOR_MEDICAL_REASONS = CATALOG.declare(
    "separate_residences_for_medical_reasons", int, non_negative=True
)
"""Whether the filer and the spouse or common-law partner occupied separate principal residences for
medical reasons, Form ON-BEN line 61080 "If, on December 31, 2025, you and your spouse or
common-law partner occupied separate principal residences for medical reasons and you are choosing
to apply individually for the OEPTC, NOEC, or OSHPTG, tick this box ...": a tick box, taken as a
count, 0 or 1."""

SEPARATE_RESIDENCES_FOR_MEDICAL_REASONS_CHECKED = CATALOG.declare(
    "separate_residences_for_medical_reasons_checked", int, non_negative=True
)
"""Separate principal residences for medical reasons, Form ON-BEN line 61080 "If, on December 31,
2025, you and your spouse or common-law partner occupied separate principal residences for medical
reasons ... tick this box": the answer of `ca-on/separate_residences_for_medical_reasons` after the
check that it is 0 or 1 (`ca/yes_or_no_count`), a count of 1 or 0. A count of 2 or more is refused,
not capped."""

SPOUSE_FOR_SEPARATE_RESIDENCES_CHECKED = CATALOG.declare(
    "spouse_for_separate_residences_checked", int, non_negative=True
)
"""Spouse or common-law partner for separate principal residences for medical reasons, Form ON-BEN
line 61080 "If, on December 31, 2025, you and your spouse or common-law partner occupied separate
principal residences for medical reasons ... tick this box": the spouse or common-law partner
count of `ca/spouse_or_common_law_partner_on_december_31_total` (T1 "Marital status on December
31, 2025" Box 1 Married, Box 2 Living common-law), passed on unchanged when it is at least the
checked line 61080 tick (`ca/count_at_least`). A tick of 1 with no spouse or common-law partner is
refused, not capped."""

RENT_PAID = CATALOG.declare("rent_paid", Decimal, non_negative=True)
"""Rent paid for the principal residence, Form ON-BEN line 61100 "Enter the total amount of rent
paid for your principal residence (including a private long-term care home) in Ontario for 2025.": a
starting amount, as the form takes it."""

PROPERTY_TAX_PAID = CATALOG.declare("property_tax_paid", Decimal, non_negative=True)
"""Property tax paid for the principal residence, Form ON-BEN line 61120 "Enter the total amount of
property tax paid for your principal residence in Ontario for 2025.": a starting amount, as the
form takes it."""

LIVED_IN_STUDENT_RESIDENCE = CATALOG.declare("lived_in_student_residence", int, non_negative=True)
"""Whether the filer resided in a designated student residence, Form ON-BEN line 61140 "If you
resided in a designated student residence in Ontario in 2025, tick this box.": a tick box, taken as
a count, 0 or 1."""

RESERVE_HOME_ENERGY_COSTS = CATALOG.declare("reserve_home_energy_costs", Decimal, non_negative=True)
"""Home energy costs paid for the principal residence on a reserve, Form ON-BEN line 61210 "If you
lived on a reserve, enter the total amount of home energy costs (like electricity and heat) paid
for your principal residence in Ontario for 2025.": a starting amount, as the form takes it."""

PUBLIC_LONG_TERM_CARE_PAID = CATALOG.declare(
    "public_long_term_care_paid", Decimal, non_negative=True
)
"""Accommodation paid in a public or non-profit long-term care home, Form ON-BEN line 61230 "Enter
the total amount paid for your accommodation in a public long-term care home or non-profit long-term
care home in Ontario for 2025.": a starting amount, as the form takes it."""

ON_BEN_RESIDENCE_MONTHS = CATALOG.declare("on_ben_residence_months", Decimal, non_negative=True)
"""Months in one residence, Form ON-BEN Part B column 3 "Number of months resident in 2025": a
starting amount of months, as the form takes it."""

ON_BEN_RESIDENCE_AMOUNT = CATALOG.declare("on_ben_residence_amount", Decimal, non_negative=True)
"""Amount paid for one residence, Form ON-BEN Part B column 4 "Amount paid for 2025": the rent,
property tax, home energy costs on a reserve or long-term care accommodation, as entered."""

ON_BEN_RESIDENCE_LONG_TERM_CARE = CATALOG.declare(
    "on_ben_residence_long_term_care", int, non_negative=True
)
"""Whether one residence is a long-term care home, Form ON-BEN Part B column 5 "Tick this box if it
is a long-term care home": a tick box, taken as a count, 0 or 1."""

ON_BEN_RESIDENCE_LONG_TERM_CARE_CHECKED = CATALOG.declare(
    "on_ben_residence_long_term_care_checked", int, non_negative=True
)
"""Whether one residence is a long-term care home, Form ON-BEN Part B column 5: the answer of
`ca-on/on_ben_residence_long_term_care` after the check that it is 0 or 1 (`ca/yes_or_no_count`).
A count of 2 or more is refused, not capped."""

ON_BEN_RESIDENCES = RecordListKind.declare(
    CATALOG,
    "on_ben_residence_rows",
    fields=(ON_BEN_RESIDENCE_MONTHS, ON_BEN_RESIDENCE_AMOUNT, ON_BEN_RESIDENCE_LONG_TERM_CARE),
)
"""Principal residences, Form ON-BEN Part B "I declare the following information about my principal
residences in Ontario during 2025": one record for each row of the table, in the order entered, any
number (the form's table has four entries and says to use a separate sheet for more). The address,
postal code and name columns are text and feed no calculation, so they are not fields. A list may
be empty."""

ON_BEN_MONTHS_IN_YEAR = CATALOG.declare("on_ben_months_in_year", Decimal, non_negative=True)
"""Months in the year, the most the months of one row of Form ON-BEN Part B column 3 may be: the
`on_ben_months_in_year` dataset as an artifact. The form does not print the 12."""

ON_BEN_RESIDENCE_MONTHS_CHECKED = CATALOG.declare(
    "on_ben_residence_months_checked", Decimal, non_negative=True
)
"""Months of one row, Form ON-BEN Part B column 3 "Number of months resident in 2025": the row's
months, passed on unchanged when they are at most the months in the year (`core/at_most`). More
than 12 in a row is refused, not capped. Rows are not added: a home with rent, property tax and
energy costs paid to different payees takes one row for each, each with the same months."""
