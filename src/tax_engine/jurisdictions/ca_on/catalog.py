"""The Ontario artifact catalog: Ontario's own kinds, named from the Ontario forms.

Amounts are `Decimal`, non-negative unless the form prints no floor. Federal kinds come from
`tax_engine.jurisdictions.ca.catalog`; identifiers are stable.
"""

from __future__ import annotations

from tax_engine.domain.artifact import ArtifactCatalog
from tax_engine.domain.kinds import AmountKind, CountKind
from tax_engine.domain.registry import Namespace
from tax_engine.jurisdictions.ca_on import NAMESPACE

CATALOG = ArtifactCatalog(Namespace(NAMESPACE))

BASIC_PERSONAL_AMOUNT = AmountKind.declare(CATALOG, "basic_personal_amount", non_negative=True)
"""Basic personal amount, ON428 line 9 (line 58040) "Basic personal amount Claim $12,747": the
amount claimed, the first part of the total of the Ontario credit amounts."""

ON428_TAXABLE_INCOME_LINE_1 = AmountKind.declare(
    CATALOG, "on428_taxable_income_line_1", non_negative=True
)
"""Taxable income, ON428 line 1 "Enter your taxable income from line 26000 of your return.": the
T1 taxable income, the base of the Part A bracket columns."""

ON428_BRACKET_LOWER_BOUND_LINE_3 = AmountKind.declare(
    CATALOG, "on428_bracket_lower_bound_line_3", non_negative=True
)
"""Bracket lower bound, ON428 line 3 (each column prints "Line 3:" with 0.00, 52,886.00, 105,775.00,
150,000.00 or 220,000.00): the printed lower bound of the column that line 1 falls in."""

ON428_TAX_AT_COLUMN_START_LINE_7 = AmountKind.declare(
    CATALOG, "on428_tax_at_column_start_line_7", non_negative=True
)
"""Tax at the column's start, ON428 line 7 (each column prints "Line 7:" with 0.00, 2,670.74,
7,510.09, 12,445.60 or 20,957.60): the printed tax at the start of the column that line 1 falls
in."""

ON428_TAXABLE_INCOME_OVER_LOWER_BOUND_LINE_4 = AmountKind.declare(
    CATALOG, "on428_taxable_income_over_lower_bound_line_4", non_negative=True
)
"""Taxable income over the lower bound, ON428 line 4 "Line 4: Line 2 minus line 3 (cannot be
negative) =": line 1 minus line 3, not below zero."""

ON428_BRACKET_COLUMN_RATE_LINE_5 = AmountKind.declare(
    CATALOG, "on428_bracket_column_rate_line_5", non_negative=True
)
"""Bracket column rate, ON428 line 5 (each column prints "Line 5: Rate" with 5.05%, 9.15%, 11.16%,
12.16% or 13.16%): the printed rate of the column that line 1 falls in."""

ON428_EXCESS_TIMES_COLUMN_RATE_LINE_6 = AmountKind.declare(
    CATALOG, "on428_excess_times_column_rate_line_6", non_negative=True
)
"""Line 4 times the column rate, ON428 line 6 "Line 6: Line 4 multiplied by the percentage from
line 5 =": line 4 times line 5, a fraction, rounded half-up to the cent."""

ON428_PERSONAL_AMOUNTS_SUBTOTAL_LINE_18 = AmountKind.declare(
    CATALOG, "on428_personal_amounts_subtotal_line_18", non_negative=True
)
"""Personal amounts subtotal, ON428 line 18 "Add lines 9, 10, 13, 16, and 17.": the sum of lines
9, 10, 13, 16 and 17."""

ON428_CPP_EI_CREDIT_AMOUNTS_LINE_24 = AmountKind.declare(
    CATALOG, "on428_cpp_ei_credit_amounts_line_24", non_negative=True
)
"""CPP and EI credit amounts subtotal, ON428 line 24 "Add lines 19 to 23.": the sum of lines 19
to 23."""

ON428_CREDITS_SUBTOTAL_LINE_25 = AmountKind.declare(
    CATALOG, "on428_credits_subtotal_line_25", non_negative=True
)
"""Credits subtotal, ON428 line 25 "Line 18 plus line 24 =": line 18 plus line 24."""

ON428_AGE_65_OR_OLDER = CountKind.declare(CATALOG, "on428_age_65_or_older", non_negative=True)
"""Aged 65 or older at the end of the year, read from the T1's `ca/age_65_or_older` (worked out once
there from the year of birth) for ON428 line 10: 1 or 0, blank when the year is blank."""

WORKSHEET_ON428_AGE_AMOUNT_MAXIMUM_LINE_1 = AmountKind.declare(
    CATALOG, "worksheet_on428_age_amount_maximum_line_1", non_negative=True
)
"""Worksheet ON428 age amount line 1 "Maximum amount 6,223.00"."""

WORKSHEET_ON428_AGE_AMOUNT_NET_INCOME_LINE_2 = AmountKind.declare(
    CATALOG, "worksheet_on428_age_amount_net_income_line_2", non_negative=True
)
"""Worksheet ON428 age amount line 2 "Amount from line 23600 of your return"."""

WORKSHEET_ON428_AGE_AMOUNT_INCOME_THRESHOLD_LINE_3 = AmountKind.declare(
    CATALOG, "worksheet_on428_age_amount_income_threshold_line_3", non_negative=True
)
"""Worksheet ON428 age amount line 3 "Income threshold 46,330.00"."""

WORKSHEET_ON428_AGE_AMOUNT_LINE_4 = AmountKind.declare(
    CATALOG, "worksheet_on428_age_amount_line_4", non_negative=True
)
"""Worksheet ON428 age amount line 4 "Line 2 minus line 3 (if negative, enter \"0\")"."""

WORKSHEET_ON428_AGE_AMOUNT_LINE_6 = AmountKind.declare(
    CATALOG, "worksheet_on428_age_amount_line_6", non_negative=True
)
"""Worksheet ON428 age amount line 6 "Line 4 multiplied by the percentage from line 5"."""

WORKSHEET_ON428_AGE_AMOUNT_LINE_7 = AmountKind.declare(
    CATALOG, "worksheet_on428_age_amount_line_7", non_negative=True
)
"""Worksheet ON428 age amount line 7 "Line 1 minus line 6 (if negative, enter \"0\")": the amount
for ON428 line 10 when the filer was born in 1960 or earlier."""

ON428_AGE_AMOUNT_CLAIMED_LINE_10 = AmountKind.declare(
    CATALOG, "on428_age_amount_claimed_line_10", non_negative=True
)
"""ON428 line 10: worksheet line 7 when born in 1960 or earlier, 0.00 otherwise, before the check
against the printed maximum."""

ON428_AGE_AMOUNT_LINE_10 = AmountKind.declare(
    CATALOG, "on428_age_amount_line_10", non_negative=True
)
"""ON428 line 10 "Age amount (if you were born in 1960 or earlier) (use Worksheet ON428)
(maximum $6,223)": worksheet line 7 when born in 1960 or earlier, 0.00 otherwise."""

ON428_CREDITS_WITH_TRANSFERS_LINE_35 = AmountKind.declare(
    CATALOG, "on428_credits_with_transfers_line_35", non_negative=True
)
"""Total of the credits with the student loan, tuition and transfer amounts, ON428 line 35 "Add
lines 31 to 34.": the sum of line 31 with lines 32 to 34."""

ON428_MEDICAL_EXPENSES_LINE_36 = AmountKind.declare(
    CATALOG, "on428_medical_expenses_line_36", non_negative=True
)
"""Medical expenses, ON428 line 36 (line 58689) "See line 58689 at canada.ca/on-tax-info for maximum
allowable amounts for attendant care, an adapted van, and moving expenses": the amount as the filer
gives it, an optional input; a blank input is read as blank."""

ON428_ATTENDANT_CARE_EXPENSES_LINE_36 = AmountKind.declare(
    CATALOG, "on428_attendant_care_expenses_line_36", non_negative=True
)
"""Attendant care expenses, ON428, line 36 "See line 58689 at canada.ca/on-tax-info for maximum
allowable amounts for attendant care, an adapted van, and moving expenses": the
attendant care expenses paid (CRA 5006-PC, section "Line 58689"), an optional input; a blank
input is read as 0 by the line 36 steps."""

ON428_ADAPTED_VAN_EXPENSES_LINE_36 = AmountKind.declare(
    CATALOG, "on428_adapted_van_expenses_line_36", non_negative=True
)
"""Adapted van expenses, ON428, line 36 "See line 58689 at canada.ca/on-tax-info for maximum
allowable amounts for attendant care, an adapted van, and moving expenses": the amount of the
medical claim for a van adapted for transporting a patient who requires the use of a wheelchair,
which CRA Guide RC4065 "Medical Expenses" (PDF page 19) prints as "20% of the amount paid for a
van that has been previously adapted, or is adapted within 6 months after the van was bought
(minus the cost of adapting the van)", an optional input; a blank input is read as 0 by the line
36 steps."""

ON428_PATIENT_MOVE_EXPENSES_LINE_36 = AmountKind.declare(
    CATALOG, "on428_patient_move_expenses_line_36", non_negative=True
)
"""Patient move expenses, ON428, line 36 "See line 58689 at canada.ca/on-tax-info for maximum
allowable amounts for attendant care, an adapted van, and moving expenses": the amount of the
medical claim for reasonable moving expenses "(that have not been claimed as moving expenses on
anyone's tax return)" for a patient's move to a more accessible dwelling (CRA Guide RC4065
"Medical Expenses", PDF page 22), an optional input; a blank input is read as 0 by the line 36
steps."""

ON428_YEAR_OF_DEATH_LINE_36 = CountKind.declare(
    CATALOG, "on428_year_of_death_line_36", non_negative=True
)
"""Year of death, ON428, line 36 "See line 58689 at canada.ca/on-tax-info for maximum allowable
amounts for attendant care, an adapted van, and moving expenses": 1 when the attendant care
maximum is the one "in the year of death" ($35,253), 0 otherwise, an optional input; a blank
input is read as 0."""

ON428_YEAR_OF_DEATH_CHECKED_LINE_36 = CountKind.declare(
    CATALOG, "on428_year_of_death_checked_line_36", non_negative=True
)
"""Year of death, checked, ON428, line 36 "See line 58689 at canada.ca/on-tax-info for maximum
allowable amounts for attendant care, an adapted van, and moving expenses": the year of death
answer with a blank read as 0, refused above 1."""

ON428_ATTENDANT_CARE_PAID_LINE_36 = AmountKind.declare(
    CATALOG, "on428_attendant_care_paid_line_36", non_negative=True
)
"""Attendant care paid, ON428, line 36 "See line 58689 at canada.ca/on-tax-info for maximum
allowable amounts for attendant care, an adapted van, and moving expenses": the attendant care
expenses paid, a blank input read as 0."""

ON428_ADAPTED_VAN_READ_LINE_36 = AmountKind.declare(
    CATALOG, "on428_adapted_van_read_line_36", non_negative=True
)
"""Adapted van, ON428, line 36 "See line 58689 at canada.ca/on-tax-info for maximum allowable
amounts for attendant care, an adapted van, and moving expenses": the adapted van expenses, a
blank input read as 0."""

ON428_PATIENT_MOVE_READ_LINE_36 = AmountKind.declare(
    CATALOG, "on428_patient_move_read_line_36", non_negative=True
)
"""Patient move, ON428, line 36 "See line 58689 at canada.ca/on-tax-info for maximum allowable
amounts for attendant care, an adapted van, and moving expenses": the patient move expenses, a
blank input read as 0."""

ON428_ATTENDANT_CARE_AT_ORDINARY_MAXIMUM_LINE_36 = AmountKind.declare(
    CATALOG, "on428_attendant_care_at_ordinary_maximum_line_36", non_negative=True
)
"""Attendant care at the ordinary maximum, ON428, line 36 "See line 58689 at canada.ca/on-tax-
info for maximum allowable amounts for attendant care, an adapted van, and moving expenses": the
attendant care expenses limited to $17,627."""

ON428_ATTENDANT_CARE_AT_DEATH_MAXIMUM_LINE_36 = AmountKind.declare(
    CATALOG, "on428_attendant_care_at_death_maximum_line_36", non_negative=True
)
"""Attendant care at the year of death maximum, ON428, line 36 "See line 58689 at canada.ca/on-
tax-info for maximum allowable amounts for attendant care, an adapted van, and moving expenses":
the attendant care expenses limited to $35,253."""

ON428_ATTENDANT_CARE_ALLOWED_LINE_36 = AmountKind.declare(
    CATALOG, "on428_attendant_care_allowed_line_36", non_negative=True
)
"""Attendant care allowed, ON428, line 36 "See line 58689 at canada.ca/on-tax-info for maximum
allowable amounts for attendant care, an adapted van, and moving expenses": the ordinary or the
year of death figure, chosen by the checked year of death answer."""

ON428_ADAPTED_VAN_ALLOWED_LINE_36 = AmountKind.declare(
    CATALOG, "on428_adapted_van_allowed_line_36", non_negative=True
)
"""Adapted van allowed, ON428, line 36 "See line 58689 at canada.ca/on-tax-info for maximum
allowable amounts for attendant care, an adapted van, and moving expenses": the adapted van
expenses limited to $8,813."""

ON428_PATIENT_MOVE_ALLOWED_LINE_36 = AmountKind.declare(
    CATALOG, "on428_patient_move_allowed_line_36", non_negative=True
)
"""Patient move allowed, ON428, line 36 "See line 58689 at canada.ca/on-tax-info for maximum
allowable amounts for attendant care, an adapted van, and moving expenses": the patient move
expenses limited to $3,525."""

ON428_ATTENDANT_CARE_FEDERAL_LIMIT_APPLIED_LINE_36 = CountKind.declare(
    CATALOG, "on428_attendant_care_federal_limit_applied_line_36", non_negative=True
)
"""Attendant care federal limit applied, ON428, line 36 "See line 58689 at canada.ca/on-tax-info
for maximum allowable amounts for attendant care, an adapted van, and moving expenses": 1 when
the attendant care expenses in the medical claim "was limited to $10,000 ($20,000 in the year of
death)", 0 otherwise, an optional input; a blank input is read as 0."""

ON428_ATTENDANT_CARE_FEDERAL_LIMIT_APPLIED_CHECKED_LINE_36 = CountKind.declare(
    CATALOG, "on428_attendant_care_federal_limit_applied_checked_line_36", non_negative=True
)
"""Attendant care federal limit applied, checked, ON428, line 36 "See line 58689 at
canada.ca/on-tax-info for maximum allowable amounts for attendant care, an adapted van, and
moving expenses": the answer with a blank read as 0, refused above 1."""

ON428_ATTENDANT_CARE_AT_FEDERAL_ORDINARY_LIMIT_LINE_36 = AmountKind.declare(
    CATALOG, "on428_attendant_care_at_federal_ordinary_limit_line_36", non_negative=True
)
"""Attendant care at the federal limit, ON428, line 36 "See line 58689 at canada.ca/on-tax-info
for maximum allowable amounts for attendant care, an adapted van, and moving expenses": the
attendant care expenses paid limited to $10,000."""

ON428_ATTENDANT_CARE_AT_FEDERAL_DEATH_LIMIT_LINE_36 = AmountKind.declare(
    CATALOG, "on428_attendant_care_at_federal_death_limit_line_36", non_negative=True
)
"""Attendant care at the federal limit in the year of death, ON428, line 36 "See line 58689 at
canada.ca/on-tax-info for maximum allowable amounts for attendant care, an adapted van, and
moving expenses": the attendant care expenses paid limited to $20,000."""

ON428_ATTENDANT_CARE_FEDERAL_INCLUDED_LINE_36 = AmountKind.declare(
    CATALOG, "on428_attendant_care_federal_included_line_36", non_negative=True
)
"""Attendant care included in the federal claim, ON428, line 36 "See line 58689 at canada.ca/on-
tax-info for maximum allowable amounts for attendant care, an adapted van, and moving expenses":
the ordinary or the year of death federal figure, chosen by the checked year of death answer."""

ON428_ATTENDANT_CARE_ABOVE_FEDERAL_LINE_36 = AmountKind.declare(
    CATALOG, "on428_attendant_care_above_federal_line_36", non_negative=True
)
"""Attendant care above the federal claim, ON428, line 36 "See line 58689 at canada.ca/on-tax-
info for maximum allowable amounts for attendant care, an adapted van, and moving expenses": the
Ontario attendant care figure less the one included in the federal claim."""

ON428_ATTENDANT_CARE_INCREASE_LINE_36 = AmountKind.declare(
    CATALOG, "on428_attendant_care_increase_line_36", non_negative=True
)
"""Attendant care increase, ON428, line 36 "See line 58689 at canada.ca/on-tax-info for maximum
allowable amounts for attendant care, an adapted van, and moving expenses": the attendant care
above the federal claim when the federal claim was limited, else 0."""

ON428_ADAPTED_VAN_FEDERAL_INCLUDED_LINE_36 = AmountKind.declare(
    CATALOG, "on428_adapted_van_federal_included_line_36", non_negative=True
)
"""Adapted van included in the federal claim, ON428, line 36 "See line 58689 at
canada.ca/on-tax-info for maximum allowable amounts for attendant care, an adapted van, and
moving expenses": the adapted van
expenses limited to the federal figure ($5,000, CRA Guide RC4065 "Medical Expenses")."""

ON428_ADAPTED_VAN_INCREASE_LINE_36 = AmountKind.declare(
    CATALOG, "on428_adapted_van_increase_line_36", non_negative=True
)
"""Adapted van increase, ON428, line 36 "See line 58689 at canada.ca/on-tax-info for maximum
allowable amounts for attendant care, an adapted van, and moving expenses": the adapted van
expenses at the Ontario figure less the same expenses at the federal figure ($5,000, CRA Guide
RC4065 "Medical Expenses"), 0 up to the federal limit."""

ON428_PATIENT_MOVE_FEDERAL_INCLUDED_LINE_36 = AmountKind.declare(
    CATALOG, "on428_patient_move_federal_included_line_36", non_negative=True
)
"""Patient move included in the federal claim, ON428, line 36 "See line 58689 at
canada.ca/on-tax-info for maximum allowable amounts for attendant care, an adapted van, and
moving expenses": the patient move
expenses limited to the federal figure ($2,000, CRA Guide RC4065 "Medical Expenses")."""

ON428_PATIENT_MOVE_INCREASE_LINE_36 = AmountKind.declare(
    CATALOG, "on428_patient_move_increase_line_36", non_negative=True
)
"""Patient move increase, ON428, line 36 "See line 58689 at canada.ca/on-tax-info for maximum
allowable amounts for attendant care, an adapted van, and moving expenses": the patient move
expenses at the Ontario figure less the same expenses at the federal figure ($2,000, CRA Guide
RC4065 "Medical Expenses"), 0 up to the federal limit."""

ON428_MEDICAL_EXPENSES_ALLOWED_LINE_36 = AmountKind.declare(
    CATALOG, "on428_medical_expenses_allowed_line_36", non_negative=True
)
"""Medical expenses allowed, ON428, line 36 "See line 58689 at canada.ca/on-tax-info for maximum
allowable amounts for attendant care, an adapted van, and moving expenses": the medical claim
plus the attendant care increase, less the van and patient move excesses, the amount line 41
reads. A result below 0 is refused, not floored."""

ON428_NET_INCOME_LINE_37 = AmountKind.declare(
    CATALOG, "on428_net_income_line_37", non_negative=True
)
"""Net income, ON428 line 37 "Amount from line 23600 of your return": the T1 net income, read from
the T1 taxable income form."""

ON428_MEDICAL_EXPENSES_RATE_AMOUNT_LINE_39 = AmountKind.declare(
    CATALOG, "on428_medical_expenses_rate_amount_line_39", non_negative=True
)
"""Medical expenses threshold, ON428 line 39 "Line 37 multiplied by the percentage from line 38 =":
line 37 times the 3% of line 38."""

ON428_MEDICAL_EXPENSES_LIMITED_AMOUNT_LINE_40 = AmountKind.declare(
    CATALOG, "on428_medical_expenses_limited_amount_line_40", non_negative=True
)
"""Medical expenses threshold, limited, ON428 line 40 "Enter whichever is less: $2,885 or the amount
on line 39.": the lesser of the printed ceiling and line 39."""

ON428_MEDICAL_EXPENSES_OVER_LIMIT_LINE_41 = AmountKind.declare(
    CATALOG, "on428_medical_expenses_over_limit_line_41", non_negative=True
)
"""Medical expenses over the limit, ON428 line 41 "Line 36 minus line 40 (if negative, enter "0")
=": line 36 minus line 40, never below 0; a blank line 36 is read as 0."""

ON428_OTHER_DEPENDANTS_MEDICAL_EXPENSES_LINE_42 = AmountKind.declare(
    CATALOG, "on428_other_dependants_medical_expenses_line_42", non_negative=True
)
"""Allowable amount of medical expenses for other dependants, ON428 line 42 (line 58729) "(use
Worksheet ON428)": the amount as the filer gives it, an optional input; a blank input is read as
blank."""

ON428_MEDICAL_EXPENSES_LINE_43 = AmountKind.declare(
    CATALOG, "on428_medical_expenses_line_43", non_negative=True
)
"""Medical expenses, ON428 line 43 and line 58769 "Line 41 plus line 42 =": line 41 plus line 42
(a blank line 42 is read as 0), a part of line 44."""

ON428_TOTAL_CREDIT_AMOUNTS_LINE_44 = AmountKind.declare(
    CATALOG, "on428_total_credit_amounts_line_44", non_negative=True
)
"""Total credit amounts, ON428 line 44 "Line 44 and line 58800: Line 35 plus line 43 =": line 35
plus line 43."""

ON428_CREDIT_AMOUNTS_AT_CREDIT_RATE_LINE_46 = AmountKind.declare(
    CATALOG, "on428_credit_amounts_at_credit_rate_line_46", non_negative=True
)
"""Credit amounts at the credit rate, ON428 line 46 "Line 46 and line 58840: Line 44 multiplied by
the percentage from line 45 =": line 44 times the 5.05% of line 45."""

ON428_TAX_ON_TAXABLE_INCOME_LINE_8 = AmountKind.declare(
    CATALOG, "on428_tax_on_taxable_income_line_8", non_negative=True
)
"""Ontario tax on taxable income, ON428 line 8 "Line 6 plus line 7 Ontario tax on taxable income =":
line 6 plus line 7."""

ON428_SURTAX_36_PERCENT_TIER_LINE_67 = AmountKind.declare(
    CATALOG, "on428_surtax_36_percent_tier_line_67", non_negative=True
)
"""36% surtax tier, ON428 line 67 "(Line 65 minus $7,307) multiplied by 36% (if negative, enter
"0") =": 36% of line 65 above $7,307, never below 0."""

ON428_DONATIONS_AMOUNT_LINE_47 = AmountKind.declare(
    CATALOG, "on428_donations_amount_line_47", non_negative=True
)
"""Donations amount, ON428 line 47 box A "Amount from line 13 of your federal Schedule 9": the
amount, a record total of Schedule 9's export
(`ca/schedule_9.donations_and_gifts_line_13`), 0 for a salary-only caller."""

ON428_DONATIONS_CREDIT_AT_RATE_LINE_47 = AmountKind.declare(
    CATALOG, "on428_donations_credit_at_rate_line_47", non_negative=True
)
"""Donations credit at 5.05%, ON428 line 47 box B "Amount from line 13 of your federal Schedule 9
multiplied by 5.05% =": the Schedule 9 amount times 5.05%; a blank amount is read as 0."""

ON428_DONATIONS_AMOUNT_LINE_48 = AmountKind.declare(
    CATALOG, "on428_donations_amount_line_48", non_negative=True
)
"""Donations amount, ON428 line 48 box A "Amount from line 14 of your federal Schedule 9": the
amount, a record total of Schedule 9's export
(`ca/schedule_9.donations_and_gifts_line_14`), 0 for a salary-only caller."""

ON428_DONATIONS_CREDIT_AT_RATE_LINE_48 = AmountKind.declare(
    CATALOG, "on428_donations_credit_at_rate_line_48", non_negative=True
)
"""Donations credit at 11.16%, ON428 line 48 box B "Amount from line 14 of your federal Schedule 9
multiplied by 11.16% =": the Schedule 9 amount times 11.16%; a blank amount is read as 0."""

ON428_DONATIONS_CREDIT_LINE_49 = AmountKind.declare(
    CATALOG, "on428_donations_credit_line_49", non_negative=True
)
"""Donations and gifts credit, ON428 line 49 "Line 49 and line 58969: Line 47 plus line 48 =": line
47 plus line 48."""

ON428_NON_REFUNDABLE_CREDITS_LINE_50 = AmountKind.declare(
    CATALOG, "on428_non_refundable_credits_line_50", non_negative=True
)
"""Ontario non-refundable tax credits, ON428 line 50 "Line 50 and line 61500: Line 46 plus line 49":
line 46 (the credits at the rate) plus line 49 (the donations and gifts credit)."""

ON428_TAX_MINUS_CREDITS_LINE_53 = AmountKind.declare(
    CATALOG, "on428_tax_minus_credits_line_53", non_negative=True
)
"""Tax minus credits, ON428 line 53 "Line 51 minus line 52 (if negative, enter "0") =": line 8
(copied to line 51) minus line 50 (copied to line 52), not below 0."""

ON428_TAX_ON_SPLIT_INCOME_LINE_54 = AmountKind.declare(CATALOG, "on428_tax_on_split_income_line_54")
"""Ontario tax on split income, ON428 line 54 "Line 54 and line 61510: Ontario tax on split income
(complete Form T1206)": the tax from Form T1206."""

ON428_TAX_WITH_SPLIT_INCOME_LINE_55 = AmountKind.declare(
    CATALOG, "on428_tax_with_split_income_line_55"
)
"""Tax with split income, ON428 line 55 "Line 55: Line 53 plus line 54 =": line 53 plus line 54."""

ON428_TAX_MINUS_CREDITS_LINE_56 = AmountKind.declare(
    CATALOG, "on428_tax_minus_credits_line_56", non_negative=True
)
"""Tax minus credits copied, ON428 line 56 "Line 56: Enter the amount from line 53 above.": a copy
of line 53."""

ON428_TAX_MINUS_DIVIDEND_TAX_CREDIT_LINE_58 = AmountKind.declare(
    CATALOG, "on428_tax_minus_dividend_tax_credit_line_58", non_negative=True
)
"""Tax minus the dividend tax credit, ON428 line 58 "Line 58: Line 56 minus line 57 (if negative,
enter "0") =": line 56 minus line 57, not below zero."""

ON428_MINIMUM_TAX_CARRYOVER_AMOUNT_LINE_59 = AmountKind.declare(
    CATALOG, "on428_minimum_tax_carryover_amount_line_59", non_negative=True
)
"""Minimum tax carryover amount, ON428 line 59 "Line 59: Amount from line 40427 of your return":
the amount from line 40427 of the T1 return, a record total of the T1's export
(`ca/minimum_tax_carryover_line_40427`), 0 for a salary-only caller; the 24.63% is applied by the
next step."""

ON428_MINIMUM_TAX_CARRYOVER_LIMIT_LINE_59 = AmountKind.declare(
    CATALOG, "on428_minimum_tax_carryover_limit_line_59", non_negative=True
)
"""Minimum tax carryover limit, ON428 line 59 "Line 59: Amount from line 40427 of your return
multiplied by 24.63% =": calculated, the amount from line 40427 multiplied by 24.63%."""

ON428_MINIMUM_TAX_CARRYOVER_LINE_60 = AmountKind.declare(
    CATALOG, "on428_minimum_tax_carryover_line_60", non_negative=True
)
"""Minimum tax carryover applied, ON428 line 60 "Line 60 and line 61540: Enter whichever is less:
amount from line 58 or line 59.": the lesser of line 58 and line 59."""

ON428_TAX_AFTER_MINIMUM_TAX_CARRYOVER_LINE_61 = AmountKind.declare(
    CATALOG, "on428_tax_after_minimum_tax_carryover_line_61", non_negative=True
)
"""Ontario tax after the minimum tax carryover, ON428 line 61 "Line 61: Line 55 minus line 60 (if
negative, enter "0") =": line 55 minus line 60, not below zero."""

ON428_SURTAX_BASE_LINE_65 = AmountKind.declare(
    CATALOG, "on428_surtax_base_line_65", non_negative=True
)
"""Surtax base, ON428 line 65 "Line 65: Line 63 minus line 64 (if negative, enter "0") =": line 61
less line 54, never below zero."""

ON428_SURTAX_20_PERCENT_TIER_LINE_66 = AmountKind.declare(
    CATALOG, "on428_surtax_20_percent_tier_line_66", non_negative=True
)
"""Surtax 20% tier, ON428 line 66 "(Line 65 minus $5,710) multiplied by 20% (if negative, enter
"0") =": 20% of line 65 above $5,710, never below 0."""

ON428_SURTAX_TOTAL_LINE_68 = AmountKind.declare(
    CATALOG, "on428_surtax_total_line_68", non_negative=True
)
"""Ontario surtax, ON428 line 68 "Line 66 plus line 67 =": line 66 plus line 67."""

ON428_DIVIDEND_TAX_CREDIT_LINE_57 = AmountKind.declare(
    CATALOG, "on428_dividend_tax_credit_line_57", non_negative=True
)
"""Ontario dividend tax credit, ON428 line 57 "Line 57 and line and line 61520: Ontario dividend tax
credit (use Worksheet ON428)": computed from Worksheet ON428 (5006-D), the sum of its line 1 and
line 2 over the T1 lines 12000 and 12010. A caller who gives neither line has a credit of 0.00."""

ON428_DIVIDEND_TAX_CREDIT_WORKSHEET_LINE_A = AmountKind.declare(
    CATALOG, "on428_dividend_tax_credit_worksheet_line_a", non_negative=True
)
"""Ontario dividend tax credit worksheet, ON428 line 57 (Worksheet ON428, 5006-D), Line A "Amount
from line 12000 of your return": the T1 line 12000 total."""

ON428_DIVIDEND_TAX_CREDIT_WORKSHEET_LINE_B = AmountKind.declare(
    CATALOG, "on428_dividend_tax_credit_worksheet_line_b", non_negative=True
)
"""Ontario dividend tax credit worksheet, ON428 line 57 (Worksheet ON428, 5006-D), Line B "Amount
from line 12010 of your return": the T1 line 12010 total."""

ON428_DIVIDEND_TAX_CREDIT_WORKSHEET_LINE_1 = AmountKind.declare(
    CATALOG, "on428_dividend_tax_credit_worksheet_line_1", non_negative=True
)
"""Ontario dividend tax credit worksheet, ON428 line 57 (Worksheet ON428, 5006-D), Line 1 "Amount
from line 12010 of your return Line B multiplied by 2.9863% =": line B at the first printed rate,
rounded half-up to the cent."""

ON428_DIVIDEND_TAX_CREDIT_WORKSHEET_LINE_C = AmountKind.declare(
    CATALOG, "on428_dividend_tax_credit_worksheet_line_c", non_negative=True
)
"""Ontario dividend tax credit worksheet, ON428 line 57 (Worksheet ON428, 5006-D), Line C "Amount A
minus amount B": line A less line B."""

ON428_DIVIDEND_TAX_CREDIT_WORKSHEET_LINE_2 = AmountKind.declare(
    CATALOG, "on428_dividend_tax_credit_worksheet_line_2", non_negative=True
)
"""Ontario dividend tax credit worksheet, ON428 line 57 (Worksheet ON428, 5006-D), Line 2 "Amount A
minus amount B Line C = multiplied by 10% =": line C at the second printed rate, rounded half-up to
the cent."""

ON428_TAX_WITH_SURTAX_LINE_69 = AmountKind.declare(
    CATALOG, "on428_tax_with_surtax_line_69", non_negative=True
)
"""ON428 line 69 "Line 69: Line 62 plus line 68 =": line 61 plus line 68."""

ON428_BASIC_REDUCTION_LINE_74 = AmountKind.declare(
    CATALOG, "on428_basic_reduction_line_74", non_negative=True
)
"""Basic reduction, ON428 line 74 "Basic reduction 294.00": the amount claimed, the first part of
line 77."""

ON428_TAX_AFTER_DIVIDEND_CREDIT_LINE_71 = AmountKind.declare(
    CATALOG, "on428_tax_after_dividend_credit_line_71", non_negative=True
)
"""Ontario tax after the dividend tax credit, ON428 line 71 "Line 71: Line 69 minus line 70 (if
negative, enter "0") =": line 69 minus the dividend tax credit, not below zero."""

ON428_WORKSHEET_T691_AMOUNT_LINE_1 = AmountKind.declare(
    CATALOG, "on428_worksheet_t691_amount_line_1", non_negative=True
)
"""Amount from line 11 of Part 5 of Form T691, Worksheet ON428 (line 72) line 1 "Amount from line
11 of Part 5 of your Form T691": a record total of the T691's export
(`ca/t691_part_5_line_11_amount`); the 24.63% is applied by the next step."""

ON428_WORKSHEET_BASIC_ADDITIONAL_TAX_LINE_1 = AmountKind.declare(
    CATALOG, "on428_worksheet_basic_additional_tax_line_1", non_negative=True
)
"""Ontario basic additional tax, Worksheet ON428 (line 72) line 1 "multiplied by 24.63% =": the
amount from line 11 of Part 5 of Form T691 multiplied by 24.63%."""

ON428_WORKSHEET_SURTAX_BASE_LINE_3 = AmountKind.declare(
    CATALOG, "on428_worksheet_surtax_base_line_3", non_negative=True
)
"""Surtax base on the additional tax, Worksheet ON428 (line 72) line 3 "Line 1 plus line 2 =": line
1 plus line 2, where line 2 is the amount from line 65 of Form ON428."""

ON428_WORKSHEET_SURTAX_20_PERCENT_TIER_LINE_4 = AmountKind.declare(
    CATALOG, "on428_worksheet_surtax_20_percent_tier_line_4", non_negative=True
)
"""Worksheet ON428 (line 72) line 4 "(Line 3 Minus $5,710) multiplied by 20% (if negative, enter
"0") =": 20% of line 3 above $5,710, never below 0."""

ON428_WORKSHEET_SURTAX_36_PERCENT_TIER_LINE_5 = AmountKind.declare(
    CATALOG, "on428_worksheet_surtax_36_percent_tier_line_5", non_negative=True
)
"""Worksheet ON428 (line 72) line 5 "(Line 3 Minus $7,307) multiplied by 36% (if negative, enter
"0") =": 36% of line 3 above $7,307, never below 0."""

ON428_WORKSHEET_SURTAX_TOTAL_LINE_6 = AmountKind.declare(
    CATALOG, "on428_worksheet_surtax_total_line_6", non_negative=True
)
"""Worksheet ON428 (line 72) line 6 "Line 4 plus line 5 =": line 4 plus line 5."""

ON428_WORKSHEET_SURTAX_ON_ADDITIONAL_TAX_LINE_8 = AmountKind.declare(
    CATALOG, "on428_worksheet_surtax_on_additional_tax_line_8"
)
"""Ontario surtax on additional tax, Worksheet ON428 (line 72) line 8 "Line 6 minus line 7 =":
line 6 less line 7 (the amount from line 68 of Form ON428). The worksheet prints no floor, so the
kind is signed."""

ON428_ADDITIONAL_TAX_FOR_MINIMUM_TAX_LINE_72 = AmountKind.declare(
    CATALOG, "on428_additional_tax_for_minimum_tax_line_72", non_negative=True
)
"""Additional tax for minimum tax purposes, ON428 line 72 "Line 72: If you entered an amount on line
11 of Part 5 of Form T691, use Worksheet ON428 to calculate your additional tax for minimum tax
purposes": calculated by Worksheet ON428 line 9 "Line 1 plus line 8", the basic additional tax plus
the surtax on it."""

ON428_TAX_WITH_MINIMUM_TAX_ADDITION_LINE_73 = AmountKind.declare(
    CATALOG, "on428_tax_with_minimum_tax_addition_line_73", non_negative=True
)
"""Tax with the minimum tax addition, ON428 line 73 "Line 73: Line 71 plus line 72 =": line 71 plus
line 72."""

ON428_TAX_REDUCTION_LINE_77 = AmountKind.declare(
    CATALOG, "on428_tax_reduction_line_77", non_negative=True
)
"""Tax reduction, ON428 line 77 "Add lines 74 to 76": the sum of the reduction parts, which for a
single filer with no dependants is the basic reduction on line 74 alone."""

ON428_TAX_REDUCTION_DOUBLED_LINE_78 = AmountKind.declare(
    CATALOG, "on428_tax_reduction_doubled_line_78", non_negative=True
)
"""Doubled tax reduction, ON428 line 78 "Amount from line 77 above multiplied by 2 =": line 77
multiplied by 2."""

ON428_TAX_REDUCTION_BEFORE_CONDITIONS_LINE_80 = AmountKind.declare(
    CATALOG, "on428_tax_reduction_before_conditions_line_80", non_negative=True
)
"""Ontario tax reduction before the conditions, ON428 line 80 "Line 80: Line 78 minus line 79 (if
negative, enter "0") Ontario tax reduction =": line 78 minus line 79 (a copy of line 73), not below
zero, before the printed "Enter "0" on line 80 if any of the following applies to you" rule."""

ON428_TAX_REDUCTION_CONDITIONS_COUNT_LINE_80 = CountKind.declare(
    CATALOG, "on428_tax_reduction_conditions_count_line_80", non_negative=True
)
"""Conditions count for ON428 line 80, "Enter "0" on line 80 if any of the following applies to
you:" "There is an amount on line 72": 0 when there is an amount on line 72, else 1."""

ON428_ONTARIO_TAX_REDUCTION_LINE_80 = AmountKind.declare(
    CATALOG, "on428_ontario_tax_reduction_line_80", non_negative=True
)
"""Ontario tax reduction, ON428 line 80 "Line 80: Line 78 minus line 79 (if negative, enter "0")
Ontario tax reduction =": the line 78 minus line 79 box, not below zero, or "0" when the printed
"Enter "0" on line 80 if any of the following applies to you" rule applies (take-home: there is
an amount on line 72)."""

ON428_TAX_AFTER_TAX_REDUCTION_LINE_81 = AmountKind.declare(
    CATALOG, "on428_tax_after_tax_reduction_line_81", non_negative=True
)
"""Ontario tax after the tax reduction, ON428 line 81 "Line 81: Line 73 minus line 80 (if negative,
enter "0") =": line 73 minus the Ontario tax reduction, not below zero."""

ON428_PROVINCIAL_FOREIGN_TAX_CREDIT_LINE_82 = AmountKind.declare(
    CATALOG, "on428_provincial_foreign_tax_credit_line_82", non_negative=True
)
"""Provincial foreign tax credit, ON428 line 82 "Line 82: Provincial foreign tax credit (complete
Form T2036)": an optional input that a salary-only caller leaves out."""

ON428_TAX_AFTER_FOREIGN_TAX_CREDIT_LINE_83 = AmountKind.declare(
    CATALOG, "on428_tax_after_foreign_tax_credit_line_83", non_negative=True
)
"""Ontario tax after the foreign tax credit, ON428 line 83 "Line 83: Line 81 minus line 82 (if
negative, enter "0") =": line 81 minus line 82, not below zero."""

ON428_LIFT_CREDIT_LINE_85 = AmountKind.declare(
    CATALOG, "on428_lift_credit_line_85", non_negative=True
)
"""Low-income individuals and families tax (LIFT) credit, ON428 line 85 "Line 85 and line 62140:
Low-income individuals and families tax (LIFT) credit (complete Schedule ON428-A)": the LIFT credit
for a single filer, Schedule ON428-A Part A line 20."""

ON428_TAX_AFTER_LIFT_CREDIT_LINE_86 = AmountKind.declare(
    CATALOG, "on428_tax_after_lift_credit_line_86", non_negative=True
)
"""Ontario tax after the LIFT credit, ON428 line 86 "Line 86: Line 84 minus line 85 (if negative,
enter "0") =": line 84 minus the LIFT credit, not below zero."""

ON428_QUALIFYING_FOOD_DONATIONS_LINE_87 = AmountKind.declare(
    CATALOG, "on428_qualifying_food_donations_line_87", non_negative=True
)
"""Qualifying food donations, ON428 line 87 "Line 87 and line 62150: Enter the amount of qualifying
donations that have also been claimed as a charitable donation": an optional input that a
salary-only caller leaves out, read as 0."""

ON428_FARMERS_FOOD_DONATION_CREDIT_LINE_87 = AmountKind.declare(
    CATALOG, "on428_farmers_food_donation_credit_line_87", non_negative=True
)
"""Farmers' food donation credit, ON428 line 87 "Line 87 and line 62150: Enter the amount of
qualifying donations that have also been claimed as a charitable donation. multiplied by 25% =":
calculated, the qualifying donations multiplied by 25%."""

ON428_TAX_AFTER_FARMERS_FOOD_DONATION_CREDIT_LINE_88 = AmountKind.declare(
    CATALOG, "on428_tax_after_farmers_food_donation_credit_line_88", non_negative=True
)
"""Ontario tax after the farmers' food donation credit, ON428 line 88 "Line 88: Line 86 minus line
87 (if negative, enter "0") =": line 86 minus line 87, never below zero."""

ON428_TAXABLE_INCOME_LINE_89 = AmountKind.declare(
    CATALOG, "on428_taxable_income_line_89", non_negative=True
)
"""Taxable income, ON428 line 89 chart line 1 "Enter your taxable income from line 26000 of your
return": the T1 taxable income, read from its record list."""

ON428_ONTARIO_HEALTH_PREMIUM_LINE_89 = AmountKind.declare(
    CATALOG, "on428_ontario_health_premium_line_89", non_negative=True
)
"""Ontario health premium, ON428 line 89 "Ontario health premium (complete the chart below)": the
row of the chart that line 1 falls in, its figure rounded half-up to the cent."""

ON428_ONTARIO_TAX_LINE_90 = AmountKind.declare(
    CATALOG, "on428_ontario_tax_line_90", non_negative=True
)
"""Ontario tax, ON428 line 90 "Line 90: Line 88 plus line 89 Enter this amount on line 42800 of your
return. Ontario tax =": line 88 plus line 89, entered on T1 line 42800."""

ON428_CPP_BASE_CREDIT_AMOUNT_LINE_19 = AmountKind.declare(
    CATALOG, "on428_cpp_base_credit_amount_line_19", non_negative=True
)
"""CPP base contributions credit amount, ON428 line 19 and line 58240 "Amount from line 30800 of
your return": a copy of Schedule 8 line 25, the CPP base contributions on the return."""

ON428_EI_CREDIT_AMOUNT_LINE_21 = AmountKind.declare(
    CATALOG, "on428_ei_credit_amount_line_21", non_negative=True
)
"""EI premiums credit amount, ON428 line 21 and line 58300: a copy of T2204 line 16, the EI
premiums credit amount."""

ON428_PENSION_INCOME_AMOUNT = AmountKind.declare(
    CATALOG, "on428_pension_income_amount", non_negative=True
)
"""Pension income amount, ON428 line 27 "Line 27 and line 58360: Pension income amount (maximum
$1,762)": the amount the filer claims, a caller input that is read as 0 when it is left out; the
line 27 step checks it against the printed maximum."""

ON428_PENSION_INCOME_AMOUNT_MAXIMUM = AmountKind.declare(
    CATALOG, "on428_pension_income_amount_maximum", non_negative=True
)
"""Pension income amount maximum, printed on ON428 line 27 "(maximum $1,762)": the printed maximum,
from the `ca-on/pension_income_amount_maximum` dataset; the bound line 27 cannot pass."""

ON428_PENSION_INCOME_AMOUNT_LINE_27 = AmountKind.declare(
    CATALOG, "on428_pension_income_amount_line_27", non_negative=True
)
"""Pension income amount, ON428 line 27 "Line 27 and line 58360: Pension income amount (maximum
$1,762)": the entered amount, passed on unchanged when it is at most the printed maximum, 0 when
left out; above the maximum it is refused, not capped."""

ON428_CREDITS_WITH_PENSION_LINE_28 = AmountKind.declare(
    CATALOG, "on428_credits_with_pension_line_28", non_negative=True
)
"""Ontario credits with the pension income amount, ON428 line 28 "Line 28: Line 26 plus line 27 =":
line 26 "Amount from line 25 of the previous page" (a copy of line 25) plus line 27 (the pension
income amount)."""

ON428_CREDITS_WITH_DISABILITY_LINE_31 = AmountKind.declare(
    CATALOG, "on428_credits_with_disability_line_31", non_negative=True
)
"""Total of the credits with the disability amounts, ON428 line 31 "Add lines 28 to 30.": the sum
of line 28 with the disability amounts of lines 29 and 30."""

TAX_REDUCTION_BASIC = AmountKind.declare(CATALOG, "tax_reduction_basic", non_negative=True)
"""Basic reduction, ON428 line 74 "Basic reduction 294.00": the amount claimed, the first part of
the Ontario tax reduction amounts."""

ON428_A_EMPLOYMENT_INCOME_LINE_1 = AmountKind.declare(
    CATALOG, "on428_a_employment_income_line_1", non_negative=True
)
"""Schedule ON428-A line 1 "Amount from line 10100 of your return" (employment income), read as the
T1 form's export."""

ON428_A_OTHER_EMPLOYMENT_INCOME_LINE_2 = AmountKind.declare(
    CATALOG, "on428_a_other_employment_income_line_2", non_negative=True
)
"""Schedule ON428-A line 2 "Amount from line 10400 of your return" (other employment income), read
as the T1 form's export."""

LIFT_EMPLOYMENT_INCOME = AmountKind.declare(CATALOG, "lift_employment_income", non_negative=True)
"""LIFT employment income, Schedule ON428-A line 3 "Line 1 plus line 2": line 1 "Amount from line
10100 of your return" (employment income) plus line 2 "Amount from line 10400 of your return"
(other employment income), in line order, the base of the LIFT rate on line 5."""

LIFT_CREDIT_BEFORE_MAXIMUM = AmountKind.declare(
    CATALOG, "lift_credit_before_maximum", non_negative=True
)
"""LIFT credit before its maximum, Schedule ON428-A line 5 "Line 3 multiplied by the percentage
from line 4 (maximum $875)" before the maximum: line 4 "Applicable rate 5.05%" on line 3 "Line 1
plus line 2", the sum of employment income (line 1 "Amount from line 10100 of your return") and
other employment income (line 2 "Amount from line 10400 of your return")."""

LIFT_MAXIMUM_CREDIT = AmountKind.declare(CATALOG, "lift_maximum_credit", non_negative=True)
"""LIFT credit at most its maximum, Schedule ON428-A line 5's "(maximum $875)", Part A line 14
"Amount from line 5 above (maximum $875)" and Part B line 29 "Amount from line 5 of the previous
page (maximum $875)"."""

LIFT_NET_INCOME = AmountKind.declare(CATALOG, "lift_net_income", non_negative=False)
"""Net income, Schedule ON428-A line 6 "Net income from line 23600 of your return (or the amount
you would have entered if the instructions on line 23600 said "if negative, show in brackets")",
which line 9 "Add lines 6 to 8." takes. Line 6 may be negative, so the kind is signed."""

LIFT_ADJUSTED_NET_INCOME = AmountKind.declare(
    CATALOG, "lift_adjusted_net_income", non_negative=True
)
"""Adjusted net income, Schedule ON428-A line 13 "Line 9 minus line 12 (if negative, enter "0")
Your adjusted net income", which Part A line 15 "Amount from line 13 above" and Part B line 30
"Amount from line 13 of the previous page" take."""

LIFT_SINGLE_EXCESS_OVER_THRESHOLD = AmountKind.declare(
    CATALOG, "lift_single_excess_over_threshold", non_negative=True
)
"""Excess over the individual threshold, Schedule ON428-A Part A line 17 "Line 15 minus line 16 (if
negative, enter "0")", line 15 being "Amount from line 13 above" and line 16 "Individual income
threshold 32,500.00"."""

LIFT_REDUCTION = AmountKind.declare(CATALOG, "lift_reduction", non_negative=True)
"""LIFT credit reduction, Schedule ON428-A Part A line 19 "Line 17 multiplied by the percentage
from line 18": line 18 "Applicable rate 5%" on line 17 "Line 15 minus line 16 (if negative, enter
"0")", line 16 "Individual income threshold 32,500.00".

Line 15 is "Amount from line 13 above", the adjusted net income (line 13). The schedule states no
eligibility rules of its own ("To find out if you are eligible for the low-income individuals and
families tax (LIFT) credit, go to canada.ca/on-tax-info.").
"""

LIFT_CREDIT_SINGLE = AmountKind.declare(CATALOG, "lift_credit_single", non_negative=True)
"""LIFT credit for a single individual, Schedule ON428-A Part A line 20 "Line 14 minus line 19 (if
negative, enter "0") Enter this amount on line 62140 of your Form ON428.": the maximum credit less
the reduction."""

LIFT_INDIVIDUAL_INCOME_THRESHOLD = AmountKind.declare(
    CATALOG, "lift_individual_income_threshold", non_negative=True
)
"""Individual income threshold, Schedule ON428-A Part A line 16 "Individual income threshold
32,500.00" and Part B line 31 "Individual income threshold 32,500.00": a printed amount, taken
whole."""

ONTARIO_SURTAX_BASE = AmountKind.declare(CATALOG, "ontario_surtax_base", non_negative=True)
"""Ontario surtax base, ON428 line 65 "Line 65: Line 63 minus line 64 (if negative, enter "0") =":
the figure on the return summary, the one amount of ON428's export of line 65 totalled into the
return's own artifact."""

ONTARIO_SURTAX_FACTOR = AmountKind.declare(CATALOG, "ontario_surtax_factor", non_negative=True)
"""Ontario surtax factor, ON428 line 66 "(Line 65 minus $5,710) multiplied by 20%" and line 67
"(Line 65 minus $7,307) multiplied by 36%": 1 plus the rate of each surtax tier line 65 is over,
the tax a further dollar of Ontario tax brings with the surtax. A plain figure with no unit, not
printed on the form."""

ONTARIO_BRACKET_RATE_RETURN = AmountKind.declare(
    CATALOG, "ontario_bracket_rate_return", non_negative=True
)
"""Ontario bracket rate, ON428 line 5 "Line 5: Rate": the printed rate of the column that line 1
falls in, read from ON428 into the return summary."""

RETURN_TAXABLE_INCOME = AmountKind.declare(CATALOG, "return_taxable_income", non_negative=True)
"""Taxable income on the Return summary: the T1 taxable income (line 26000), the base of the
health premium chart."""

RETURN_HEALTH_PREMIUM_SLOPE = AmountKind.declare(
    CATALOG, "return_health_premium_slope", non_negative=True
)
"""Health premium slope, ON428 line 89 chart: the printed rate of the chart row that the taxable
income falls in (6% or 25%), 0 for a flat row."""

ONTARIO_TAX_AFTER_LIFT_RETURN = AmountKind.declare(
    CATALOG, "ontario_tax_after_lift_return", non_negative=True
)
"""Ontario tax after the LIFT credit, ON428 line 86 "Line 83 minus line 85 (if negative, enter
"0")": the one amount of ON428's export totalled into the return summary's own artifact, the base
of the Ontario rate gate."""

ONTARIO_RATE_GATE = AmountKind.declare(CATALOG, "ontario_rate_gate", non_negative=True)
"""Ontario rate gate: 0 where the Ontario tax after the LIFT credit (ON428 line 86) is 0.00 and 1
where it is at least one cent, from the `ca-on/marginal_rate_gate` dataset. Where the LIFT credit
takes all the Ontario tax, a further dollar of salary adds no Ontario tax. A plain figure, not
printed on the form."""

ONTARIO_TAX_REDUCTION_RETURN = AmountKind.declare(
    CATALOG, "ontario_tax_reduction_return", non_negative=True
)
"""Ontario tax reduction, ON428 line 80: the one amount of ON428's export totalled into the return
summary's own artifact, the base of the Ontario reduction gate."""

ONTARIO_REDUCTION_GATE = AmountKind.declare(CATALOG, "ontario_reduction_gate", non_negative=True)
"""Ontario reduction gate: 0 where the Ontario tax reduction (ON428 line 80) is 0.00 and 1 where
it is at least one cent, from the `ca-on/marginal_rate_gate` dataset. A plain figure, not printed
on the form."""

MARGINAL_NET_INCOME_RATE = AmountKind.declare(
    CATALOG, "marginal_net_income_rate", non_negative=True
)
"""Part of a further dollar of salary left in the net income (T1 line 23600) and the taxable
income: 1 less the CPP first additional rate and the CPP second additional rate, which T1 line
22215 takes off the income. The federal form's export `ca/take_home_marginal_rates.marginal_net_
income_rate`, totalled into the return summary's own artifact. Not printed on the form."""

MARGINAL_CREDIT_CONTRIBUTION_RATE = AmountKind.declare(
    CATALOG, "marginal_credit_contribution_rate", non_negative=True
)
"""Credit-earning contribution rate on a further dollar of salary: the CPP base rate (T1 line
30800) plus the EI rate (T1 line 31200), the two contributions that earn a non-refundable credit.
The federal form's export `ca/take_home_marginal_rates.marginal_credit_contribution_rate`, totalled
into the return summary's own artifact. Not printed on the form."""

MARGINAL_ONTARIO_CONTRIBUTION_CREDIT_RATE = AmountKind.declare(
    CATALOG, "marginal_ontario_contribution_credit_rate", non_negative=True
)
"""Ontario credit rate on the CPP base and EI of a further dollar of salary: the credit-earning
contribution rate times the Ontario credit rate (ON428 line 45 "Ontario non-refundable tax credit
rate"), the Ontario tax the contributions take off. An exact product, not printed on the form."""

MARGINAL_FEDERAL_RATE = AmountKind.declare(CATALOG, "marginal_federal_rate", non_negative=True)
"""Federal marginal rate on the take-home basis: the federal rate on a further dollar of salary
after the credits, where the basic federal tax (T1 line 42900) is above zero, and 0 where it is
not, a fraction (0.2 for 20%). The federal form's export `ca/take_home_marginal_rates.marginal_
federal_rate`, totalled into the return summary's own artifact. Not printed on the form."""

MARGINAL_ONTARIO_BRACKET_RATE = AmountKind.declare(
    CATALOG, "marginal_ontario_bracket_rate", non_negative=True
)
"""Ontario bracket rate on a further dollar of salary, ON428 line 5 "Line 5: Rate" times the part
left in the net income. An exact product, not printed on the form."""

MARGINAL_AGE_INCOME_OVER_THRESHOLD = AmountKind.declare(
    CATALOG, "marginal_age_income_over_threshold", non_negative=True
)
"""Worksheet ON428 "Line 58080 - Age amount" line 4 "Line 2 minus line 3 (if negative, enter 0)":
ON428's export totalled into the return summary's own artifact, the net income over the age
threshold, the base of the age threshold gate."""

MARGINAL_AGE_AMOUNT_CLAIMED = AmountKind.declare(
    CATALOG, "marginal_age_amount_claimed", non_negative=True
)
"""The age amount the filer claims before the printed maximum check (Worksheet ON428 line 7 times
the aged 65 or older count; 0 for a filer under 65 or with no birth year): ON428's export totalled
into the return summary's own artifact, the base of the age amount gate."""

MARGINAL_AGE_THRESHOLD_GATE = AmountKind.declare(
    CATALOG, "marginal_age_threshold_gate", non_negative=True
)
"""Age threshold gate: 0 where the net income over the age threshold is 0.00 and 1 where it is at
least one cent, from the `ca-on/marginal_rate_gate` dataset: the age amount is falling only over
its threshold. A plain figure, not printed on the form."""

MARGINAL_AGE_AMOUNT_GATE = AmountKind.declare(
    CATALOG, "marginal_age_amount_gate", non_negative=True
)
"""Age amount gate: 0 where the age amount claimed is 0.00 (a filer under 65, no birth year, or an
amount already reduced to nothing) and 1 where it is at least one cent, from the
`ca-on/marginal_rate_gate` dataset. A plain figure, not printed on the form."""

MARGINAL_AGE_RATE = AmountKind.declare(CATALOG, "marginal_age_rate", non_negative=True)
"""Age amount reduction rate, Worksheet ON428 "Line 58080 - Age amount" line 5 "Applicable rate
15%": the `ca-on/age_rate` dataset as it is, the fall of the age amount per dollar of net income
over the threshold. A rate, with the cent rounding of the worksheet's line 6 box left off."""

MARGINAL_AGE_REDUCTION_RATE_OVER_THRESHOLD = AmountKind.declare(
    CATALOG, "marginal_age_reduction_rate_over_threshold", non_negative=True
)
"""The age amount reduction rate where the net income is over the age threshold, 0 at or under it.
An exact product, not printed on the form."""

MARGINAL_AGE_REDUCTION_RATE = AmountKind.declare(
    CATALOG, "marginal_age_reduction_rate", non_negative=True
)
"""Fall of the Ontario age amount (ON428 line 10) on a further dollar of net income: the reduction
rate where net income is over the threshold and an age amount is still claimed, 0 otherwise. An
exact product, not printed on the form."""

MARGINAL_AGE_PHASE_DOWN_NET_INCOME_RATE = AmountKind.declare(
    CATALOG, "marginal_age_phase_down_net_income_rate", non_negative=True
)
"""Fall of the Ontario age amount on a further dollar of salary: its fall per dollar of net income
times the part of the dollar left in the net income. An exact product, not printed on the form."""

MARGINAL_ONTARIO_AGE_CREDIT_RATE = AmountKind.declare(
    CATALOG, "marginal_ontario_age_credit_rate", non_negative=True
)
"""Ontario tax a further dollar of salary adds through the age amount: the fall of the age amount
times the Ontario credit rate (ON428 line 45), before the surtax. An exact product, not printed on
the form."""

MARGINAL_ONTARIO_RATE_BEFORE_CREDITS = AmountKind.declare(
    CATALOG, "marginal_ontario_rate_before_credits", non_negative=True
)
"""Ontario rate on a further dollar of salary before the CPP base and EI credits: the bracket rate
plus the tax the falling age amount adds. An exact sum, not printed on the form."""

MARGINAL_ONTARIO_RATE_AFTER_CREDITS = AmountKind.declare(
    CATALOG, "marginal_ontario_rate_after_credits", non_negative=True
)
"""Ontario rate on a further dollar of salary after the CPP base and EI credits, before the
surtax: the rate before the credits less the credit on the contributions. An exact difference, not
printed on the form."""

MARGINAL_ONTARIO_RATE_WITH_SURTAX = AmountKind.declare(
    CATALOG, "marginal_ontario_rate_with_surtax", non_negative=True
)
"""Ontario rate on a further dollar of salary with the surtax: the rate after the credits times
the surtax factor of ON428 lines 66 and 67. An exact product, not printed on the form."""

ONTARIO_REDUCTION_PHASE_OUT_RATE = AmountKind.declare(
    CATALOG, "ontario_reduction_phase_out_rate", non_negative=True
)
"""Ontario reduction phase-out rate: the Ontario rate with the surtax where the Ontario tax
reduction (ON428 line 80) is above zero, and 0 where it is not, the extra tax on a further dollar
while the reduction is phased out. An exact product, not printed on the form."""

MARGINAL_ONTARIO_RATE_WITH_REDUCTION = AmountKind.declare(
    CATALOG, "marginal_ontario_rate_with_reduction", non_negative=True
)
"""Ontario rate on a further dollar of salary with the surtax and the tax reduction's phase-out,
before the LIFT credit. An exact sum, not printed on the form."""

RETURN_LIFT_REDUCTION = AmountKind.declare(CATALOG, "return_lift_reduction", non_negative=True)
"""LIFT reduction, Schedule ON428-A Part A line 19 "Line 17 multiplied by the percentage from line
18": the one amount of ON428-A's export totalled into the return summary's own artifact, the base
of the LIFT reduction rate."""

RETURN_LIFT_CREDIT = AmountKind.declare(CATALOG, "return_lift_credit", non_negative=True)
"""LIFT credit left, Schedule ON428-A Part A line 20: the one amount of ON428-A's export totalled
into the return summary's own artifact."""

LIFT_REDUCTION_GATE = AmountKind.declare(CATALOG, "lift_reduction_gate", non_negative=True)
"""1 where the LIFT reduction (line 19) is at least a cent, 0 where it is 0.00, from the
`ca-on/marginal_rate_gate` dataset. A plain figure, not printed on the form."""

LIFT_CREDIT_GATE = AmountKind.declare(CATALOG, "lift_credit_gate", non_negative=True)
"""1 where the LIFT credit left (line 20) is at least a cent, 0 where it is 0.00, from the
`ca-on/marginal_rate_gate` dataset. A plain figure, not printed on the form."""

LIFT_PHASE_OUT_GATE = AmountKind.declare(CATALOG, "lift_phase_out_gate", non_negative=True)
"""1 where the LIFT reduction and the credit left are both above 0, the two gates multiplied: the
credit is falling with income. A plain figure, not printed on the form."""

LIFT_SINGLE_RATE_FIGURE = AmountKind.declare(CATALOG, "lift_single_rate_figure", non_negative=True)
"""LIFT reduction rate, Schedule ON428-A line 18 "Applicable rate 5%": the `ca-on/lift_single_rate`
dataset as it is, a rate, not printed as a figure of its own."""

MARGINAL_ONTARIO_CREDIT_RATE = AmountKind.declare(
    CATALOG, "marginal_ontario_credit_rate", non_negative=True
)
"""Ontario non-refundable tax credit rate, ON428 line 45: the `ca-on/credit_rate` dataset as it is,
with none of the cent rounding the credit box applies. A rate, not printed as its own figure."""

MARGINAL_LIFT_REDUCTION_RATE = AmountKind.declare(
    CATALOG, "marginal_lift_reduction_rate", non_negative=True
)
"""LIFT reduction rate on a further dollar of net income, Schedule ON428-A line 18 "Applicable
rate 5%": 5% while the reduction (line 19) and the credit left (line 20) are both above zero, 0
elsewhere. Not printed on the form."""

MARGINAL_LIFT_PHASE_OUT_RATE = AmountKind.declare(
    CATALOG, "marginal_lift_phase_out_rate", non_negative=True
)
"""LIFT credit phase-out on a further dollar of salary: the LIFT reduction rate times the part
left in the net income, the Ontario tax the lost credit adds. An exact product, not printed on the
form."""

MARGINAL_ONTARIO_RATE_AFTER_LIFT = AmountKind.declare(
    CATALOG, "marginal_ontario_rate_after_lift", non_negative=True
)
"""Ontario rate on a further dollar of salary after the LIFT credit, before the Ontario gate: the
rate with the surtax and the tax reduction plus the LIFT phase-out. An exact sum, not printed on
the form."""

ONTARIO_MARGINAL_RATE = AmountKind.declare(CATALOG, "ontario_marginal_rate", non_negative=True)
"""Ontario marginal rate on the take-home basis: the Ontario rate on a further dollar of salary
after the credits and the LIFT phase-out, where the Ontario tax after the LIFT credit (ON428 line
86) is above zero, and 0 where it is not. Not printed on the form."""

MARGINAL_HEALTH_PREMIUM_RATE = AmountKind.declare(
    CATALOG, "marginal_health_premium_rate", non_negative=True
)
"""Health premium rate on a further dollar of salary, ON428 line 89 chart: the rate of the chart
row the taxable income falls in (the health premium slope) times the part left in the taxable
income. An exact product, not printed on the form."""

MARGINAL_CONTRIBUTION_RATE = AmountKind.declare(
    CATALOG, "marginal_contribution_rate", non_negative=True
)
"""Contribution rate on a further dollar of salary: the CPP base, first additional and second
additional rates plus the EI rate of T2204 line 16. The federal form's export
`ca/take_home_marginal_rates.marginal_contribution_rate`, totalled into the return summary's own
artifact. Not printed on the form."""

MARGINAL_TAX_RATE = AmountKind.declare(CATALOG, "marginal_tax_rate", non_negative=True)
"""Marginal tax rate on the take-home basis: the change in the T1 line 43500 income tax, the CPP
and the EI (T2204 line 16) per further dollar of salary, the sum of the federal marginal rate, the
Ontario marginal rate, the health premium rate and the contribution rate, on the return summary.
Calculated from the forms' rates, not printed on the form."""

AVERAGE_TAX_RATE = AmountKind.declare(CATALOG, "average_tax_rate", non_negative=True)
"""Average tax rate on the take-home basis, the Ontario return summary's own figure (no form prints
it): the income tax, CPP (Schedule 8 lines 25 and 28), EI (T2204 line 16) together divided by the
salary (`ca/return_employment_income`), as a fraction, so 0.1598 is 15.98%. Paid credits are not
in it. It is 0 when the salary is 0."""
