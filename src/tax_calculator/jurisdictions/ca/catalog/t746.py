"""The federal catalog: Form T746 (2025), "Calculating Your Deduction for Refund of Unused RRSP,
PRPP, and SPP Contributions", lines 1 to 13, in a row form and a summary form.

The row form `ca/t746_year` is the form's lines 1 to 4 filled in for one year of unused
contributions ("fill out a separate Form T746, lines 1 to 4 only, for each year"), run once for
each record of its list `ca/t746_years`. The summary form `ca/t746` runs once: it adds the line 4
amounts of all years, takes the withdrawals of lines 6 to 10, adds them at line 12 and gives line
13, the lesser of lines 4 and 12, which is the deduction for T1 line 23200. Line 11 (the amount
from Form T2205) is left out until Form T2205 is built (it is a figure that form computes, not one
the filer re-types). Line 5, the year of the withdrawal, is entered and read by no step. The two
conditions printed under "For you to claim the deduction" are the filer's yes or no answers, a
count of 1 or 0, and a deduction is allowed when at least one holds."""

from __future__ import annotations

from decimal import Decimal

from tax_calculator.domain.record_list import RecordListKind
from tax_calculator.jurisdictions.ca.catalog.base import CATALOG

T746_CONTRIBUTION_YEAR = CATALOG.declare("t746_contribution_year", int, non_negative=True)
"""Year the unused contributions were made, Form T746 line 1 "Enter the year you made the unused
RRSP, PRPP, and SPP contributions": the year the filer enters for each record, read by no step."""

T746_CONTRIBUTIONS = CATALOG.declare("t746_contributions", Decimal, non_negative=True)
"""Total contributions, Form T746 line 2 "Enter the total contributions you made to your RRSPs,
PRPPs, or SPP and your spouse's or common-law partner's RRSPs or SPP in the year shown on line 1":
the amount the filer enters for each record, a starting amount."""

T746_CONTRIBUTIONS_DEDUCTED = CATALOG.declare(
    "t746_contributions_deducted", Decimal, non_negative=True
)
"""Contributions deducted, Form T746 line 3 "Enter the part of the amount from line 2 that you
deducted or will be deducting on your income tax and benefit return for any year": the amount the
filer enters for each record, a starting amount, a part of line 2 and so refused above it by
`ca/t746_contributions_deducted_checked`."""

T746_CONTRIBUTIONS_DEDUCTED_CHECKED = CATALOG.declare(
    "t746_contributions_deducted_checked", Decimal, non_negative=True
)
"""Line 3 of Form T746 as checked: the part deducted, at most the total of line 2 (the form prints
no bound of its own; the part never exceeds the whole, so an amount above line 2 is refused, not
capped)."""

T746_UNUSED_CONTRIBUTIONS_OF_YEAR = CATALOG.declare(
    "t746_unused_contributions_of_year", Decimal, non_negative=True
)
"""Unused contributions of one year, Form T746 line 4 "Line 2 minus line 3": the unused RRSP, PRPP
and SPP contributions for the year shown on line 1, the export of the row form."""

T746_YEARS = RecordListKind.declare(
    CATALOG,
    "t746_years",
    fields=(T746_CONTRIBUTION_YEAR, T746_CONTRIBUTIONS, T746_CONTRIBUTIONS_DEDUCTED),
)
"""Years of unused contributions, Form T746 lines 1 to 3: a starting list with one record for each
year, holding line 1, line 2 and line 3. The row form `ca/t746_year` runs once for each record."""

T746_UNUSED_CONTRIBUTIONS = CATALOG.declare("t746_unused_contributions", Decimal, non_negative=True)
"""Unused contributions of all years, Form T746 line 4 "Line 2 minus line 3" on the most recent
form: "enter the total of the amounts from line 4 for all years on line 4 of the most recent Form
T746", the total of the row form's line 4 over its records."""

T746_WITHDRAWAL_YEAR = CATALOG.declare("t746_withdrawal_year", int, non_negative=True)
"""Year of the withdrawal, Form T746 line 5 "Enter the year you or your spouse or common-law
partner withdrew the unused RRSP, PRPP, or SPP contributions": the year the filer enters, read by
no step."""

T746_T4RSP_BOX_20 = CATALOG.declare("t746_t4rsp_box_20", Decimal, non_negative=True)
"""Unused RRSP contributions refunded, Form T746 line 6 "Enter the amount shown in box 20 of your
T4RSP slips": the amount the filer enters, one total for all the slips, a starting amount."""

T746_T4RSP_BOX_22 = CATALOG.declare("t746_t4rsp_box_22", Decimal, non_negative=True)
"""Withdrawal from an RRSP, Form T746 line 7 "Enter the amount shown in box 22 of your T4RSP
slips" (not an amount designated as a qualifying withdrawal on Form T1006): the amount the filer
enters, one total for all the slips, a starting amount."""

T746_T4RIF_BOX_24 = CATALOG.declare("t746_t4rif_box_24", Decimal, non_negative=True)
"""Withdrawal from a RRIF, Form T746 line 8 "Enter the amount shown in box 24 of your T4RIF
slips": the amount the filer enters, one total for all the slips, a starting amount."""

T746_T4A_BOX_194 = CATALOG.declare("t746_t4a_box_194", Decimal, non_negative=True)
"""Lump sum PRPP withdrawals, Form T746 line 9 "Enter the amount of lump sum PRPP withdrawals
included in box 194 of your T4A slips": the amount the filer enters, a starting amount."""

T746_T4A_BOX_18_SPP = CATALOG.declare("t746_t4a_box_18_spp", Decimal, non_negative=True)
"""Withdrawal from an SPP, Form T746 line 10 "Enter the amount shown in box 18 of your T4A slips
only if this amount is a withdrawal from your SPP": the amount the filer enters, a starting
amount."""

T746_WITHDRAWALS = CATALOG.declare("t746_withdrawals", Decimal, non_negative=True)
"""Total withdrawals, Form T746 line 12 "Add lines 6 to 11": the RRSP, RRIF, PRPP and SPP amounts
withdrawn in the year shown on line 5 and included in income; line 11 is not added yet (see the
module note)."""

T746_EXPECTED_TO_FULLY_DEDUCT_CONTRIBUTIONS = CATALOG.declare(
    "t746_expected_to_fully_deduct_contributions", int, non_negative=True
)
"""Expected to fully deduct the contributions, Form T746 "For you to claim the deduction, it has to
be reasonable for the CRA to consider that one or both of the following conditions apply: you
expected to be able to fully deduct your RRSP, PRPP, or SPP contributions in the year you made
them or the year before": the answer to a yes or no question, a count of 1 or 0, checked before
the step that reads it (`ca/t746_expected_to_fully_deduct_contributions_checked`)."""

T746_DID_NOT_MAKE_CONTRIBUTIONS_INTENDING_TO_WITHDRAW = CATALOG.declare(
    "t746_did_not_make_contributions_intending_to_withdraw", int, non_negative=True
)
"""Did not make the contributions intending to withdraw them, Form T746 "it has to be reasonable
for the CRA to consider that one or both of the following conditions apply: you did not make the
contributions intending to withdraw them later and claim the deduction": the answer to a yes or no
question, a count of 1 or 0, checked before the step that reads it
(`ca/t746_did_not_make_contributions_intending_to_withdraw_checked`)."""

T746_EXPECTED_TO_FULLY_DEDUCT_CONTRIBUTIONS_CHECKED = CATALOG.declare(
    "t746_expected_to_fully_deduct_contributions_checked", int, non_negative=True
)
"""Expected to fully deduct the contributions (Form T746), after the check that the count is 0 or 1
(`ca/yes_or_no_count`)."""

T746_DID_NOT_MAKE_CONTRIBUTIONS_INTENDING_TO_WITHDRAW_CHECKED = CATALOG.declare(
    "t746_did_not_make_contributions_intending_to_withdraw_checked", int, non_negative=True
)
"""Did not make the contributions intending to withdraw them (Form T746), after the check that the
count is 0 or 1 (`ca/yes_or_no_count`)."""

T746_CONDITIONS_MET = CATALOG.declare("t746_conditions_met", int, non_negative=True)
"""Eligibility of Form T746, "one or both of the following conditions apply": 1 when at least one of
the two answers is yes, else 0 (`ca/count_by_conditions`)."""

T746_LINE_13 = CATALOG.declare("t746_line_13", Decimal, non_negative=True)
"""Form T746 line 13 "Enter the amount from line 4 or the amount from line 12, whichever is less",
before the conditions: the lesser of the two lines."""

T746_DEDUCTION = CATALOG.declare("t746_deduction", Decimal, non_negative=True)
"""Deduction, Form T746 line 13 "This is your deduction. Enter this amount on line 23200 of your
income tax and benefit return", for "you to claim the deduction" with one or both conditions
met: line 13 when they are, else 0. The export of the summary form, read by T1 line 23200."""

T746_DEDUCTION_ON_RETURN = CATALOG.declare("t746_deduction_on_return", Decimal, non_negative=True)
"""Deduction of Form T746 on the return, T1 line 23200 "Other deductions": line 13 of the form (the
one record of `ca/t746`, totalled), a part of the line 23200 sum beside the caller's other
deductions."""
