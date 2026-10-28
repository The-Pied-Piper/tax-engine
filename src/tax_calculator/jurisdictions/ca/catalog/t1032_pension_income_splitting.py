"""The federal catalog: Form T1032, Joint Election to Split Pension Income, the form `ca/t1032`, run
once (no instances). Step 2 is the maximum split-pension amount (lines 1 to 21), Step 3 the elected
amount (line 22), Step 4 the pension income amounts of line 31400 for both spouses (lines 23 to 34)
and Step 5 the income tax deducted (lines 35 to 42). The starting inputs are the lines 1, 2, 4, 18,
32 and 35 and the three yes-or-no answers; lines 37 and 40 are the return's own
`ca/income_tax_deducted` (T1 line 43700 before the election); the elected amount is the
one amount of line 22, entered once with the answer of Step 3 and carried by the return on line
21000 (`ca/elected_split_pension_deduction`, the transferring spouse's return) or on line 11600
(`ca/elected_split_pension_amount`, the receiving spouse's return), never entered on those lines.
The intermediate kinds are the steps between the inputs and the exports; the exports are the form's
lines 21, the checked answer of Step 3, 22, 31400 of each spouse, 39 and 42. The last kinds check
line 1 of a transferring spouse's return against line 8 of the return's own Federal Worksheet for
line 31400, and read the exports into the return's T1 lines 31400 and 43700."""

from __future__ import annotations

from decimal import Decimal

from tax_calculator.jurisdictions.ca.catalog.base import CATALOG

T1032_ELIGIBLE_PENSION_INCOME = CATALOG.declare(
    "t1032_eligible_pension_income", Decimal, non_negative=True
)
"""Eligible pension income, Form T1032 Step 2 "Line 1 and line 68020: Enter the amount of eligible
pension income that was calculated on line 8 of the transferring spouse's or common-law partner's
Federal Worksheet for line 31400": the amount the filer enters, a starting amount."""

T1032_T4A_BOX_128 = CATALOG.declare("t1032_t4a_box_128", Decimal, non_negative=True)
"""Veterans benefits in box 128 of the T4A, Form T1032 Step 2 "Line 2 and line 68025: Enter the
amount from box 128 of the transferring spouse's or common-law partner's T4A slip": the amount the
filer enters, a starting amount, refused above line 1 (it is included in line 1)."""

T1032_T4A_RCA_BOX_17 = CATALOG.declare("t1032_t4a_rca_box_17", Decimal, non_negative=True)
"""Amount from box 17 of the T4A-RCA slips, Form T1032 Step 2 "Line 4 and line 68026: Enter the
amount from box 17 of the transferring spouse's or common-law partner's T4A-RCA slips": the amount
the filer enters, a starting amount."""

T1032_RCA_PAYMENTS_QUALIFY = CATALOG.declare("t1032_rca_payments_qualify", int, non_negative=True)
"""Qualifying RCA payments, Form T1032 Step 2 "Qualifying retirement compensation arrangement (RCA)
payments": "If the transferring spouse or common-law partner received life annuity payments from
an RCA and was 65 years of age or older on December 31, 2025 (or on the date of death), complete
lines 4 to 8. Otherwise, enter "0" on line 8": 1 for yes and 0 for no, a starting count, refused
above 1."""

T1032_MARITAL_STATUS_CHANGED = CATALOG.declare(
    "t1032_marital_status_changed", int, non_negative=True
)
"""Marital status changed in the year, Form T1032 Step 2 "Adjustment for marital status change
during the tax year": "If your marital status changed during the year, use line 18 to calculate
the eligible pension income to enter at line 19": 1 for yes and 0 for no, a starting count,
refused above 1."""

T1032_TRANSFERRING_SPOUSE_DIED = CATALOG.declare(
    "t1032_transferring_spouse_died", int, non_negative=True
)
"""Transferring spouse died in the year, Form T1032 Step 2 Note 1 "If the transferring spouse or
common-law partner is deceased, replace the "12" with the number of months up to and including the
month of death": 1 for yes and 0 for no, a starting count, refused above 1."""

T1032_NOT_SEPARATED_90_DAYS = CATALOG.declare("t1032_not_separated_90_days", int, non_negative=True)
"""Not living separate and apart, Form T1032 page 1 "You must meet all of the following conditions:
You and your spouse or common-law partner were not living separate and apart from each other,
because of a breakdown in your marriage or common-law relationship, for a continuous period of 90
days or more which includes December 31, 2025": 1 when the condition is met and 0 when it is not,
a starting count, refused above 1."""

T1032_RESIDENTS_OF_CANADA = CATALOG.declare("t1032_residents_of_canada", int, non_negative=True)
"""Residents of Canada, Form T1032 page 1 "You must meet all of the following conditions: You and
your spouse or common-law partner were residents of Canada on December 31, 2025 (or on the date of
death)": 1 when the condition is met and 0 when it is not, a starting count, refused above 1."""

T1032_FILER_IS_TRANSFERRING_SPOUSE = CATALOG.declare(
    "t1032_filer_is_transferring_spouse", int, non_negative=True
)
"""This return is the transferring spouse's, Form T1032 Step 3 "Enter this amount on line 21000 of
the transferring spouse's or common-law partner's return and on line 11600 of the receiving
spouse's or common-law partner's return", and "you (the transferring spouse or common-law partner)":
1 when this return is the transferring spouse's, whose elected amount is on line 21000, and 0
when it is the receiving spouse's, whose elected amount is on line 11600, a starting count, refused
above 1."""

T1032_MONTHS_MARRIED = CATALOG.declare("t1032_months_married", Decimal, non_negative=True)
"""Number of months married or living common-law, Form T1032 line 18 "Line 18: Number of months
married or living common-law Line 68030": the number of months the filer enters, a starting amount,
refused above the months in the tax year."""

T1032_MONTHS_IN_TAX_YEAR = CATALOG.declare("t1032_months_in_tax_year", Decimal, non_negative=True)
"""Number of months in the tax year, Form T1032 line 18 "Divided by Number of months in the tax year
(12) (Note 1)": 12, or for a deceased transferring spouse the number of months up to and including
the month of death (Note 1), a starting amount, refused above 12."""

T1032_RECEIVING_SPOUSE_PENSION_AMOUNT = CATALOG.declare(
    "t1032_receiving_spouse_pension_amount", Decimal, non_negative=True
)
"""Pension amount of the receiving spouse, Form T1032 Step 4 "Line 32: If there is an amount on line
11500 or line 12900 of the receiving spouse's or common-law partner's return, enter the amount from
line 8 of their Federal Worksheet for line 31400. Otherwise, enter "0"": a starting amount."""

T1032_INCOME_TAX_DEDUCTED_ON_PENSION = CATALOG.declare(
    "t1032_income_tax_deducted_on_pension", Decimal, non_negative=True
)
"""Income tax deducted on the pension, Form T1032 Step 5 "Line 35 and line 68040: Enter the total
tax deducted from the transferring spouse's or common-law partner's pension income entered on
line 17": a starting amount, refused above line 37."""

T1032_RCA_PAYMENTS_QUALIFY_CHECKED = CATALOG.declare(
    "t1032_rca_payments_qualify_checked", int, non_negative=True
)
"""Qualifying RCA payments, checked, Form T1032 Step 2 "Qualifying retirement compensation
arrangement (RCA) payments" "Otherwise, enter "0" on line 8": 0 or 1, which the lines 8 read."""

T1032_MARITAL_STATUS_CHANGED_CHECKED = CATALOG.declare(
    "t1032_marital_status_changed_checked", int, non_negative=True
)
"""Marital status changed in the year, checked, Form T1032 Step 2 "Adjustment for marital status
change during the tax year" "If your marital status changed during the year": 0 or 1, which line
19 reads."""

T1032_TRANSFERRING_SPOUSE_DIED_CHECKED = CATALOG.declare(
    "t1032_transferring_spouse_died_checked", int, non_negative=True
)
"""Transferring spouse died in the year, checked, Form T1032 Step 2 Note 1 "If the transferring
spouse or common-law partner is deceased": 0 or 1, which the denominator of line 18 reads."""

T1032_NOT_SEPARATED_90_DAYS_CHECKED = CATALOG.declare(
    "t1032_not_separated_90_days_checked", int, non_negative=True
)
"""Not living separate and apart, checked, Form T1032 page 1 "were not living separate and apart
from each other ... for a continuous period of 90 days or more which includes December 31, 2025":
0 or 1, which the maximum split-pension amount reads."""

T1032_RESIDENTS_OF_CANADA_CHECKED = CATALOG.declare(
    "t1032_residents_of_canada_checked", int, non_negative=True
)
"""Residents of Canada, checked, Form T1032 page 1 "were residents of Canada on December 31, 2025
(or on the date of death)": 0 or 1, which the maximum split-pension amount reads."""

T1032_LINE_21_IF_NOT_SEPARATED = CATALOG.declare(
    "t1032_line_21_if_not_separated", Decimal, non_negative=True
)
"""Line 21 of Form T1032 when the first condition of page 1 is met, "Line 21: Line 19 multiplied by
line 20 Maximum split-pension amount": line 21 when the spouses were not separated, otherwise 0."""

T1032_LINE_21_IF_CONDITIONS_MET = CATALOG.declare(
    "t1032_line_21_if_conditions_met", Decimal, non_negative=True
)
"""Line 21 of Form T1032 when the two conditions of page 1 about the spouses are met, "You must meet
all of the following conditions": line 21 when the spouses were not separated and were residents
of Canada, otherwise 0, the most line 22 can be."""

T1032_FILER_IS_TRANSFERRING_SPOUSE_CHECKED = CATALOG.declare(
    "t1032_filer_is_transferring_spouse_checked", int, non_negative=True
)
"""This return is the transferring spouse's, checked, Form T1032 Step 3 "Enter this amount on line
21000 of the transferring spouse's or common-law partner's return and on line 11600 of the receiving
spouse's or common-law partner's return": 0 or 1, which line 22 reads and the form exports."""

T1032_LINE_2_CHECKED = CATALOG.declare("t1032_line_2_checked", Decimal, non_negative=True)
"""Line 2 of Form T1032, "Line 2 and line 68025: Enter the amount from box 128": the box 128 amount,
refused above line 1 (the form prints no bound), which lines 3 and 16 read."""

T1032_LINE_3 = CATALOG.declare("t1032_line_3", Decimal, non_negative=True)
"""Line 3 of Form T1032, "Line 3: Line 1 minus line 2 =": the eligible pension income less line
2."""

T1032_LINE_5 = CATALOG.declare("t1032_line_5", Decimal, non_negative=True)
"""Line 5 of Form T1032, "Line 5: 131,483.45": the ceiling of the retirement compensation
arrangement calculation, the amount of the dataset."""

T1032_LINE_7 = CATALOG.declare("t1032_line_7", Decimal, non_negative=True)
"""Line 7 of Form T1032, "Line 7: Line 5 minus line 6 (if negative, enter "0") =": line 5 less line
3, not below zero."""

T1032_LINE_8_BEFORE_GATE = CATALOG.declare("t1032_line_8_before_gate", Decimal, non_negative=True)
"""Line 8 of Form T1032 before the RCA answer, "Line 8: Enter whichever is less: line 4 or line 7.":
the lesser of line 4 and line 7, which line 8 keeps only with a qualifying RCA payment."""

T1032_LINE_8 = CATALOG.declare("t1032_line_8", Decimal, non_negative=True)
"""Line 8 of Form T1032, "Line 8: Enter whichever is less: line 4 or line 7" and "Otherwise, enter
"0" on line 8": the amount of line 8 before the gate when there is a qualifying RCA payment,
otherwise 0."""

T1032_LINE_12 = CATALOG.declare("t1032_line_12", Decimal, non_negative=True)
"""Line 12 of Form T1032, "Line 12: Line 10 plus line 11 =", where line 10 is line 3 and line 11 is
line 8."""

T1032_LINE_13 = CATALOG.declare("t1032_line_13", Decimal, non_negative=True)
"""Line 13 of Form T1032, "Line 13: 131,483.45": the ceiling of the veterans benefits calculation,
the amount of the dataset."""

T1032_LINE_15 = CATALOG.declare("t1032_line_15", Decimal, non_negative=True)
"""Line 15 of Form T1032, "Line 15: Line 13 minus line 14 (if negative, enter "0") =", where line 14
is line 12: line 13 less line 12, not below zero."""

T1032_LINE_16 = CATALOG.declare("t1032_line_16", Decimal, non_negative=True)
"""Line 16 of Form T1032, "Line 16: Enter whichever is less: line 9 or line 15", where line 9 is
line 2: the lesser of line 2 and line 15."""

T1032_LINE_17 = CATALOG.declare("t1032_line_17", Decimal, non_negative=True)
"""Line 17 of Form T1032, "Line 17: Add lines 3, 8, and 16. =": the sum of lines 3, 8 and 16."""

T1032_MONTHS_MARRIED_CHECKED = CATALOG.declare(
    "t1032_months_married_checked", Decimal, non_negative=True
)
"""Number of months married or living common-law, checked, Form T1032 line 18 "Line 18: Number of
months married or living common-law": at most the months in the tax year, refused above it (the
form prints no bound), which line 18 reads as its numerator."""

T1032_MONTHS_IN_TAX_YEAR_CEILING = CATALOG.declare(
    "t1032_months_in_tax_year_ceiling", Decimal, non_negative=True
)
"""Number of months in the tax year, the ceiling, Form T1032 line 18 "Divided by Number of months in
the tax year (12) (Note 1)": the 12 months of the dataset, the most the denominator can be."""

T1032_LINE_18_MONTHS_IN_TAX_YEAR = CATALOG.declare(
    "t1032_line_18_months_in_tax_year", Decimal, non_negative=True
)
"""Number of months in the tax year, Form T1032 line 18 "Divided by Number of months in the tax year
(12) (Note 1)": the printed 12 when the marital status did not change in the year, otherwise the
months in the tax year the filer enters (Note 1: the months up to and including the month of
death)."""

T1032_MONTHS_IN_TAX_YEAR_CHECKED = CATALOG.declare(
    "t1032_months_in_tax_year_checked", Decimal, non_negative=True
)
"""Number of months in the tax year, checked, Form T1032 line 18 "Divided by Number of months in the
tax year (12) (Note 1)": the chosen denominator, at most 12, refused above it, which line 18 reads
as its denominator."""

T1032_LINE_18 = CATALOG.declare("t1032_line_18", Decimal, non_negative=True)
"""Line 18 of Form T1032, "Line 18: Number of months married or living common-law Line 68030
Divided by Number of months in the tax year (12) (Note 1) multiplied by Amount from line 17 =": line
17 multiplied by the months married and divided by the months in the tax year (the printed 12, or
under Note 1 the typed months), a zero denominator refused, rounded half-up to the cent once."""

T1032_LINE_19 = CATALOG.declare("t1032_line_19", Decimal, non_negative=True)
"""Line 19 of Form T1032, "Line 19: Enter the amount from line 18, if it applies. Otherwise, enter
the amount from line 17.": line 18 if the marital status changed in the year, otherwise line 17."""

T1032_LINE_21 = CATALOG.declare("t1032_line_21", Decimal, non_negative=True)
"""Line 21 of Form T1032, "Line 21: Line 19 multiplied by line 20 Maximum split-pension amount =":
line 19 at the maximum rate of 50% (line 20), the maximum split-pension amount, which line 22 is
checked against once the conditions of page 1 are applied."""

T1032_LINE_22 = CATALOG.declare("t1032_line_22", Decimal, non_negative=True)
"""Line 22 of Form T1032, "Line 22: Enter the amount that you and your spouse or common-law partner
decide to jointly elect to be your split-pension amount for the year" and "Enter this amount on line
21000 of the transferring spouse's or common-law partner's return and on line 11600 of the receiving
spouse's or common-law partner's return": the one amount the filer enters, a starting amount, which
the return carries on line 21000 when `ca/t1032_filer_is_transferring_spouse` is 1 and on line 11600
when it is 0, before it is checked against line 21."""

T1032_LINE_22_CHECKED = CATALOG.declare("t1032_line_22_checked", Decimal, non_negative=True)
"""Line 22 of Form T1032, "Line 22: Enter the amount that you and your spouse or common-law partner
decide to jointly elect to be your split-pension amount for the year. The split-pension amount
cannot be more than the amount from line 21": line 22, refused above line 21, not
capped, which lines 24, 29, 36 and the exports read."""

T1032_LINE_29 = CATALOG.declare("t1032_line_29", Decimal, non_negative=True)
"""Line 29 of Form T1032, "Line 27 multiplied by line 28 =", where line 27 is line 25 (line 8)
divided by line 26 (line 17) and line 28 is line 24 (line 22): zero when line 17 is zero, rounded
half-up to the cent once."""

T1032_LINE_30 = CATALOG.declare("t1032_line_30", Decimal, non_negative=True)
"""Line 30 of Form T1032, "Line 30: Line 24 minus line 29 =": line 22 less line 29."""

T1032_LINE_31 = CATALOG.declare("t1032_line_31", Decimal, non_negative=True)
"""Line 31 of Form T1032, "Line 31: Line 23 minus line 30 =", where line 23 is line 1: the eligible
pension income less line 30."""

T1032_LINE_31400_TRANSFERRING = CATALOG.declare(
    "t1032_line_31400_transferring", Decimal, non_negative=True
)
"""Line 31400 of the transferring spouse, Form T1032 Step 4 Part A "Enter on line 31400 of the
transferring spouse's or common-law partner's return, whichever is less: $2,000 or the amount from
line 31.": the lesser of $2,000 and line 31, which the return's pension income amount reads."""

T1032_LINE_34 = CATALOG.declare("t1032_line_34", Decimal, non_negative=True)
"""Line 34 of Form T1032, "Line 34: Line 32 plus line 33 =": the receiving spouse's pension amount
plus line 33."""

T1032_LINE_31400_RECEIVING = CATALOG.declare(
    "t1032_line_31400_receiving", Decimal, non_negative=True
)
"""Line 31400 of the receiving spouse, Form T1032 Step 4 Part B "Enter on line 31400 of the
receiving spouse's or common-law partner's return, whichever is less: $2,000 or the amount from
line 34.": the lesser of $2,000 and line 34, which the return's pension income amount reads."""

T1032_LINE_35_OF_TRANSFERRING_SPOUSE = CATALOG.declare(
    "t1032_line_35_of_transferring_spouse", Decimal, non_negative=True
)
"""Line 35 of Form T1032 for the transferring spouse's return, "Line 35 and line 68040: Enter the
total tax deducted from the transferring spouse's or common-law partner's pension income entered on
line 17": line 35 when this return is the transferring spouse's, otherwise 0."""

T1032_LINE_37_OF_TRANSFERRING_SPOUSE = CATALOG.declare(
    "t1032_line_37_of_transferring_spouse", Decimal, non_negative=True
)
"""Line 37 of Form T1032 for the transferring spouse's return, "Line 37: Total tax deducted from all
of the transferring spouse's or common-law partner's slips. Enter the amount that you would have
entered on line 43700 of your return if you did not choose to split your eligible pension income":
the return's own `ca/income_tax_deducted` when this return is the transferring spouse's, otherwise
0."""

T1032_LINE_35_OF_TRANSFERRING_SPOUSE_CHECKED = CATALOG.declare(
    "t1032_line_35_of_transferring_spouse_checked", Decimal, non_negative=True
)
"""Line 35 of Form T1032 for the transferring spouse's return, checked: line 35 refused above line
37 (the tax on the pension is part of all the tax deducted from the transferring spouse's slips),
not capped, when this return is the transferring spouse's, otherwise 0."""

T1032_LINE_35_CHECKED = CATALOG.declare("t1032_line_35_checked", Decimal, non_negative=True)
"""Line 35 of Form T1032, "Line 35 and line 68040: Enter the total tax deducted from the
transferring spouse's or common-law partner's pension income entered on line 17": the checked
amount (refused above line 37, not capped) on the transferring spouse's return, and the amount as
entered on the receiving spouse's, whose line 37 is not the transferring spouse's total. Line 36
reads it."""

T1032_LINE_36 = CATALOG.declare("t1032_line_36", Decimal, non_negative=True)
"""Line 36 of Form T1032, "Line 36: Amount from line 35 multiplied by Amount from line 22 divided by
Amount from line 17 Line 68050 =": the tax deducted on the elected amount, zero when line 17 is
zero, rounded half-up to the cent once, which lines 39 and 42 read."""

T1032_LINE_39 = CATALOG.declare("t1032_line_39", Decimal)
"""Line 39 of Form T1032, "Line 39: Line 37 minus line 38 Enter the result on line 43700 of the
transferring spouse's or common-law partner's return.": line 37 (the return's own
`ca/income_tax_deducted`) less line 36, the export for line 43700 of the transferring spouse's
return. It can be below 0 on a receiving spouse's return, whose own tax deducted is not line 37 of
the transferring spouse; that return reads line 42, not this line."""

T1032_LINE_42 = CATALOG.declare("t1032_line_42", Decimal, non_negative=True)
"""Line 42 of Form T1032, "Line 42: Line 40 plus line 41 Enter the result on line 43700 of the
receiving spouse's or common-law partner's return.": line 40 (the return's own
`ca/income_tax_deducted`) plus line 36, the export for line 43700 of the receiving spouse's
return."""

T1032_FILER_IS_TRANSFERRING_SPOUSE_TOTAL = CATALOG.declare(
    "t1032_filer_is_transferring_spouse_total", int, non_negative=True
)
"""This return is the transferring spouse's, as the return reads it, Form T1032 Step 2 "Line 1 and
line 68020: Enter the amount of eligible pension income that was calculated on line 8 of the
transferring spouse's or common-law partner's Federal Worksheet for line 31400": the first value of
the form's export of the checked answer (`core/first_record_count`), 0 or 1, which the check of
line 1 against line 8 of the return's own Federal Worksheet for line 31400 reads."""

T1032_LINE_1_OF_TRANSFERRING_SPOUSE = CATALOG.declare(
    "t1032_line_1_of_transferring_spouse", Decimal, non_negative=True
)
"""Line 1 of Form T1032 for the transferring spouse's return, "Line 1 and line 68020: Enter the
amount of eligible pension income that was calculated on line 8 of the transferring spouse's or
common-law partner's Federal Worksheet for line 31400": line 1 when this return is the transferring
spouse's, otherwise 0."""

T1032_WORKSHEET_LINE_8_OF_TRANSFERRING_SPOUSE = CATALOG.declare(
    "t1032_worksheet_line_8_of_transferring_spouse", Decimal, non_negative=True
)
"""Line 8 of the Federal Worksheet for line 31400 for the transferring spouse's return, Form T1032
Step 2 "Line 1 and line 68020: Enter the amount of eligible pension income that was calculated on
line 8 of the transferring spouse's or common-law partner's Federal Worksheet for line 31400": line
8 of this return's own worksheet when this return is the transferring spouse's, otherwise 0."""

T1032_LINE_1_OF_TRANSFERRING_SPOUSE_CHECKED = CATALOG.declare(
    "t1032_line_1_of_transferring_spouse_checked", Decimal, non_negative=True
)
"""Line 1 of Form T1032 for the transferring spouse's return, checked, "Line 1 and line 68020:
Enter the amount of eligible pension income that was calculated on line 8 of the transferring
spouse's or common-law partner's Federal Worksheet for line 31400": line 1 refused above line 8 of
the return's own Federal Worksheet for line 31400, not capped."""

T1032_WORKSHEET_LINE_8_OF_TRANSFERRING_SPOUSE_CHECKED = CATALOG.declare(
    "t1032_worksheet_line_8_of_transferring_spouse_checked", Decimal, non_negative=True
)
"""Line 8 of the Federal Worksheet for line 31400 for the transferring spouse's return, checked,
Form T1032 Step 2 "Line 1 and line 68020: Enter the amount of eligible pension income that was
calculated on line 8 of the transferring spouse's or common-law partner's Federal Worksheet for
line 31400": line 8 of the worksheet refused above line 1, not capped, so line 1 is not below it."""

T1032_LINE_4_OF_TRANSFERRING_SPOUSE = CATALOG.declare(
    "t1032_line_4_of_transferring_spouse", Decimal, non_negative=True
)
"""Line 4 of Form T1032 for the transferring spouse's return, "Line 4 and line 68026: Enter the
amount from box 17 of the transferring spouse's or common-law partner's T4A-RCA slips": line 4 when
this return is the transferring spouse's, otherwise 0."""

T1032_OTHER_INCOME_OF_TRANSFERRING_SPOUSE = CATALOG.declare(
    "t1032_other_income_of_transferring_spouse", Decimal, non_negative=True
)
"""Other income of the transferring spouse's return (line 13000 of the T1, where the amounts of the
T4A-RCA slips go), the bound of line 4 of Form T1032 (Guide 5000-G gives box 17 of the T4A-RCA as
"already included in box 16"): the return's other income when it is the transferring spouse's,
otherwise 0."""

T1032_LINE_4_OF_TRANSFERRING_SPOUSE_CHECKED = CATALOG.declare(
    "t1032_line_4_of_transferring_spouse_checked", Decimal, non_negative=True
)
"""Line 4 of Form T1032 for the transferring spouse's return, checked, "Line 4 and line 68026: Enter
the amount from box 17 of the transferring spouse's or common-law partner's T4A-RCA slips": line 4
refused above the return's other income (line 13000, where the T4A-RCA amounts go), not capped."""

T1032_LINE_22_TOTAL = CATALOG.declare("t1032_line_22_total", Decimal, non_negative=True)
"""Line 22 of Form T1032 as the return reads it, "Line 22: Enter the amount that you and your spouse
or common-law partner decide to jointly elect": the total of the form's export of the checked line
22 (`core/record_total`, a record list of one record), which tells whether the election applies."""

T1032_ELECTION_APPLIES = CATALOG.declare("t1032_election_applies", int, non_negative=True)
"""The Form T1032 election applies to this return, 1 or 0: 1 when line 22 is above 0
(`ca/count_by_conditions`). The T1032 is filed only when a split-pension amount is elected, so an
amount of 0 is no election, and the T1 lines 31400 and 43700 are what they were without the form."""

T1032_LINE_39_TOTAL = CATALOG.declare("t1032_line_39_total", Decimal)
"""Line 39 of Form T1032 as the return reads it, "Enter the result on line 43700 of the transferring
spouse's or common-law partner's return": the total of the form's export of line 39
(`core/record_total`, a record list of one record)."""

T1032_LINE_42_TOTAL = CATALOG.declare("t1032_line_42_total", Decimal, non_negative=True)
"""Line 42 of Form T1032 as the return reads it, "Enter the result on line 43700 of the receiving
spouse's or common-law partner's return": the total of the form's export of line 42
(`core/record_total`, a record list of one record)."""

T1032_LINE_43700 = CATALOG.declare("t1032_line_43700", Decimal, non_negative=True)
"""T1 line 150 (line 43700) when the Form T1032 election applies: line 39 on the transferring
spouse's return and line 42 on the receiving spouse's, as this return's answer names."""

T1032_LINE_31400_TRANSFERRING_TOTAL = CATALOG.declare(
    "t1032_line_31400_transferring_total", Decimal, non_negative=True
)
"""Line 31400 of the transferring spouse as the return reads it, Form T1032 Step 4 Part A "Enter on
line 31400 of the transferring spouse's or common-law partner's return, whichever is less: $2,000
or the amount from line 31.": the total of the form's export (`core/record_total`, a record list of
one record)."""

T1032_LINE_31400_RECEIVING_TOTAL = CATALOG.declare(
    "t1032_line_31400_receiving_total", Decimal, non_negative=True
)
"""Line 31400 of the receiving spouse as the return reads it, Form T1032 Step 4 Part B "Enter on
line 31400 of the receiving spouse's or common-law partner's return, whichever is less: $2,000 or
the amount from line 34.": the total of the form's export (`core/record_total`, a record list of
one record)."""

T1032_LINE_31400 = CATALOG.declare("t1032_line_31400", Decimal, non_negative=True)
"""T1 line 31400 when the Form T1032 election applies: the transferring spouse's amount (Part A) on
the transferring spouse's return and the receiving spouse's amount (Part B) on the receiving
spouse's, as this return's answer names. The Federal Worksheet for line 31400 sends the filer to
the form "to calculate the amount to enter on line 31400 of your return instead"."""

T1032_RECEIVING_SPOUSE_UNDER_65 = CATALOG.declare(
    "t1032_receiving_spouse_under_65", int, non_negative=True
)
"""The receiving spouse was under age 65 on December 31, 2025, Form T1032 Step 4 Part B "If all of
the following conditions apply, calculate line 33 according to the instructions in note 1: ... the
receiving spouse or common-law partner was under age 65 on December 31, 2025": the answer, 1 for yes
and 0 for no, a starting count."""

T1032_TRANSFERRING_SPOUSE_65_OR_OLDER = CATALOG.declare(
    "t1032_transferring_spouse_65_or_older", int, non_negative=True
)
"""The transferring spouse was age 65 or older, Form T1032 Step 4 Part B "the transferring spouse or
common-law partner was age 65 or older and received any of the following amounts in the year": the
answer, 1 for yes and 0 for no, a starting count."""

T1032_NOTE_1_PAYMENTS_A_TO_D = CATALOG.declare(
    "t1032_note_1_payments_a_to_d", Decimal, non_negative=True
)
"""The amounts of a) to d) the transferring spouse received, Form T1032 Step 4 Part B "a)
registered retirement income fund (RRIF), registered retirement savings plan (RRSP), or other
annuity payments b) payments (other than life annuity payments) from a money purchase provision of
a registered pension plan (RPP) or a specified pension plan (SPP) c) payments out of a pooled
registered pension plan (PRPP) d) payments out of an advanced life deferred annuity": the total of
a) to d), a starting amount. e) eligible veterans benefits is not entered here: it is the amount
from box 128 of the T4A (`ca/t1032_t4a_box_128`, line 2)."""

T1032_NOTE_1_PAYMENTS_DUE_TO_DEATH = CATALOG.declare(
    "t1032_note_1_payments_due_to_death", Decimal, non_negative=True
)
"""The part of the payments of a) to e) received as a consequence of the death of a spouse or
common-law partner in the year, Form T1032 Note 1 "The receiving spouse or common-law partner does
not need to remove those payments from line 1 if the transferring spouse or common-law partner has
received those payments as a consequence of the death of a spouse or common-law partner in the
year": the total of those payments, a starting amount, refused above the total of a) to e)."""

T1032_RECEIVING_SPOUSE_UNDER_65_CHECKED = CATALOG.declare(
    "t1032_receiving_spouse_under_65_checked", int, non_negative=True
)
"""The receiving spouse was under age 65, checked, Form T1032 Step 4 Part B: 0 or 1, which the
conditions of Note 1 read."""

T1032_TRANSFERRING_SPOUSE_65_OR_OLDER_CHECKED = CATALOG.declare(
    "t1032_transferring_spouse_65_or_older_checked", int, non_negative=True
)
"""The transferring spouse was age 65 or older, checked, Form T1032 Step 4 Part B: 0 or 1, which the
conditions of Note 1 read."""

T1032_NOTE_1_PAYMENTS_DUE_TO_DEATH_CHECKED = CATALOG.declare(
    "t1032_note_1_payments_due_to_death_checked", Decimal, non_negative=True
)
"""The payments received as a consequence of a death, checked, Form T1032 Note 1: refused above the
total of a) to e) (`ca/t1032_note_1_payments_total`), not capped."""

T1032_NOTE_1_PAYMENTS_TOTAL = CATALOG.declare(
    "t1032_note_1_payments_total", Decimal, non_negative=True
)
"""The amounts a) to e) the transferring spouse received, Form T1032 Step 4 Part B: the total of a)
to d) (`ca/t1032_note_1_payments_a_to_d`) plus e) eligible veterans benefits, the amount from box
128 of the T4A that line 2 takes (`ca/t1032_t4a_box_128`)."""

T1032_NOTE_1_PAYMENTS_TO_REMOVE = CATALOG.declare(
    "t1032_note_1_payments_to_remove", Decimal, non_negative=True
)
"""The payments subtracted from line 1, Form T1032 Note 1 "Subtract from line 1 any of the above
amounts noted in a) through e)" but "does not need to remove those payments from line 1 if ... as a
consequence of the death of a spouse": the amounts a) to e) less those received on a death."""

T1032_NOTE_1_LINE_32_LIMIT = CATALOG.declare(
    "t1032_note_1_line_32_limit", Decimal, non_negative=True
)
"""The $2,000 line 32 is compared with, Form T1032 Step 4 Part B "the amount on line 32 is less than
$2,000", from the dataset."""

T1032_NOTE_1_APPLIES = CATALOG.declare("t1032_note_1_applies", int, non_negative=True)
"""Note 1 applies to line 33, 1 or 0, Form T1032 Step 4 Part B "If all of the following conditions
apply, calculate line 33 according to the instructions in note 1": 1 when line 32 is less than
$2,000, the receiving spouse was under 65, and the transferring spouse was 65 or older and received
any of the amounts a) to e) (`ca/count_by_conditions`)."""

T1032_NOTE_1_PAYMENTS_TOTAL_IF_APPLIES = CATALOG.declare(
    "t1032_note_1_payments_total_if_applies", Decimal, non_negative=True
)
"""The amounts a) to e) when Note 1 applies, otherwise 0, Form T1032 Note 1 "Subtract from line 1
any of the above amounts": the amounts are subtracted only when Note 1 asks for it. The form prints
no bound for them against line 1."""

T1032_NOTE_1_PAYMENTS_DUE_TO_DEATH_IF_APPLIES = CATALOG.declare(
    "t1032_note_1_payments_due_to_death_if_applies", Decimal, non_negative=True
)
"""The part of the amounts a) to e) received on a death when Note 1 applies, otherwise 0, Form T1032
Note 1 "does not need to remove those payments from line 1": refused above the amounts a) to e)
only when Note 1 applies."""

T1032_NOTE_1_LINE_29_APPLIES = CATALOG.declare(
    "t1032_note_1_line_29_applies", int, non_negative=True
)
"""Line 29 of Form T1032 recalculated has an amount to multiply, 1 or 0 (`ca/count_by_conditions`),
"Line 28: Amount from line 24": 1 when the recalculated line 22 is above 0."""

T1032_NOTE_1_LINE_8_TO_CHECK = CATALOG.declare(
    "t1032_note_1_line_8_to_check", Decimal, non_negative=True
)
"""Line 8 of Form T1032 (line 25) when line 29 has an amount to multiply, otherwise 0."""

T1032_NOTE_1_LINE_17_IS_ZERO = CATALOG.declare(
    "t1032_note_1_line_17_is_zero", int, non_negative=True
)
"""Line 17 of Form T1032 for the recalculation (line 26), 1 when it is 0, otherwise 0
(`ca/count_by_conditions`). Line 27, "Line 25 divided by line 26", is then a division by 0 and the
form prints no answer."""

T1032_NOTE_1_LINE_8_BOUND = CATALOG.declare("t1032_note_1_line_8_bound", Decimal, non_negative=True)
"""What line 8 of Form T1032 (line 25) may not exceed: 0 when the line 17 of the recalculation is 0,
otherwise line 8 itself, so only a division by 0 is refused."""

T1032_NOTE_1_LINE_8_CHECKED = CATALOG.declare(
    "t1032_note_1_line_8_checked", Decimal, non_negative=True
)
"""Line 8 of Form T1032 (line 25), checked against the line 17 of the recalculation (line 26),
Note 1 "use that result as the amount for line 17": refused only where that line 17 is 0 and line 8
is not, since the form prints no answer for a division by 0."""

T1032_NOTE_1_RESULT = CATALOG.declare("t1032_note_1_result", Decimal)
"""The result of Form T1032 Note 1, "Subtract from line 1 any of the above amounts noted in a)
through e) ... The receiving spouse or common-law partner does not need to remove those payments
from line 1 if the transferring spouse or common-law partner has received those payments as a
consequence of the death of a spouse or common-law partner in the year": line 1 less the amounts, or
line 1 itself when they were received as a consequence of a death."""

T1032_NOTE_1_RESULT_LIMIT = CATALOG.declare("t1032_note_1_result_limit", Decimal, non_negative=True)
"""The $4,000 the result is compared with, Form T1032 Note 1 "If the result is $4,000 or more, enter
on line 33 the amount from line 30. If the result is less than $4,000 ...", from the dataset."""

T1032_NOTE_1_RECALCULATION = CATALOG.declare("t1032_note_1_recalculation", int, non_negative=True)
"""Form T1032 line 33 is recalculated, 1 or 0 (`ca/count_by_conditions`), Note 1 "If the result is
less than $4,000, use that result as the amount for line 17 to recalculate lines 18 to 31": 1 when
Note 1 applies and the result is less than $4,000, 0 when line 33 is line 30."""

T1032_NOTE_1_LINE_17 = CATALOG.declare("t1032_note_1_line_17", Decimal)
"""Line 17 of Form T1032 for the recalculation, Note 1 "use that result as the amount for line 17":
the result of Note 1 when line 33 is recalculated, otherwise line 17."""

T1032_NOTE_1_LINE_22 = CATALOG.declare("t1032_note_1_line_22", Decimal, non_negative=True)
"""Line 22 of Form T1032 for the recalculation, Note 1 "Enter on line 33 whichever is less: the
amount from line 22 or line 30": the elected amount of line 22, already checked against line 21."""

T1032_NOTE_1_LINE_29 = CATALOG.declare("t1032_note_1_line_29", Decimal)
"""Line 29 of Form T1032 recalculated, Note 1 "use that result as the amount for line 17 to
recalculate lines 18 to 31": line 22 times line 8 over the recalculated line 17."""

T1032_NOTE_1_LINE_30 = CATALOG.declare("t1032_note_1_line_30", Decimal)
"""Line 30 of Form T1032 recalculated, Note 1: line 22 less the recalculated line 29."""

T1032_NOTE_1_LINE_33 = CATALOG.declare("t1032_note_1_line_33", Decimal)
"""Line 33 of Form T1032 when it is recalculated, Note 1 "Enter on line 33 whichever is less: the
amount from line 22 or line 30", where line 30 is the recalculated one."""

T1032_NOTE_1_LINE_31 = CATALOG.declare("t1032_note_1_line_31", Decimal)
"""Line 31 of Form T1032 recalculated, Note 1 "use that result as the amount for line 17 to
recalculate lines 18 to 31": line 1 less the recalculated line 30."""

T1032_LINE_31_AFTER_NOTE_1 = CATALOG.declare("t1032_line_31_after_note_1", Decimal)
"""Line 31 of Form T1032 once Note 1 is followed: the recalculated line 31 when lines 18 to 31 are
recalculated, otherwise line 31 as it was."""

T1032_LINE_33 = CATALOG.declare("t1032_line_33", Decimal)
"""Line 33 of Form T1032, "Line 33: Otherwise, enter the amount from line 30", or when the
conditions above it apply the amount Note 1 gives."""
