"""The federal catalog: non-refundable credits.

The CPP, EI and Canada employment amounts, donations and gifts, the top-up credit, the non-
refundable tax credits total, the federal foreign tax credit and the investment tax credit
recapture.
"""

from __future__ import annotations

from decimal import Decimal

from tax_engine.domain.record_list import RecordListKind
from tax_engine.jurisdictions.ca.catalog.base import CATALOG

CPP_BASE_CONTRIBUTIONS = CATALOG.declare("cpp_base_contributions", Decimal, non_negative=True)
"""Base CPP contributions, Schedule 8 Part 3 line 11 "amount from line 7 multiplied by 4.95%
(maximum $3,356.10)": the required contributions on the employment income between the basic
exemption and the maximum pensionable earnings, a part of the total of the credit amounts on the
T1 and, as ON428 line 19 (line 58240) "Amount from line 30800 of your return", on ON428.

Line 15 is "Amount from line 11"; Part 3b line 30 "If line 16 is positive or "0", enter the amount
from line 15 at line 30 and line 36, and continue at line 37." and line 36 "Line 34 plus line 35.
Enter this amount (in dollars and cents) on line 30800 of your return and line 58240 of your Form
428." carry it to T1 line 30800 and ON428 line 58240 when line 24 is "0" or negative
(schedule_8_cpp_base_contributions_on_return). When line 24 is positive, Part 3a line 25 "Enter the
amount from line 15." carries the same amount to the same lines.

Line 1 (50339) is "Total CPP pensionable earnings from box 26 of all of your T4 slips (if box 26
is blank, enter the amount from box 14)", so the three contributions read employment income.
Not triggered by the returns modelled: Part 2's proration for fewer than 12 months, and box 26
differing from box 14. The slips' contributions differing from the required ones are line 24, which
routes to the T1 line 44800 overpayment when positive (schedule_8_cpp_overpayment).
"""

CPP_BASE_CONTRIBUTIONS_ON_SELF_EMPLOYMENT = CATALOG.declare(
    "cpp_base_contributions_on_self_employment", Decimal, non_negative=True
)
"""Base CPP contributions on self-employment income and other earnings, T1 line 87 and line 31000
"on self-employment income and other earnings" under "Base CPP or QPP contributions (complete
Schedule 8 or Form RC381, whichever applies)": Schedule 8 Part 4 line 15, entered once for each
Part 4 completed (1 or 0), a part of the total of the credit amounts on the T1 (ON428 line 20,
line 58280, copies it)."""

EI_PREMIUMS = CATALOG.declare("ei_premiums", Decimal, non_negative=True)
"""EI premiums, T1 line 31200 "through employment (boxes 18 and 55 of all T4 slips) (maximum
$1,077.48)": Form T2204 line 16, a part of the total of the
credit amounts on the T1 and, as ON428 line 21 (line 58300) "Amount from line 31200 of your
return", on ON428.

The premiums deducted (boxes 18 and 55 of the T4 slips) are a caller input of Form T2204 (line 4);
the EI overpayment, T1 line 45000, is `ca/ei_overpayment`.
"""

EI_PREMIUMS_ON_SELF_EMPLOYMENT = CATALOG.declare(
    "ei_premiums_on_self_employment", Decimal, non_negative=True
)
"""EI premiums on self-employment and other eligible earnings, T1 line 89 and line 31217 "on
self-employment and other eligible earnings (complete Schedule 13)" under "Employment insurance
premiums": Schedule 13 line 9 ("Enter the amount from line 9 or line 10, whichever applies, on
line 31217 and line 42120 of your return."), entered once for each agreement with the Commission
(1 or 0), a part of the total of the credit amounts on the T1 (ON428 line 22, line 58305, copies
it)."""

CANADA_EMPLOYMENT_AMOUNT_INCOME = CATALOG.declare(
    "canada_employment_amount_income", Decimal, non_negative=True
)
"""Canada employment amount income, T1 line 31260 "Enter whichever is less: $1,471 or line 1 plus
line 2.": line 1 (line 10100, "Employment income (box 14 of all T4 slips)") plus line 2 (line
10400, "Other employment income"), in line order, the base the cap is applied to.
"""

CANADA_EMPLOYMENT_AMOUNT = CATALOG.declare("canada_employment_amount", Decimal, non_negative=True)
"""Canada employment amount, T1 line 31260 "Enter whichever is less: $1,471 or line 1 plus line
2.": the lesser of the cap and line 1 plus line 2, the fourth part of the total of the credit
amounts on the T1 alone (ON428 has no such line).

Line 1 (10100) is "Employment income (box 14 of all T4 slips)" and line 2 (10400) is "Other
employment income", which is wired from the caller's input, so the cap is applied to both.
"""

CANADIAN_TUITION_FEES = CATALOG.declare("canadian_tuition_fees", Decimal, non_negative=True)
"""Canadian tuition fees, Schedule 11 line 1 and line 32000 "Eligible tuition fees paid to Canadian
educational institutions for 2025 (fees for each institution must be more than $100)": the
student's fees, taken as entered. Lines 2 to 8 read `ca/canadian_tuition_fees_checked`, which
`ca/more_than_per_unit` produces from this total and `ca/canadian_tuition_institutions`."""

CANADIAN_TUITION_INSTITUTIONS = CATALOG.declare(
    "canadian_tuition_institutions", int, non_negative=True
)
"""Number of Canadian educational institutions the fees on Schedule 11 line 1 were paid to, line 1
and line 32000 "(fees for each institution must be more than $100)": a caller count, carried as
entered, which `ca/more_than_per_unit` multiplies by $100 for the minimum of the total."""

CANADIAN_TUITION_FEES_CHECKED = CATALOG.declare(
    "canadian_tuition_fees_checked", Decimal, non_negative=True
)
"""Canadian tuition fees checked, Schedule 11 line 1 and line 32000: `ca/canadian_tuition_fees`
once it is more than $100 for each institution (`ca/more_than_per_unit`); the amount that line 2
and line 6 read."""

CANADA_TRAINING_CREDIT_LIMIT = CATALOG.declare(
    "canada_training_credit_limit", Decimal, non_negative=True
)
"""Canada training credit limit, Schedule 11 line 3 "Your Canada training credit limit from your
latest notice of assessment or reassessment": the limit on the notice, taken as entered."""

CANADA_TRAINING_CREDIT_CLAIMED = CATALOG.declare(
    "canada_training_credit_claimed", Decimal, non_negative=True
)
"""Canada training credit claimed, Schedule 11 "Enter the Canada training credit amount that you
are claiming for 2025 (cannot be more than the amount on line 4).": the filer's election, taken as
entered and held to line 4 when line 5 is computed."""

FOREIGN_TUITION_FEES = CATALOG.declare("foreign_tuition_fees", Decimal, non_negative=True)
"""Foreign tuition fees, Schedule 11 line 7 and line 32001 "Eligible tuition fees paid to foreign
educational institutions for 2025": the student's fees, taken as entered."""

UNUSED_TUITION_FROM_2024 = CATALOG.declare("unused_tuition_from_2024", Decimal, non_negative=True)
"""Unused federal tuition from 2024, Schedule 11 line 9 "Unused federal tuition from your 2024
notice of assessment or reassessment (note 1)": the amount on the notice, taken as entered."""

TUITION_TRANSFER_ELECTED = CATALOG.declare("tuition_transfer_elected", Decimal, non_negative=True)
"""Tuition transfer elected, Schedule 11 line 24 and line 32700 "Enter the amount you are
transferring to a designated individual as shown on your Tuition and Enrolment Certificate (cannot
be more than the amount on line 23).": the filer's election, taken as entered and held to line 23
when line 24 is computed."""

TUITION_TRANSFERRED_FROM_CHILD = CATALOG.declare(
    "tuition_transferred_from_child", Decimal, non_negative=True
)
"""Tuition amount transferred from a child or grandchild, T1 line 104 and line 32400 "Tuition
amount transferred from a child or grandchild": the amount the student designates (the guide's
maximum is $5,000 minus the amount the student used), taken as entered and refused above the bound
of `ca/tuition_transferred_from_child_maximum` (`core/at_most`); the total of the credit amounts on
the T1 (line 33500) reads the checked amount, `ca/tuition_transferred_from_child_checked`."""

TUITION_TRANSFER_STUDENTS = CATALOG.declare("tuition_transfer_students", int, non_negative=True)
"""Number of students the tuition amount transferred from a child or grandchild comes from, T1 line
32400 "Tuition amount transferred from a child or grandchild" (5000-G: "The maximum amount each
student can transfer to you is $5,000 minus the amount that they used to reduce their own tax
payable."; "Only one person can claim this transfer from a student"): a count carried as entered,
which `core/per_unit_amount` multiplies by $5,000 for the bound."""

TUITION_TRANSFERRED_FROM_CHILD_MAXIMUM = CATALOG.declare(
    "tuition_transferred_from_child_maximum", Decimal, non_negative=True
)
"""Maximum tuition amount transferred from a child or grandchild, T1 line 32400 "Tuition amount
transferred from a child or grandchild" (5000-G: "The maximum amount each student can transfer to
you is $5,000 minus the amount that they used to reduce their own tax payable."): the number of
students, `ca/tuition_transfer_students`, times the printed $5,000 for each student
(`core/per_unit_amount`)."""

TUITION_TRANSFERRED_FROM_CHILD_CHECKED = CATALOG.declare(
    "tuition_transferred_from_child_checked", Decimal, non_negative=True
)
"""Tuition amount transferred from a child or grandchild, T1 line 32400, after the check that
`ca/tuition_transferred_from_child` is not more than `ca/tuition_transferred_from_child_maximum`
(`core/at_most`): the amount the total of the credit amounts on the T1 (line 33500) adds. A transfer
above the maximum is refused, not capped."""

CANADA_TRAINING_CREDIT_BASIS = CATALOG.declare(
    "canada_training_credit_basis", Decimal, non_negative=True
)
"""Canada training credit basis, Schedule 11 line 2 "Amount from line 1 multiplied by 50% =":
line 1 (the Canadian tuition fees) times the credit rate."""

CANADA_TRAINING_CREDIT_MAXIMUM = CATALOG.declare(
    "canada_training_credit_maximum", Decimal, non_negative=True
)
"""Canada training credit maximum, Schedule 11 line 4 "Enter whichever is less: amount from line 2
or line 3.": the lesser of the basis and the limit on the notice, which the credit claimed cannot
exceed."""

CANADIAN_TUITION_AVAILABLE = CATALOG.declare(
    "canadian_tuition_available", Decimal, non_negative=True
)
"""Canadian tuition available, Schedule 11 line 6 "Line 1 minus line 5 =": the Canadian fees less
the Canada training credit."""

CURRENT_YEAR_TUITION_AVAILABLE = CATALOG.declare(
    "current_year_tuition_available", Decimal, non_negative=True
)
"""Current-year tuition available, Schedule 11 line 8 "Line 6 plus line 7 =": the Canadian tuition
available plus the foreign fees (line 7, line 32001)."""

TOTAL_TUITION_AVAILABLE = CATALOG.declare("total_tuition_available", Decimal, non_negative=True)
"""Total tuition available, Schedule 11 line 10 "Line 8 plus line 9 =": the current-year tuition
available plus the unused federal tuition from the 2024 notice (line 9)."""

TUITION_INCOME_BASE = CATALOG.declare("tuition_income_base", Decimal, non_negative=True)
"""Income base for the tuition amount, Schedule 11 line 11 "Enter the amount from line 26000 of
your return on line 11 if it is $57,375 or less. If it is more than $57,375, enter the result of
the following calculation: Amount from line 76 of your return divided by 14.5% =": the taxable
income, or the federal basic tax divided by 14.5% above the threshold."""

TOSI_ADJUSTED_TAXABLE_INCOME = CATALOG.declare(
    "tosi_adjusted_taxable_income", Decimal, non_negative=True
)
"""TOSI-adjusted taxable income, Form T1206 Part 2 line 8A "TOSI-adjusted taxable income Amount
from line 8 ÷ 14.5% =": the federal tax on split income divided by 14.5%, which is added to the
amount on line 11 of Schedule 11."""

TUITION_INCOME_WITH_TOSI = CATALOG.declare("tuition_income_with_tosi", Decimal, non_negative=True)
"""Income base for the tuition amount with the TOSI-adjusted taxable income, Schedule 11 line 11
plus Form T1206 line 8A "If you are completing a federal Schedule 11, calculate line 8A and add it
to the amount on line 11 of Schedule 11": the amount that line 13 "Line 11 minus line 12" reads."""

CREDIT_AMOUNTS_SUBTOTAL = CATALOG.declare("credit_amounts_subtotal", Decimal, non_negative=True)
"""Credit amounts subtotal, T1 line 101 "Add lines 98 to 100. =", which Schedule 11 line 12 "Enter
the amount from line 101 of your return" reads: the credit amounts of the lines wired up to line
100 (line 31800), in line order, before line 102 (the tuition amount)."""

TUITION_INCOME_LESS_CREDITS = CATALOG.declare(
    "tuition_income_less_credits", Decimal, non_negative=True
)
"""Income left for the tuition amount, Schedule 11 line 13 "Line 11 minus line 12 (if negative,
enter "0") =": the income base less the credit amounts subtotal, not below zero."""

UNUSED_TUITION_CLAIMED = CATALOG.declare("unused_tuition_claimed", Decimal, non_negative=True)
"""Unused tuition claimed, Schedule 11 line 14 "Enter whichever is less amount from line 9 or line
13.": the lesser of the unused federal tuition from 2024 and the income left."""

TUITION_INCOME_REMAINING = CATALOG.declare("tuition_income_remaining", Decimal, non_negative=True)
"""Income remaining for the tuition amount, Schedule 11 line 15 "Line 13 minus line 14 =": the
income left less the unused tuition claimed."""

CURRENT_YEAR_TUITION_CLAIMED = CATALOG.declare(
    "current_year_tuition_claimed", Decimal, non_negative=True
)
"""Current-year tuition claimed, Schedule 11 line 16 "Enter whichever is less amount from line 8
or line 15.": the lesser of the current-year tuition available and the income remaining."""

FEDERAL_TUITION_AMOUNT = CATALOG.declare("federal_tuition_amount", Decimal, non_negative=True)
"""Federal tuition amount, Schedule 11 line 17 "Line 14 plus line 16 Enter this amount on line
32300 of your return. Your federal tuition amount =", T1 line 103 and line 32300 "Your federal
tuition amount (complete Schedule 11)": a part of the total of the credit amounts on the T1 (line
33500)."""

UNUSED_FEDERAL_TUITION = CATALOG.declare("unused_federal_tuition", Decimal, non_negative=True)
"""Unused federal tuition, Schedule 11 line 20 "Line 18 minus line 19 Total unused federal tuition
amount =": line 18 (the total tuition available, line 10) less line 19 (the federal tuition
amount, line 17)."""

TUITION_TRANSFER_LIMIT = CATALOG.declare("tuition_transfer_limit", Decimal, non_negative=True)
"""Tuition transfer limit, Schedule 11 line 21 "Amount from line 8 of the previous page (maximum
$5,000)": the current-year tuition available, at most $5,000."""

TUITION_AVAILABLE_TO_TRANSFER = CATALOG.declare(
    "tuition_available_to_transfer", Decimal, non_negative=True
)
"""Tuition available to transfer, Schedule 11 line 23 "Unused federal tuition amount available to
transfer": line 21 less line 22 (the current-year tuition claimed, line 16), not below zero."""

TUITION_TRANSFERRED = CATALOG.declare("tuition_transferred", Decimal, non_negative=True)
"""Federal tuition amount transferred, Schedule 11 line 24 and line 32700 "Federal tuition amount
transferred": the amount elected, at most line 23."""

TUITION_CARRIED_FORWARD = CATALOG.declare("tuition_carried_forward", Decimal, non_negative=True)
"""Tuition carried forward, Schedule 11 line 25 "Line 20 minus line 24 Unused federal tuition
amount available to carry forward to a future year =": the unused federal tuition less the amount
transferred. An output of the return: nothing else reads it."""

TUITION_CANNOT_BE_FULL_TIME_STUDENT = CATALOG.declare(
    "tuition_cannot_be_full_time_student", int, non_negative=True
)
"""Cannot be a full-time student because of an impairment, Schedule 11 line 32005 "Tick this box if
you were eligible for the disability tax credit in 2025 or had a mental or physical impairment in
2025 and a medical practitioner has certified that you cannot reasonably be expected to be enrolled
as a full-time student because of the effects of your impairment.": a 0 or 1 tick, carried as
entered, which no step reads."""

TUITION_PART_TIME_MONTHS = CATALOG.declare("tuition_part_time_months", int, non_negative=True)
"""Months enrolled as a part-time student, Schedule 11 line 32010 "Number of months you were
enrolled as a part-time student (box 24 of your Form T2202 and column B of your forms TL11A and
TL11C) (maximum 12)": a count carried as entered, which no step reads. The form's printed maximum
of 12 is not enforced here."""

TUITION_FULL_TIME_MONTHS = CATALOG.declare("tuition_full_time_months", int, non_negative=True)
"""Months enrolled as a full-time student, Schedule 11 line 32020 "Number of months you were
enrolled as a full-time student (box 25 of your Form T2202 and column C of your forms TL11A and
TL11C) (maximum 12)": a count carried as entered, which no step reads. The form's printed maximum
of 12 is not enforced here."""

SPOUSE_RETURN_AGE_AMOUNT = CATALOG.declare("spouse_return_age_amount", Decimal, non_negative=True)
"""Spouse's age amount, Schedule 2 line 1 and line 35200 "Enter the amount from line 30100 of
their return.": a figure from the spouse's return, taken as entered."""

SPOUSE_RETURN_AGE_AMOUNT_MAXIMUM = CATALOG.declare(
    "spouse_return_age_amount_maximum", Decimal, non_negative=True
)
"""Largest spouse's age amount, T1 line 78 "Age amount (if you were born in 1960 or earlier) (use
Federal Worksheet) (maximum $9,028)": the printed maximum of 9028, from a dataset, claimed whole;
an amount above it is refused, not capped."""

SPOUSE_RETURN_AGE_AMOUNT_CHECKED = CATALOG.declare(
    "spouse_return_age_amount_checked", Decimal, non_negative=True
)
"""Spouse's age amount after the check, Schedule 2 line 1 and line 35200 "Enter the amount from
line 30100 of their return.": the amount of `ca/spouse_return_age_amount` after the check that it
is not more than `ca/spouse_return_age_amount_maximum` (`core/at_most`). Line 6 adds this amount."""

SPOUSE_RETURN_INFIRM_CHILDREN_AMOUNT = CATALOG.declare(
    "spouse_return_infirm_children_amount", Decimal, non_negative=True
)
"""Spouse's Canada caregiver amount for infirm children, Schedule 2 line 2 and line 35300 "Enter
the amount from line 30500 of their return.": a figure from the spouse's return, taken as
entered."""

SPOUSE_RETURN_PENSION_INCOME_AMOUNT = CATALOG.declare(
    "spouse_return_pension_income_amount", Decimal, non_negative=True
)
"""Spouse's pension income amount, Schedule 2 line 3 and line 35500 "Enter the amount from line
31400 of their return. (maximum $2,000)": a figure from the spouse's return, taken as entered."""

SPOUSE_RETURN_PENSION_INCOME_AMOUNT_MAXIMUM = CATALOG.declare(
    "spouse_return_pension_income_amount_maximum", Decimal, non_negative=True
)
"""Largest spouse's pension income amount, T1 line 97 "Pension income amount (use Federal
Worksheet) (maximum $2,000)": the printed maximum of 2000, from a dataset, claimed whole; an amount
above it is refused, not capped."""

SPOUSE_RETURN_PENSION_INCOME_AMOUNT_CHECKED = CATALOG.declare(
    "spouse_return_pension_income_amount_checked", Decimal, non_negative=True
)
"""Spouse's pension income amount after the check, Schedule 2 line 3 and line 35500 "Enter the
amount from line 31400 of their return. (maximum $2,000)": the amount of
`ca/spouse_return_pension_income_amount` after the check that it is not more than
`ca/spouse_return_pension_income_amount_maximum` (`core/at_most`). Line 6 adds this amount."""

SPOUSE_RETURN_DISABILITY_AMOUNT = CATALOG.declare(
    "spouse_return_disability_amount", Decimal, non_negative=True
)
"""Spouse's disability amount, Schedule 2 line 4 and line 35700 "Enter the amount from line 31600
of their return. (Note 1)": a figure from the spouse's return, taken as entered."""

SPOUSE_RETURN_DISABILITY_AMOUNT_MAXIMUM = CATALOG.declare(
    "spouse_return_disability_amount_maximum", Decimal, non_negative=True
)
"""Largest spouse's disability amount, Federal Worksheet 5000-D1 line 7 "Enter this amount on line
31600 of your return. (maximum $16,052)": the printed maximum of 16052, from a dataset, claimed
whole; an amount above it is refused, not capped."""

SPOUSE_RETURN_DISABILITY_AMOUNT_CHECKED = CATALOG.declare(
    "spouse_return_disability_amount_checked", Decimal, non_negative=True
)
"""Spouse's disability amount after the check, Schedule 2 line 4 and line 35700 "Enter the amount
from line 31600 of their return. (Note 1)": the amount of `ca/spouse_return_disability_amount`
after the check that it is not more than `ca/spouse_return_disability_amount_maximum`
(`core/at_most`). Line 6 adds this amount."""

SPOUSE_DESIGNATED_TUITION = CATALOG.declare("spouse_designated_tuition", Decimal, non_negative=True)
"""Tuition designated by the spouse, Schedule 2 line 5 and line 36000 "Enter the federal amount
designated to you from their forms T2202, TL11A, or TL11C. (Note 2)": taken as entered."""

SPOUSE_DESIGNATED_TUITION_MAXIMUM = CATALOG.declare(
    "spouse_designated_tuition_maximum", Decimal, non_negative=True
)
"""Largest tuition amount designated by the spouse, Schedule 2 Note 2 "$5,000 minus the current
year amounts they use": the printed maximum of 5000, from a dataset, claimed whole; an amount above
it is refused, not capped. The amounts the spouse uses themselves stay in their figure."""

SPOUSE_DESIGNATED_TUITION_CHECKED = CATALOG.declare(
    "spouse_designated_tuition_checked", Decimal, non_negative=True
)
"""Tuition designated by the spouse after the check, Schedule 2 line 5 and line 36000 "Enter the
federal amount designated to you from their forms T2202, TL11A, or TL11C. (Note 2)": the amount of
`ca/spouse_designated_tuition` after the check that it is not more than
`ca/spouse_designated_tuition_maximum` (`core/at_most`). Line 6 adds this amount."""

SPOUSE_RETURN_TAXABLE_INCOME = CATALOG.declare(
    "spouse_return_taxable_income", Decimal, non_negative=True
)
"""Spouse's taxable income, Schedule 2 line 7 "Enter the amount from line 26000 of their return on
line 7 if it is $57,375 or less.": a figure from the spouse's return, taken as entered."""

SPOUSE_RETURN_FEDERAL_BASIC_TAX = CATALOG.declare(
    "spouse_return_federal_basic_tax", Decimal, non_negative=True
)
"""Spouse's federal tax, Schedule 2 line 7 "amount from line 76 of their return divided by 14.5%
=": a figure from the spouse's return, taken as entered."""

SPOUSE_RETURN_BASIC_PERSONAL_AMOUNT = CATALOG.declare(
    "spouse_return_basic_personal_amount", Decimal, non_negative=True
)
"""Spouse's basic personal amount, Schedule 2 line 8 "Amount from line 30000 of their return": a
figure from the spouse's return, taken as entered."""

SPOUSE_RETURN_BASIC_PERSONAL_AMOUNT_MAXIMUM = CATALOG.declare(
    "spouse_return_basic_personal_amount_maximum", Decimal, non_negative=True
)
"""Largest spouse's basic personal amount, T1 line 77 and line 30000 "(maximum $16,129)": the
printed maximum of 16129, from a dataset, claimed whole; an amount above it is refused, not
capped."""

SPOUSE_RETURN_BASIC_PERSONAL_AMOUNT_CHECKED = CATALOG.declare(
    "spouse_return_basic_personal_amount_checked", Decimal, non_negative=True
)
"""Spouse's basic personal amount after the check, Schedule 2 line 8 "Amount from line 30000 of
their return": the amount of `ca/spouse_return_basic_personal_amount` after the check that it is
not more than `ca/spouse_return_basic_personal_amount_maximum` (`core/at_most`). Line 11 adds this
amount."""

SPOUSE_RETURN_LINE_96 = CATALOG.declare("spouse_return_line_96", Decimal, non_negative=True)
"""Spouse's line 96, Schedule 2 line 9 "Amount from line 96 of their return": a figure from the
spouse's return, taken as entered."""

SPOUSE_RETURN_FEDERAL_TUITION_AMOUNT = CATALOG.declare(
    "spouse_return_federal_tuition_amount", Decimal, non_negative=True
)
"""Spouse's federal tuition amount, Schedule 2 line 10 "Amount from line 32300 of their return": a
figure from the spouse's return, taken as entered."""

SPOUSE_NOT_SEPARATED_90_DAYS = CATALOG.declare(
    "spouse_not_separated_90_days", int, non_negative=True
)
"""Spouse not separated for 90 days, Schedule 2 "If you were separated because of a breakdown in
your relationship for a period of 90 days or more including December 31, 2025, your spouse or
common-law partner cannot transfer any unused amounts to you.": the caller's count, 1 when not
separated and 0 when separated (only 0 or 1 is valid), which line 13 is counted by."""

SPOUSE_NOT_SEPARATED_90_DAYS_CHECKED = CATALOG.declare(
    "spouse_not_separated_90_days_checked", int, non_negative=True
)
"""Spouse not separated for 90 days, Schedule 2: the answer of `ca/spouse_not_separated_90_days`
after the check that it is 0 or 1 (`ca/yes_or_no_count`), a count of 1 or 0. A count of 2 or more is
refused, not capped."""

SPOUSE_TRANSFERABLE_AMOUNTS = CATALOG.declare(
    "spouse_transferable_amounts", Decimal, non_negative=True
)
"""Spouse's transferable amounts, Schedule 2 line 6 "Add lines 1 to 5. =": the spouse's age,
infirm children, pension income and disability amounts and the designated tuition."""

SPOUSE_INCOME_FOR_TRANSFER = CATALOG.declare(
    "spouse_income_for_transfer", Decimal, non_negative=True
)
"""Spouse's income for the transfer, Schedule 2 line 7 "Enter the amount from line 26000 of their
return on line 7 if it is $57,375 or less. If it is more than $57,375, enter the result of the
following calculation: amount from line 76 of their return divided by 14.5% =": their taxable
income, or their federal tax divided by 14.5% above the threshold."""

SPOUSE_CREDITS_USED = CATALOG.declare("spouse_credits_used", Decimal, non_negative=True)
"""Spouse's credits used, Schedule 2 line 11 "Add lines 8 to 10. =": the spouse's basic personal
amount, line 96 and federal tuition amount."""

SPOUSE_ADJUSTED_TAXABLE_INCOME = CATALOG.declare(
    "spouse_adjusted_taxable_income", Decimal, non_negative=True
)
"""Spouse's income left, Schedule 2 line 12 and line 36100 "Line 7 minus line 11 (if negative,
enter "0") =": line 7 less line 11, not below zero."""

SPOUSE_UNUSED_AMOUNTS = CATALOG.declare("spouse_unused_amounts", Decimal, non_negative=True)
"""Spouse's unused amounts, Schedule 2 line 13 "Line 6 minus line 12 (if negative, enter "0")":
line 6 less line 12, not below zero, before the separation rule."""

AMOUNTS_TRANSFERRED_FROM_SPOUSE = CATALOG.declare(
    "amounts_transferred_from_spouse", Decimal, non_negative=True
)
"""Amounts transferred from a spouse, Schedule 2 line 13 "Enter this amount on line 32600 of your
return. Federal amounts transferred from your spouse or common-law partner", T1 line 105 and line
32600 "Amounts transferred from your spouse or common-law partner (complete Schedule 2)": line 13,
or nothing when separated for 90 days or more including December 31, a part of the total of the
credit amounts on the T1 (line 33500)."""

NON_REFUNDABLE_CREDIT_AMOUNTS = CATALOG.declare(
    "non_refundable_credit_amounts", Decimal, non_negative=True
)
"""Total of the non-refundable credit amounts, T1 line 33500 "Line 106 plus line 112": the sum
of the credit amounts the rate is applied to once, here, in line order, the basic personal amount
(line 30000), the age amount (line 78, 30100), the spouse or common-law partner amount (line 79,
30300), the amount for an eligible dependant (line 80, 30400), the Canada caregiver amount for a
spouse or common-law partner (line 81, 30425), the Canada caregiver amount for infirm children
(line 83, 30500), the base CPP contributions (line 30800), the base CPP contributions on
self-employment income (line 31000), the EI premiums (line 31200), the EI premiums on
self-employment income (line 31217), the Canada employment amount (line 31260), the federal
tuition amount (line 32300), the tuition amount transferred from a child or grandchild (line
32400) and the amounts transferred from a spouse or common-law partner (line 32600)."""

CHARITABLE_DONATIONS = CATALOG.declare("charitable_donations", Decimal, non_negative=True)
"""Charitable donations, Schedule 9 line 1 "Donations to registered charities and similar
organizations": the eligible amount on the receipts, with any unused donations of the previous five
years that the filer chooses to claim, a starting amount."""

GOVERNMENT_DONATIONS = CATALOG.declare("government_donations", Decimal, non_negative=True)
"""Government donations, Schedule 9 line 2 (line 32900) "Donations to the Government of Canada, a
province or territory and similar bodies": the eligible amount on the receipts, a starting amount.
"""

UNIVERSITY_DONATIONS_OUTSIDE_CANADA = CATALOG.declare(
    "university_donations_outside_canada", Decimal, non_negative=True
)
"""University donations outside Canada, Schedule 9 line 3 (line 33300) "Donations to registered
universities outside Canada": the eligible amount on the receipts, a starting amount."""

FOREIGN_CHARITY_DONATIONS = CATALOG.declare("foreign_charity_donations", Decimal, non_negative=True)
"""Foreign charity donations, Schedule 9 line 4 (line 33400) "Donations to the United Nations and
its agencies and registered foreign charities": the eligible amount on the receipts, a starting
amount."""

ECOLOGICAL_AND_CULTURAL_GIFTS = CATALOG.declare(
    "ecological_and_cultural_gifts", Decimal, non_negative=True
)
"""Ecological and cultural gifts, Schedule 9 line 11 (line 34200) "Eligible amount of ecological
gifts and cultural gifts (see Guide P113)": a starting amount."""

ECOLOGICAL_GIFTS_BEFORE_2016 = CATALOG.declare(
    "ecological_gifts_before_2016", Decimal, non_negative=True
)
"""Ecological gifts before 2016, Schedule 9 line 15 (line 34210) "Total ecological gifts made after
February 10, 2014, and before 2016 included in the amount on line 11": a starting amount."""

DEPRECIABLE_GIFT_RECAPTURED_DEPRECIATION = CATALOG.declare(
    "depreciable_gift_recaptured_depreciation", Decimal, non_negative=True
)
"""Recaptured depreciation on the depreciable property donated, Schedule 9 chart for line 33700,
line 1 "Amount of recaptured depreciation included on your 2025 return": a starting amount."""

DEPRECIABLE_GIFT_NET_PROCEEDS = CATALOG.declare(
    "depreciable_gift_net_proceeds", Decimal, non_negative=True
)
"""Net proceeds of disposition of the depreciable property donated, Schedule 9 chart for line 33700,
line 2: the net proceeds of disposition of the property donated in 2025, a starting amount for the
one class and property the return claims."""

DEPRECIABLE_GIFT_CAPITAL_COST = CATALOG.declare(
    "depreciable_gift_capital_cost", Decimal, non_negative=True
)
"""Capital cost of the depreciable property donated, Schedule 9 chart for line 33700, line 3: the
capital cost of the property donated in 2025, a starting amount for the one class and property the
return claims."""

CAPITAL_GIFT_TAXABLE_GAINS = CATALOG.declare(
    "capital_gift_taxable_gains", Decimal, non_negative=True
)
"""Taxable capital gains on the capital property donated, Schedule 9 chart for line 33900, line 1
"Amount of current-year taxable capital gains from capital property donated in 2025": a starting
amount."""

CAPITAL_GIFT_GAINS_DEDUCTION = CATALOG.declare(
    "capital_gift_gains_deduction", Decimal, non_negative=True
)
"""Capital gains deduction on the capital property donated, Schedule 9 chart for line 33900, line 2
"Amount of current-year capital gains deduction from capital property donated in 2025": a starting
amount."""

CAPITAL_GIFT_GAINS_DEDUCTION_CHECKED = CATALOG.declare(
    "capital_gift_gains_deduction_checked", Decimal, non_negative=True
)
"""Capital gains deduction after the check, Schedule 9 chart for line 33900, line 2 "Amount of
current-year capital gains deduction from capital property donated in 2025": the amount of
`ca/capital_gift_gains_deduction` after the check that it is not more than
`ca/capital_gift_taxable_gains` (`core/at_most`). Line 3 subtracts this amount."""

DEPRECIABLE_GIFT_PROCEEDS_OR_COST = CATALOG.declare(
    "depreciable_gift_proceeds_or_cost", Decimal, non_negative=True
)
"""Lesser of the proceeds and the cost of the depreciable property donated, Schedule 9 chart for
line 33700, line 4 "Enter whichever is less: amount from line 2 or line 3.": the lesser of the net
proceeds of disposition and the capital cost."""

DEPRECIABLE_GIFTS = CATALOG.declare("depreciable_gifts", Decimal, non_negative=True)
"""Gifts of capital property that are depreciable property, Schedule 9 line B and line 33700, chart
line 5 "Enter whichever is less: amount from line 1 or line 4. Enter this amount on line 33700 of
the previous page.": the lesser of the recaptured depreciation and line 4."""

CAPITAL_PROPERTY_GIFTS = CATALOG.declare("capital_property_gifts", Decimal, non_negative=True)
"""Gifts of capital property, Schedule 9 line C and line 33900, chart line 3 "Line 1 minus Line 2
Enter this amount on line 33900 on the previous page.": the taxable capital gains less the capital
gains deduction."""

TOTAL_CHARITABLE_DONATIONS = CATALOG.declare(
    "total_charitable_donations", Decimal, non_negative=True
)
"""Total eligible amount of charitable donations, Schedule 9 line 5 "Add lines 1 to 4. Total
eligible amount of charitable donations": the sum of the four kinds of donations."""

DONATION_LIMIT_ON_NET_INCOME = CATALOG.declare(
    "donation_limit_on_net_income", Decimal, non_negative=True
)
"""Donation limit on the net income, Schedule 9 line 6 "Enter your net income from line 23600 of
your return. Line A multiplied by 75%": 75% of the net income."""

CAPITAL_GIFTS_TOTAL = CATALOG.declare("capital_gifts_total", Decimal, non_negative=True)
"""Gifts of capital property, Schedule 9 line 7 "Amount B plus amount C Line D": the gifts of
capital property that are depreciable property (line B) plus the gifts of capital property (line C).
"""

CAPITAL_GIFTS_LIMIT_ADDITION = CATALOG.declare(
    "capital_gifts_limit_addition", Decimal, non_negative=True
)
"""Donation limit addition for gifts of capital property, Schedule 9 line 7 "multiplied by 25%": 25%
of line D."""

DONATION_LIMIT_WITH_CAPITAL_GIFTS = CATALOG.declare(
    "donation_limit_with_capital_gifts", Decimal, non_negative=True
)
"""Donation limit with the gifts of capital property, Schedule 9 line 8 "Line 6 plus line 7": line 6
plus line 7."""

CHARITABLE_DONATIONS_LIMIT = CATALOG.declare(
    "charitable_donations_limit", Decimal, non_negative=True
)
"""Total charitable donations limit, Schedule 9 line 9 "Enter whichever is less: amount A or line 8.
Total charitable donations limit": the lesser of the net income (amount A) and line 8."""

CHARITABLE_DONATIONS_CLAIMED = CATALOG.declare(
    "charitable_donations_claimed", Decimal, non_negative=True
)
"""Charitable donations claimed, Schedule 9 line 10 and line 34000 "Enter whichever is less: amount
from line 5 or line 9.": the lesser of the total eligible amount of charitable donations and the
limit."""

DONATIONS_AND_GIFTS_TOTAL = CATALOG.declare("donations_and_gifts_total", Decimal, non_negative=True)
"""Donations and gifts, Schedule 9 line 12 "Line 10 plus line 11": the charitable donations claimed
plus the ecological and cultural gifts."""

DONATION_FIRST_TIER_MAXIMUM = CATALOG.declare(
    "donation_first_tier_maximum", Decimal, non_negative=True
)
"""Donations first tier maximum, Schedule 9 line 13 "Enter whichever is less: amount from line 12 or
$200.": the $200, claimed whole."""

DONATIONS_FIRST_TIER = CATALOG.declare("donations_first_tier", Decimal, non_negative=True)
"""Donations at the first tier, Schedule 9 line 13 "Enter whichever is less: amount from line 12 or
$200." (line H): the lesser of line 12 and $200."""

DONATIONS_OVER_FIRST_TIER = CATALOG.declare("donations_over_first_tier", Decimal, non_negative=True)
"""Donations over the first tier, Schedule 9 line 14 "Line 12 minus line 13" (amount E): line 12
less line 13."""

DONATIONS_OVER_FIRST_TIER_AFTER_2016_GIFTS = CATALOG.declare(
    "donations_over_first_tier_after_2016_gifts", Decimal, non_negative=True
)
"""Donations over the first tier less the ecological gifts before 2016, Schedule 9 line 16 "Line 14
minus line 15 (if negative, enter "0")": line 14 less line 15, not below zero."""

DONATION_HIGH_INCOME_THRESHOLD = CATALOG.declare(
    "donation_high_income_threshold", Decimal, non_negative=True
)
"""Donations high income threshold, Schedule 9 line 18 "Income threshold 253,414.00": the threshold,
claimed whole."""

TAXABLE_INCOME_OVER_DONATION_THRESHOLD = CATALOG.declare(
    "taxable_income_over_donation_threshold", Decimal, non_negative=True
)
"""Taxable income over the donations threshold, Schedule 9 line 19 "Line 17 minus line 18 (if
negative, enter "0")": the taxable income of line 17 (line 26000) less the threshold, not below
zero."""

HIGH_INCOME_DONATIONS = CATALOG.declare("high_income_donations", Decimal, non_negative=True)
"""Donations at the high income rate, Schedule 9 line 20 "Enter whichever is less: amount from line
16 or line 19. Line F": the lesser of line 16 and line 19."""

HIGH_INCOME_DONATION_CREDIT = CATALOG.declare(
    "high_income_donation_credit", Decimal, non_negative=True
)
"""Donations credit at the high income rate, Schedule 9 line 20 "multiplied by 33%": 33% of line F.
"""

REGULAR_RATE_DONATIONS = CATALOG.declare("regular_rate_donations", Decimal, non_negative=True)
"""Donations at the regular rate, Schedule 9 line 21 "Amount E minus amount F Line G": the donations
over the first tier (amount E) less line F."""

REGULAR_RATE_DONATION_CREDIT = CATALOG.declare(
    "regular_rate_donation_credit", Decimal, non_negative=True
)
"""Donations credit at the regular rate, Schedule 9 line 21 "multiplied by 29%": 29% of line G."""

FIRST_TIER_DONATION_CREDIT = CATALOG.declare(
    "first_tier_donation_credit", Decimal, non_negative=True
)
"""Donations credit at the first tier, Schedule 9 line 22 "Amount from line 13 of the previous page
Line H multiplied by 14.5%": 14.5% of line 13."""

DONATIONS_AND_GIFTS_CREDIT = CATALOG.declare(
    "donations_and_gifts_credit", Decimal, non_negative=True
)
"""Donations and gifts credit, Schedule 9 line 23 "Add lines 20 to 22. Enter this amount on line
34900 of your return. Allowable donations for 2025", T1 line 116 (line 34900) "Donations and gifts
(complete Schedule 9)": lines 20, 21 and 22 added."""

CREDIT_AMOUNTS_AT_CREDIT_RATE = CATALOG.declare(
    "credit_amounts_at_credit_rate", Decimal, non_negative=True
)
"""Federal credit amounts at the credit rate, T1 line 115 (line 33800) "Line 113 multiplied by the
percentage from line 114": the total of the credit amounts times the credit rate, the first of the
three lines that line 35000 adds and line 1 of the top-up tax credit worksheet."""

TOP_UP_CREDITS_BASE = CATALOG.declare("top_up_credits_base", Decimal, non_negative=True)
"""Credits for the top-up tax credit, Federal Worksheet "Line 34990 - Top-up tax credit", line 3
"Line 1 plus line 2": line 1 "Amount from line 33800 of your return" plus line 2 "Amount from line
22 of your Schedule 9"."""

TOP_UP_THRESHOLD = CATALOG.declare("top_up_threshold", Decimal, non_negative=True)
"""Top-up tax credit threshold, Federal Worksheet "Line 34990 - Top-up tax credit", line 4
"8,319.38": the threshold, claimed whole."""

TOP_UP_EXCESS = CATALOG.declare("top_up_excess", Decimal, non_negative=True)
"""Credits over the top-up threshold, Federal Worksheet "Line 34990 - Top-up tax credit", line 5
"Line 3 minus line 4 (if negative, enter "0")": line 3 less line 4, not below zero."""

TOP_UP_TAX_CREDIT = CATALOG.declare("top_up_tax_credit", Decimal, non_negative=True)
"""Top-up tax credit, Federal Worksheet "Line 34990 - Top-up tax credit", line 7 "Line 5 multiplied
by the percentage from line 6 Enter this amount on line 34990 of your return.", T1 line 117 (line
34990) "Top-up tax credit (use Federal Worksheet)": line 5 times the 3.45% of line 6."""

NON_REFUNDABLE_TAX_CREDITS = CATALOG.declare(
    "non_refundable_tax_credits", Decimal, non_negative=True
)
"""Federal non-refundable tax credits, T1 line 118 (line 35000) "Add lines 115 to 117. Total
federal non-refundable tax credits": line 115 (line 33800, the total of the credit amounts times the
credit rate), line 116 (line 34900, the donations and gifts credit) and line 117 (line 34990, the
top-up tax credit), in line order."""

FEDERAL_TAX_ON_SPLIT_INCOME = CATALOG.declare(
    "federal_tax_on_split_income", Decimal, non_negative=True
)
"""Federal tax on split income, Form T1206 Part 2 line 8 "Amount from line 7 multiplied by 33%
Enter this amount on line 40424 of your return. Federal tax on split income", line 7 being "Total
split income from line 4": T1 line 120 and line 40424 "Federal tax on split income (TOSI) (complete
Form T1206)"."""

FEDERAL_TAX_WITH_SPLIT_INCOME = CATALOG.declare(
    "federal_tax_with_split_income", Decimal, non_negative=True
)
"""Federal tax with the tax on split income, T1 line 121 and line 40400 "Line 119 plus line 120 =":
the federal basic tax (line 119 "Enter the amount from line 76.") plus the federal tax on split
income (line 120), in line order."""

FEDERAL_TAX_AFTER_CREDITS = CATALOG.declare("federal_tax_after_credits", Decimal, non_negative=True)
"""Basic federal tax, T1 line 126 (line 42900) "Line 121 minus line 125 (if negative, enter "0")
Basic federal tax": line 121 less the credits against it, not below zero.

Line 121 (40400, `federal_tax_with_split_income`) is "Line 119 plus line 120", line 119 "Enter the
amount from line 76." and line 120 (40424, `federal_tax_on_split_income`) the tax on split income;
line 125 is "Add lines 122 to 124.", line 122 "Amount from line 35000", line 123 "Federal
dividend tax credit" and line 124 (40427), the minimum tax carryover applied on Form T691 Part 8
line 12.
"""

T2203_HAS_TAX_ON_SPLIT_INCOME = CATALOG.declare(
    "t2203_has_tax_on_split_income", int, non_negative=True
)
"""You have to pay tax on split income, Form T2203 Part 2 line 5 "If you have to pay tax on split
income, enter the amount from line 22 of your Form T1206. If not, enter "0".": a yes or no count, 1
when the federal tax on split income (Form T1206 line 8) is more than 0, and 0 otherwise."""

T2203_LINE_5 = CATALOG.declare("t2203_line_5", Decimal)
"""Tax on split income, Form T2203 Part 2 line 5 "If you have to pay tax on split income, enter the
amount from line 22 of your Form T1206. If not, enter "0".": line 22 of Form T1206
(`split_income_line_22`) when the count of the condition is 1, and "0" otherwise. Line 22 is
"Line 15 minus line 21" with no "(if negative, enter "0")", so the kind is signed."""

T2203_LINE_6 = CATALOG.declare("t2203_line_6", Decimal, non_negative=True)
"""Amount the surtax is taken on, Form T2203 Part 2 line 6 "Enter whichever is more: amount from
line 4 or line 5.": the greater of line 4 (`federal_tax_after_credits`, the basic federal tax from
line 42900) and line 5 (`t2203_line_5`). Line 4 is not below zero, so neither is line 6."""

T2203_LINE_8 = CATALOG.declare("t2203_line_8", Decimal, non_negative=True)
"""Line 8, Form T2203 Part 2 line 8 "Line 6 multiplied by the percentage from line 7": line 6 times
the percentage of income allocated to "Other (Outside Canada)" from line 52220 of column 5 in Part
1, the caller's figure as printed (25 for 25%), rounded once to the cent. Line 6 and the percentage
are not below zero, so neither is line 8."""

T2203_FEDERAL_SURTAX_OUTSIDE_CANADA = CATALOG.declare(
    "t2203_federal_surtax_outside_canada", Decimal, non_negative=True
)
"""Federal surtax on income allocated to "Other (Outside Canada)", Form T2203 Part 2 line 10 "Line 8
multiplied by the percentage from line 9 (1)": line 8 times the federal surtax rate of line 9, 48%,
rounded once to the cent. Note (1): "For every province and territory, other than Quebec, enter this
amount on line 127 of your return." It is the surtax when you are not subject to minimum tax."""

FEDERAL_SURTAX_OUTSIDE_CANADA = CATALOG.declare("federal_surtax_outside_canada", Decimal)
"""Federal surtax on income earned outside Canada, T1 line 127 "Federal surtax on income earned
outside Canada (complete Form T2203)": line 10 of Form T2203 Part 2
(`t2203_federal_surtax_outside_canada`) when you are not subject to minimum tax
(`amt_subject_to_minimum_tax` is 0), and otherwise Form T691 Part 3 line 4 (`amt_federal_surtax`),
which Form T2203 Part 2 says to calculate instead of lines 4 to 10. Form T691 Part 3 line 4 prints
no floor, so the kind is signed."""

FEDERAL_TAX_WITH_SURTAX = CATALOG.declare("federal_tax_with_surtax", Decimal)
"""Line 128, T1 line 128 "Line 126 plus line 127 =": line 126 (`federal_tax_after_credits`) plus
line 127 (`federal_surtax_outside_canada`). It is the limit of Form T2209 line 13, "The amount on
line 13 should not be more than the total of the amount on line 42900 of your return, plus any
federal surtax on income earned outside of Canada", and the amount that T1 line 130 "Line 128 minus
line 129 =" takes. The form prints no floor on line 127, so the kind is signed."""

ITC_RECAPTURE_EXPENDITURE_AT_15_PERCENT = CATALOG.declare(
    "itc_recapture_expenditure_at_15_percent", Decimal, non_negative=True
)
"""Expenditure on which ITC earned at 15% is recaptured, Form T2038(IND) Part C, line 67193 "Amount
of expenditure on which ITC earned at 15% (after 2013) is recaptured. Do not enter more than the
amount of the original expenditure": the caller's amount, as entered."""

ITC_RECAPTURE_EXPENDITURE_AT_20_PERCENT = CATALOG.declare(
    "itc_recapture_expenditure_at_20_percent", Decimal, non_negative=True
)
"""Expenditure on which ITC earned at 20% is recaptured, Form T2038(IND) Part C, line 67195 "Amount
of expenditure on which ITC earned at 20% (before 2014) is recaptured. Do not enter more than the
amount of the original expenditure": the caller's amount, as entered."""

ITC_RECAPTURE_AT_15_PERCENT = CATALOG.declare(
    "itc_recapture_at_15_percent", Decimal, non_negative=True
)
"""Recapture at 15%, Form T2038(IND) Part C, amount 1: line 67193 "× 0.15 =", the expenditure on
which ITC earned at 15% is recaptured times 0.15."""

ITC_RECAPTURE_AT_20_PERCENT = CATALOG.declare(
    "itc_recapture_at_20_percent", Decimal, non_negative=True
)
"""Recapture at 20%, Form T2038(IND) Part C, amount 2: line 67195 "× 0.20 =", the expenditure on
which ITC earned at 20% is recaptured times 0.20."""

ITC_RECAPTURE = CATALOG.declare("itc_recapture", Decimal, non_negative=True)
"""Recapture of investment tax credit, T1 line 131 "Recapture of investment tax credit (complete
Form T2038(IND))": Part C amount 3 "Total recapture of investment tax credit on SR&ED expenditures
(add amounts 1 and 2)", which the form says to enter on this line."""

FIRST_NATIONS_ABATEMENT = CATALOG.declare("first_nations_abatement", Decimal, non_negative=True)
"""Federal refundable First Nations abatement, Form T2209 note (4) "federal refundable First Nations
abatement (line 44100 of your return)": a starting amount, taken off the basic federal tax of the
foreign tax credit."""

FOREIGN_TAX_CREDIT_NET_INCOME_DEDUCTIONS = CATALOG.declare(
    "foreign_tax_credit_net_income_deductions", Decimal, non_negative=True
)
"""Deductions taken off the net income of Form T2209, note (3) "Net income" "minus any:" the
amounts of lines 24400, 24900, 25000, 25300, 25395 and 25400 of the return and the exempt part of
line 25600, added in the note's order."""

FOREIGN_TAX_CREDIT_NET_INCOME_BEFORE_SPLIT_INCOME = CATALOG.declare(
    "foreign_tax_credit_net_income_before_split_income", Decimal
)
"""Net income before the split income, Form T2209 note (3) "Amount from line 23600 of your return
(or the amount you would have entered if the instructions said "if negative, show in brackets")":
line 23400 less line 23500, not floored, so signed. It is not the line 23600 kind, which is floored
at 0."""

FOREIGN_TAX_CREDIT_NET_INCOME_WITH_SPLIT_INCOME = CATALOG.declare(
    "foreign_tax_credit_net_income_with_split_income", Decimal
)
"""Net income with the split income, Form T2209 note (3) "plus the amount on line 68360 of Form
T1206, Total split income": the amount of note (3) before the split income plus line 68360. It is
the same figure as the TOSI-adjusted net income, which adds line 68360 to line 23400 less line
23500."""

FOREIGN_TAX_CREDIT_NET_INCOME = CATALOG.declare("foreign_tax_credit_net_income", Decimal)
"""Net income for the foreign tax credit, Form T2209 note (3) "Net income (3)": "Amount from line
23600 of your return (or the amount you would have entered if the instructions said "if negative,
show in brackets") plus the amount on line 68360 of Form T1206, Total split income, minus any:"
the listed deductions; the net income with the split income less them. The note prints no "(if
negative, enter "0")", so the result may be negative."""

BASIC_FEDERAL_TAX_WITH_DIVIDEND_CREDIT = CATALOG.declare(
    "basic_federal_tax_with_dividend_credit", Decimal, non_negative=True
)
"""Basic federal tax with the dividend credit, Form T2209 note (4) "Line 42900 of your return plus
any:" "federal dividend tax credit (line 40425 of your return)" (note (8) is this sum alone, for
the business lines): line 42900 (`federal_tax_after_credits`) and line 40425
(`dividend_tax_credit`)."""

BASIC_FEDERAL_TAX_WITH_DIVIDEND_CREDIT_AND_SURTAX = CATALOG.declare(
    "basic_federal_tax_with_dividend_credit_and_surtax", Decimal
)
"""Basic federal tax with the dividend credit and the surtax, Form T2209 note (4) "Basic federal
tax": "Line 42900 of your return plus any:" "federal dividend tax credit (line 40425 of your
return)" and "federal surtax on income allocated to "Other (Outside Canada)" (line 10 of Part 2 of
Form T2203 or 48% of the amount from line 42900 of your return)": the basic federal tax with the
dividend credit (`basic_federal_tax_with_dividend_credit`) plus the surtax on income earned outside
Canada (T1 line 127, `federal_surtax_outside_canada`). The surtax prints no floor, so the sum may be
negative under minimum tax (Form T691 Part 3 line 4); the abatement subtraction of note (4) then
holds the result at 0 (`foreign_tax_credit_basic_federal_tax`)."""

FOREIGN_TAX_CREDIT_BASIC_FEDERAL_TAX = CATALOG.declare(
    "foreign_tax_credit_basic_federal_tax", Decimal, non_negative=True
)
"""Basic federal tax for the foreign tax credit, Form T2209 note (4) "Basic federal tax": the
basic federal tax with the dividend credit and the surtax, the amount of
`basic_federal_tax_with_dividend_credit_and_surtax`, "minus any:" the refundable Quebec abatement
(line 44000 of your return or line 15 of Part 2 of Form T2203), which does not apply to an Ontario
return, and "federal refundable First Nations abatement (line 44100 of your return)"."""

FEDERAL_NON_BUSINESS_FOREIGN_TAX_CREDIT = CATALOG.declare(
    "federal_non_business_foreign_tax_credit", Decimal, non_negative=True
)
"""Federal non-business foreign tax credit, Form T2209 line 3 "Enter whichever is less: the amount
from line 1 or line 2. Federal non-business foreign tax credit": the total of line 3 over the
countries."""

FEDERAL_FOREIGN_TAX_CREDIT = CATALOG.declare(
    "federal_foreign_tax_credit", Decimal, non_negative=True
)
"""Federal foreign tax credit, Form T2209 line 13 "Federal foreign tax credit" and T1 line 129
(line 40500) "Federal foreign tax credit (complete Form T2209)": line 13, the sum of line 11
(`federal_business_foreign_tax_credit`) and line 12 (`federal_non_business_foreign_tax_credit`),
limited as the form says, "The amount on line 13 should not be more than the total of the amount
on line 42900 of your return, plus any federal surtax on income earned outside of Canada", to line
128 (`federal_tax_with_surtax`), line 42900 plus line 127. Line 128 is not above zero only when line
126 is 0 or line 127 is negative (minimum tax, Form T691 Part 3 line 4 prints no floor); then the
credit is 0 (`lesser_of_when_positive`)."""

FEDERAL_TAX_LESS_FOREIGN_TAX_CREDIT = CATALOG.declare(
    "federal_tax_less_foreign_tax_credit", Decimal
)
"""Federal tax less the foreign tax credit, T1 line 130 "Line 128 minus line 129 =": line 128
(`federal_tax_with_surtax`, "Line 126 plus line 127 =") less line 129 (40500), signed (the line
prints no "(if negative, enter "0")"). Line 128 is negative only when line 127 is negative; then the
credit is 0 (`federal_foreign_tax_credit`) and the result is line 128."""

FEDERAL_TAX_WITH_ITC_RECAPTURE = CATALOG.declare("federal_tax_with_itc_recapture", Decimal)
"""Federal tax with the recapture, T1 line 132 "Line 130 plus line 131 =": line 130
(`federal_tax_less_foreign_tax_credit`) and line 131 (`itc_recapture`)."""


CPP_PART_5_BASE_CONTRIBUTIONS_ON_SELF_EMPLOYMENT = CATALOG.declare(
    "cpp_part_5_base_contributions_on_self_employment", Decimal, non_negative=True
)
"""T1 line 31000 from Part 5 line 70, once for each Part 5 completed (1 or 0)."""

CPP_BASE_CONTRIBUTIONS_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS = CATALOG.declare(
    "cpp_base_contributions_on_self_employment_and_other_earnings", Decimal, non_negative=True
)
"""T1 line 31000: the Part 4 amount (cpp_base_contributions_on_self_employment) plus the Part 5
amount, read by 08_non_refundable_credits (twice), 15_ontario_personal_amounts and
16_ontario_credits."""

VOLUNTEER_FIREFIGHTERS_CONDITIONS_MET = CATALOG.declare(
    "volunteer_firefighters_conditions_met", int, non_negative=True
)
"""Volunteer firefighters' conditions met, T1 line 90 (line 31220) "Volunteer firefighters' amount
(VFA)" and the guide's "You can claim $6,000 for the volunteer firefighters' amount (VFA) or search
and rescue volunteers' amount (SRVA), but not both, if you meet all of the following conditions:": a
caller's count, 1 when the conditions are met, else 0."""

VOLUNTEER_FIREFIGHTERS_CONDITIONS_MET_CHECKED = CATALOG.declare(
    "volunteer_firefighters_conditions_met_checked", int, non_negative=True
)
"""Volunteer firefighters' conditions met, T1 line 90 (line 31220): the answer of
`ca/volunteer_firefighters_conditions_met` after the check that it is 0 or 1 (`ca/yes_or_no_count`),
a count of 1 or 0. A count of 2 or more is refused, not capped."""

SEARCH_AND_RESCUE_CONDITIONS_MET = CATALOG.declare(
    "search_and_rescue_conditions_met", int, non_negative=True
)
"""Search and rescue conditions met, T1 line 91 (line 31240) "Search and rescue volunteers' amount
(SRVA)" and the guide's "but not both" condition for the same $6,000: a caller's count, 1 when the
conditions are met, else 0. At most one of the VFA and the SRVA is claimed."""

SEARCH_AND_RESCUE_CONDITIONS_MET_CHECKED = CATALOG.declare(
    "search_and_rescue_conditions_met_checked", int, non_negative=True
)
"""Search and rescue conditions met, T1 line 91 (line 31240): the answer of
`ca/search_and_rescue_conditions_met` after the check that it is 0 or 1 (`ca/yes_or_no_count`), a
count of 1 or 0. A count of 2 or more is refused, not capped."""

VOLUNTEER_FIREFIGHTERS_CREDIT = CATALOG.declare(
    "volunteer_firefighters_credit", Decimal, non_negative=True
)
"""Volunteer firefighters' amount, T1 line 90 (line 31220) "Volunteer firefighters' amount (VFA)":
$6,000 once the conditions are met, else 0; a part of the total of the credit amounts on line
33500."""

SEARCH_AND_RESCUE_CREDIT = CATALOG.declare("search_and_rescue_credit", Decimal, non_negative=True)
"""Search and rescue volunteers' amount, T1 line 91 (line 31240) "Search and rescue volunteers'
amount (SRVA)": $6,000 once the conditions are met, else 0; a part of the total of the credit
amounts on line 33500."""

VOLUNTEER_CREDITS_CLAIMED = CATALOG.declare("volunteer_credits_claimed", Decimal, non_negative=True)
"""The volunteer firefighters' and search and rescue amounts together, T1 lines 31220 and 31240
before the "but not both" maximum: the sum of the VFA and the SRVA, checked against the maximum."""

VOLUNTEER_AMOUNT_MAXIMUM = CATALOG.declare("volunteer_amount_maximum", Decimal, non_negative=True)
"""Volunteer amount maximum, T1 guide 5000-G "You can claim $6,000 for the volunteer firefighters'
amount (VFA) or search and rescue volunteers' amount (SRVA), but not both": the $6,000, the most
the VFA and the SRVA together can be."""

VOLUNTEER_CREDITS_CHECKED = CATALOG.declare("volunteer_credits_checked", Decimal, non_negative=True)
"""Volunteer credits checked, T1 lines 31220 and 31240 "but not both": the VFA and the SRVA together
at most $6,000. Above the maximum the claim is an input error, not capped; a checked side artifact
that is not summed on line 33500."""

HOME_BUYERS_CLAIM = CATALOG.declare("home_buyers_claim", Decimal, non_negative=True)
"""Home buyers' claim, T1 line 93 (line 31270) "Home buyers' amount (maximum $10,000)": the filer's
share of the claim, the amount the filer enters (the split with a spouse is an election), at most
$10,000."""

HOME_BUYERS_MAXIMUM = CATALOG.declare("home_buyers_maximum", Decimal, non_negative=True)
"""Home buyers' maximum, T1 line 93 (line 31270) "Enter $10,000 on line 31270 of your return if you
are not splitting the amount with your spouse or common-law partner": the $10,000, the most the
claim can be."""

HOME_BUYERS_CREDIT = CATALOG.declare("home_buyers_credit", Decimal, non_negative=True)
"""Home buyers' amount, T1 line 93 (line 31270) "Home buyers' amount (maximum $10,000)": the
claim, at most $10,000, a part of the total of the credit amounts on line 33500."""

HOME_ACCESSIBILITY_EXPENSES = CATALOG.declare(
    "home_accessibility_expenses", Decimal, non_negative=True
)
"""Home accessibility expenses, Federal Worksheet for line 31285, line 1 "Total eligible expenses":
the caller's total of the eligible expenses for the home, a starting amount."""

HOME_ACCESSIBILITY_CLAIMED_BY_OTHERS = CATALOG.declare(
    "home_accessibility_claimed_by_others", Decimal, non_negative=True
)
"""Home accessibility claimed by others, Federal Worksheet for line 31285, line 3 "Enter the amount
claimed by other qualifying individuals and eligible individuals living in the same eligible
dwelling from line 31285 of their return": a caller's amount."""

HOME_ACCESSIBILITY_CLAIMED_BY_OTHERS_CHECKED = CATALOG.declare(
    "home_accessibility_claimed_by_others_checked", Decimal, non_negative=True
)
"""Home accessibility claimed by others checked, Federal Worksheet for line 31285, line 3 against
line 2: `ca/home_accessibility_claimed_by_others` at most line 2, since line 4 "Line 2 minus line 3"
prints no "if negative, enter 0". Above line 2 the claim is an input error, not floored; line 4
reads the checked amount."""

HOME_ACCESSIBILITY_LINE_2 = CATALOG.declare("home_accessibility_line_2", Decimal, non_negative=True)
"""Home accessibility line 2, Federal Worksheet for line 31285, line 2 "Enter whichever is less:
amount from line 1 or $20,000.": the lesser of the expenses and the $20,000 maximum."""

HOME_ACCESSIBILITY_CREDIT = CATALOG.declare("home_accessibility_credit", Decimal, non_negative=True)
"""Home accessibility expenses, T1 line 94 (line 31285) "Home accessibility expenses (use Federal
Worksheet) (maximum $20,000)", Federal Worksheet line 4 "Line 2 minus line 3 Enter this amount on
line 31285 of your return": line 2 less the amount claimed by others (checked not to exceed line
2); a part of the total of the credit amounts on line 33500."""

ADOPTION_CHILD_EXPENSES = CATALOG.declare("adoption_child_expenses", Decimal, non_negative=True)
"""Adoption expenses for a child, T1 line 95 (line 31300) "Adoption expenses": a field of each
record of the eligible children, the filer's eligible adoption expenses for that child."""

ADOPTION_EXPENSE_CHILDREN = RecordListKind.declare(
    CATALOG, "adoption_expense_children", fields=(ADOPTION_CHILD_EXPENSES,)
)
"""Adoption expense children, T1 line 95 (line 31300) "Enter on line 31300 of your return the amount
of eligible adoption expenses that you can claim for all eligible children": a starting list with
one record for each eligible child, holding the filer's eligible expenses for that child."""

ADOPTION_CREDIT = CATALOG.declare("adoption_credit", Decimal, non_negative=True)
"""Adoption expenses, T1 line 95 (line 31300) "Adoption expenses": the total of the records of the
eligible children, a part of the total of the credit amounts on line 33500."""

PENSION_FOREIGN_INCOME = CATALOG.declare("pension_foreign_income", Decimal, non_negative=True)
"""Foreign pension income, Federal Worksheet for line 31400, line 2 "Foreign pension income included
in the amount on line 11500 of your return and deducted on line 25600 of your return": a caller's
amount."""

PENSION_FOREIGN_INCOME_CHECKED = CATALOG.declare(
    "pension_foreign_income_checked", Decimal, non_negative=True
)
"""Foreign pension income after the check, Federal Worksheet for line 31400, line 2 "Foreign
pension income included in the amount on line 11500 of your return and deducted on line 25600 of
your return": the amount of `ca/pension_foreign_income` after the check that it is not more than
`ca/additional_deductions_total` (`core/at_most`). Line 2 is part of line 25600, so an amount above
it is an input error, not capped. Line 5 reads this amount."""

PENSION_US_IRA_INCOME = CATALOG.declare("pension_us_ira_income", Decimal, non_negative=True)
"""U.S. IRA income, Federal Worksheet for line 31400, line 3 "Income from a U.S. individual
retirement account (IRA) included in the amount on line 11500 of your return": a caller's amount."""

PENSION_RRIF_TRANSFERRED = CATALOG.declare("pension_rrif_transferred", Decimal, non_negative=True)
"""RRIF or PRPP amounts transferred, Federal Worksheet for line 31400, line 4 "Amounts from a
registered retirement income fund (RRIF) or a pooled registered pension plan (PRPP) included in the
amount on line 11500 of your return and transferred to a registered retirement savings plan (RRSP),
a RRIF, a PRPP, or an annuity": a caller's amount."""

PENSION_ANNUITY_PAYMENTS = CATALOG.declare("pension_annuity_payments", Decimal, non_negative=True)
"""Annuity payments from line 12900, Federal Worksheet for line 31400, line 7 "Annuity payments from
line 12900 of your return (box 16 of all your T4RSP slips)": a caller's amount, counted only when
the conditions are met."""

PENSION_ANNUITY_CONDITIONS_MET = CATALOG.declare(
    "pension_annuity_conditions_met", int, non_negative=True
)
"""Pension annuity conditions met, Federal Worksheet for line 31400, line 7 "only if you were 65
years of age or older on December 31, 2025, or you received the payments because of the death of
your spouse or common-law partner": a caller's 0 or 1 gate on the annuity payments."""

PENSION_ANNUITY_CONDITIONS_MET_CHECKED = CATALOG.declare(
    "pension_annuity_conditions_met_checked", int, non_negative=True
)
"""Pension annuity conditions met, Federal Worksheet for line 31400 line 7: the answer of
`ca/pension_annuity_conditions_met` after the check that it is 0 or 1 (`ca/yes_or_no_count`), a
count of 1 or 0. A count of 2 or more is refused, not capped."""

PENSION_CHART_LINE_1 = CATALOG.declare("pension_chart_line_1", Decimal, non_negative=True)
"""Pension chart line 1, Federal Worksheet for line 31400, line 1 "Amount from line 11500 of your
return": the other pensions and superannuation the filer types plus the Form T2205 amount on line
11500 (`ca/t2205_on_line_11500`, signed), not below zero."""

PENSION_CHART_LINE_5 = CATALOG.declare("pension_chart_line_5", Decimal, non_negative=True)
"""Pension chart line 5, Federal Worksheet for line 31400, line 5 "Add lines 2 to 4.": the foreign
pension income, the U.S. IRA income and the RRIF or PRPP amounts transferred."""

PENSION_CHART_LINE_5_CHECKED = CATALOG.declare(
    "pension_chart_line_5_checked", Decimal, non_negative=True
)
"""Pension chart line 5 after the check, Federal Worksheet for line 31400, line 1 "Amount from line
11500 of your return": the amount of `ca/pension_chart_line_5` after the check that it is not more
than `ca/pension_chart_line_1` (`core/at_most`). Line 6 reads this amount."""

PENSION_CHART_LINE_6 = CATALOG.declare("pension_chart_line_6", Decimal, non_negative=True)
"""Pension chart line 6, Federal Worksheet for line 31400, line 6 "Line 1 minus line 5": the amount
from line 11500 less line 5, not below zero."""

PENSION_CHART_LINE_7 = CATALOG.declare("pension_chart_line_7", Decimal, non_negative=True)
"""Pension chart line 7, Federal Worksheet for line 31400, line 7 "Annuity payments from line 12900
of your return": the annuity payments once when the conditions are met, else 0."""

PENSION_CHART_LINE_8 = CATALOG.declare("pension_chart_line_8", Decimal, non_negative=True)
"""Pension chart line 8, Federal Worksheet for line 31400, line 8 "Line 6 plus line 7": the sum of
line 6 and line 7."""

PENSION_WORKSHEET_AMOUNT = CATALOG.declare("pension_worksheet_amount", Decimal, non_negative=True)
"""Pension income amount by the Federal Worksheet for line 31400, last line "Enter on line 31400 of
your return whichever amount is less: line 8 or $2,000.": the lesser of line 8 and $2,000, the
amount for line 31400 when the filer does not elect to split the pension."""

PENSION_INCOME_CREDIT = CATALOG.declare("pension_income_credit", Decimal, non_negative=True)
"""Pension income amount, T1 line 97 (line 31400) "Pension income amount (use Federal Worksheet)
(maximum $2,000)": the Form T1032 amount when the filer elects to split the pension, else the
lesser of line 8 of the Federal Worksheet and $2,000, a part of the total of the credit amounts on
line 33500."""

STUDENT_LOAN_INTEREST = CATALOG.declare("student_loan_interest", Decimal, non_negative=True)
"""Interest paid on student loans, T1 line 102 (line 31900) "Interest paid on your student loans (go
to canada.ca/taxes-students)": the eligible amount of interest the filer paid, a part of the total
of the credit amounts on line 33500."""
