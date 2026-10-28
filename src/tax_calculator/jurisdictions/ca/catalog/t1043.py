"""The federal catalog: Form T1043 (2025), "Deduction for Excess Registered Pension Plan Transfers
You Withdrew from an RRSP, a PRPP, an SPP, or a RRIF", lines 1 to 9, in one form.

The form `ca/t1043` runs once. Line 1 is the lesser of the excess transfer shown on the T4A slips
and the excess amount shown on the receipt ("whichever is less"); line 4 is line 2 plus line 3;
line 5 is line 1 minus line 4; line 8 is line 6 minus line 7; line 9, the lesser of lines 5 and 8,
is the amount the form allows for T1 line 23200 once the filer has answered the two conditions
the form prints under "To claim the deduction, you have to meet both of the following conditions"
(each a yes or no answer, a count of 1 or 0; a "no" to either leaves a deduction of $0). The
"Year(s)" box above line 1 is not a numbered line and no figure depends on it, so it is not
entered."""

from __future__ import annotations

from decimal import Decimal

from tax_calculator.jurisdictions.ca.catalog.base import CATALOG

T1043_INCLUDED_EXCESS_IN_INCOME_FOR_YEAR_TRANSFERRED = CATALOG.declare(
    "t1043_included_excess_in_income_for_year_transferred", int, non_negative=True
)
"""Form T1043 "To claim the deduction, you have to meet both of the following conditions": "You
included the excess amount that was transferred to your RRSP, PRPP, SPP, or RRIF in your income for
the year it was transferred": the answer to a yes or no question, a count of 1 or 0, checked before
the step that reads it (`ca/t1043_included_excess_in_income_for_year_transferred_checked`)."""

T1043_INCLUDING_PLAN_AMOUNTS_IN_INCOME_FOR_YEAR_CLAIMED = CATALOG.declare(
    "t1043_including_plan_amounts_in_income_for_year_claimed", int, non_negative=True
)
"""Form T1043 "To claim the deduction, you have to meet both of the following conditions": "You are
including amounts received from your RRSPs, PRPPs, SPP, or RRIFs in your income for the year you are
claiming this deduction": the answer to a yes or no question, a count of 1 or 0, checked before the
step that reads it (`ca/t1043_including_plan_amounts_in_income_for_year_claimed_checked`)."""

T1043_EXCESS_TRANSFER_ON_T4A = CATALOG.declare(
    "t1043_excess_transfer_on_t4a", Decimal, non_negative=True
)
"""Excess transfer on the T4A slips, Form T1043 line 1 "Enter the amount of the excess transfer
shown on your T4A slip(s) and included in your income for the above year(s)": the amount the filer
enters, one total for the year(s), a starting amount."""

T1043_EXCESS_AMOUNT_ON_RECEIPT = CATALOG.declare(
    "t1043_excess_amount_on_receipt", Decimal, non_negative=True
)
"""Excess amount on the receipt, Form T1043 line 1 "the excess amount shown on your RRSP, PRPP, or
SPP receipt": the amount the filer enters, a starting amount. A filer with only one of the two
figures enters it in both boxes, as an unentered box counts as 0 and line 1 is the lesser."""

T1043_EXCESS_TRANSFERRED = CATALOG.declare("t1043_excess_transferred", Decimal, non_negative=True)
"""Excess transferred, Form T1043 line 1 "Enter the amount of the excess transfer shown on your T4A
slip(s) and included in your income for the above year(s) or the excess amount shown on your RRSP,
PRPP, or SPP receipt, whichever is less": the lesser of the two amounts entered."""

T1043_CLAIMED_AS_RRSP_DEDUCTION = CATALOG.declare(
    "t1043_claimed_as_rrsp_deduction", Decimal, non_negative=True
)
"""Claimed as an RRSP deduction, Form T1043 line 2 "Enter the part of the amount from line 1 that
you claimed as an RRSP deduction for any previous year": the amount the filer enters, a starting
amount."""

T1043_DEDUCTED_USING_FORM = CATALOG.declare("t1043_deducted_using_form", Decimal, non_negative=True)
"""Deducted using this form, Form T1043 line 3 "Enter the part of the amount from line 1 that you
deducted using this form for any previous year": the amount the filer enters, a starting amount."""

T1043_PREVIOUSLY_CLAIMED = CATALOG.declare("t1043_previously_claimed", Decimal, non_negative=True)
"""Previously claimed, Form T1043 line 4 "Line 2 plus line 3": the sum of lines 2 and 3, before the
check that it is no more than line 1."""

T1043_PREVIOUSLY_CLAIMED_CHECKED = CATALOG.declare(
    "t1043_previously_claimed_checked", Decimal, non_negative=True
)
"""Line 4 of Form T1043 as checked: lines 2 and 3 are parts of line 1 ("the part of the amount from
line 1"), so their sum is at most line 1; an amount above it is refused, not capped."""

T1043_NOT_YET_CLAIMED = CATALOG.declare("t1043_not_yet_claimed", Decimal, non_negative=True)
"""Excess amounts not yet claimed, Form T1043 line 5 "Line 1 minus line 4": the transferred excess
amounts that are not already claimed as an RRSP deduction or deducted using this form."""

T1043_PLAN_AMOUNTS_IN_INCOME = CATALOG.declare(
    "t1043_plan_amounts_in_income", Decimal, non_negative=True
)
"""Plan amounts in income, Form T1043 line 6 "Enter the total of all RRSP, PRPP, SPP, and RRIF
amounts that you included in your income for the current tax year": the amount the filer enters, a
starting amount."""

T1043_PART_DEDUCTIBLE_ELSEWHERE = CATALOG.declare(
    "t1043_part_deductible_elsewhere", Decimal, non_negative=True
)
"""Part deductible elsewhere, Form T1043 line 7 "Enter the part of the amount from line 6 that you
can deduct as a transfer after the maturity of an RRSP, as an excess amount from a RRIF that was
transferred to an annuity, or as an unused contribution that you withdrew": the amount the filer
enters, a starting amount, a part of line 6."""

T1043_PART_DEDUCTIBLE_ELSEWHERE_CHECKED = CATALOG.declare(
    "t1043_part_deductible_elsewhere_checked", Decimal, non_negative=True
)
"""Line 7 of Form T1043 as checked: "the part of the amount from line 6", so at most line 6; an
amount above it is refused, not capped."""

T1043_PLAN_AMOUNTS_REMAINING = CATALOG.declare(
    "t1043_plan_amounts_remaining", Decimal, non_negative=True
)
"""Plan amounts remaining, Form T1043 line 8 "Line 6 minus line 7": the plan amounts in income that
are not deductible elsewhere."""

T1043_INCLUDED_EXCESS_IN_INCOME_FOR_YEAR_TRANSFERRED_CHECKED = CATALOG.declare(
    "t1043_included_excess_in_income_for_year_transferred_checked", int, non_negative=True
)
"""Form T1043 condition, included the excess amount in income for the year it was transferred, after
the check that the count is 0 or 1 (`ca/yes_or_no_count`)."""

T1043_INCLUDING_PLAN_AMOUNTS_IN_INCOME_FOR_YEAR_CLAIMED_CHECKED = CATALOG.declare(
    "t1043_including_plan_amounts_in_income_for_year_claimed_checked", int, non_negative=True
)
"""Form T1043 condition, including the amounts received from the plans in income for the year of
the claim, after the check that the count is 0 or 1 (`ca/yes_or_no_count`)."""

T1043_LINE_9 = CATALOG.declare("t1043_line_9", Decimal, non_negative=True)
"""Form T1043 line 9 "Enter the amount from line 5 or line 8, whichever is less", before the two
conditions "you have to meet both of the following conditions"."""

T1043_LINE_9_IF_EXCESS_INCLUDED = CATALOG.declare(
    "t1043_line_9_if_excess_included", Decimal, non_negative=True
)
"""Form T1043 line 9 when the filer "included the excess amount that was transferred to your RRSP,
PRPP, SPP, or RRIF in your income for the year it was transferred": line 9 when the answer is yes,
else 0."""

T1043_DEDUCTION = CATALOG.declare("t1043_deduction", Decimal, non_negative=True)
"""Deduction, Form T1043 line 9 "Enter the amount from line 5 or line 8, whichever is less. You can
deduct this amount on line 23200 of your income tax and benefit return", for a filer who meets
"both of the following conditions" (the line 9 amount when both answers are yes, else 0): the
export of the form, read by T1 line 23200."""

T1043_DEDUCTION_ON_RETURN = CATALOG.declare("t1043_deduction_on_return", Decimal, non_negative=True)
"""Deduction of Form T1043 on the return, T1 line 23200 "Other deductions": line 9 of the form (the
one record of `ca/t1043`, totalled), a part of the line 23200 sum beside the caller's other
deductions."""
