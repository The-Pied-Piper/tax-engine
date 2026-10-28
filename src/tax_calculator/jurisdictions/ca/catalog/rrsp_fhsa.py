"""The federal catalog: the RRSP and FHSA deductions.

The RPP deduction, the RRSP contribution, limit and deduction lines, and the FHSA contribution,
transfer, limit and deduction lines.
"""

from __future__ import annotations

from decimal import Decimal

from tax_calculator.jurisdictions.ca.catalog.base import CATALOG

PENSION_ADJUSTMENT = CATALOG.declare("pension_adjustment", Decimal, non_negative=True)
"""Pension adjustment, T1 line 20600 "Pension adjustment (box 52 of all T4 slips and box 034 of all
T4A slips)": a memo carried as entered, which no step reads."""

RPP_DEDUCTION = CATALOG.declare("rpp_deduction", Decimal, non_negative=True)
"""Registered pension plan (RPP) deduction, T1 line 35 and line 20700 "Registered pension plan
(RPP) deduction (box 20 of all T4 slips and box 032 of all T4A slips)": the amount claimed, a
starting amount, used as typed. Guide 5000-G line 20700 sends the limit to Guide T4040, which is not
in the repo, for more than $3,500 contributed with a past-service amount for service before 1990 on
the slips, and for a previous-year amount for a period before 1990 not fully deducted; those cases
are not modelled."""

UNUSED_RRSP_CONTRIBUTIONS = CATALOG.declare("unused_rrsp_contributions", Decimal, non_negative=True)
"""Unused RRSP contributions, Schedule 7 line 1 "Enter your unused RRSP contributions previously
reported and available to deduct for 2025 as shown on your latest notice of assessment or
reassessment, or Form T1028 for 2025": the contributions previously reported and not yet
deducted, a starting amount."""

RRSP_CONTRIBUTIONS = CATALOG.declare("rrsp_contributions", Decimal, non_negative=True)
"""RRSP contributions, Schedule 7 line 4 (line 24500) "Line 2 plus line 3": the contributions made
from March 4, 2025, to March 2, 2026, a starting amount.

Line 2 is "Enter contributions made to your RRSP, SPP or PRPP, or to your spouse's or common-law
partner's RRSP or SPP from March 4, 2025, to December 31, 2025 (attach all receipts)."; line 3 is
the same contributions "from January 1, 2026, to March 2, 2026".
"""

RRSP_CONTRIBUTIONS_AVAILABLE = CATALOG.declare(
    "rrsp_contributions_available", Decimal, non_negative=True
)
"""RRSP contributions available to deduct, Schedule 7 line 10 "Line 6 minus line 9 Contributions
available to deduct": the unused contributions plus the contributions.

Line 5 is "Line 1 plus line 4 ... Total contributions"; line 6 "Total contributions from line 5".
With line 9 at 0, line 10 is line 5. Not triggered by the returns modelled: HBP and LLP repayments
(lines 7 to 9).
"""

RRSP_DEDUCTION_LIMIT = CATALOG.declare("rrsp_deduction_limit", Decimal, non_negative=True)
"""RRSP deduction limit, Schedule 7 line 11 "Enter your RRSP deduction limit for 2025 as shown on
your latest notice of assessment or reassessment, or Form T1028 for 2025.": a starting amount."""

RRSP_DEDUCTION_MAXIMUM = CATALOG.declare("rrsp_deduction_maximum", Decimal, non_negative=True)
"""RRSP deduction maximum, Schedule 7 line 17 "Enter whichever is less: amount from line 13 or line
16.": the lesser of the contributions available to deduct and the deduction limit, the most that
may be deducted.

Line 13 is "Line 11 minus line 12"; line 16 "Line 14 minus line 15". With lines 12 and 15 at 0,
line 13 is the limit and line 16 the contributions available to deduct. Not triggered by the
returns modelled: employer PRPP contributions (line 12) and transfers (line 15).
"""

RRSP_AMOUNT_DEDUCTED = CATALOG.declare("rrsp_amount_deducted", Decimal, non_negative=True)
"""RRSP amount deducted, Schedule 7 line 18 "Enter your RRSP, PRPP, or SPP contributions you are
deducting for 2025 (cannot be more than the amount on line 17).": the amount the filer chooses to
deduct, a starting amount, refused when above line 17."""

RRSP_DEDUCTION = CATALOG.declare("rrsp_deduction", Decimal, non_negative=True)
"""RRSP deduction, Schedule 7 line 20 "Enter whichever is less: amount from line 10 or line 19.
Enter this amount on line 20800 of your return. RRSP deduction": the amount deducted, at most the
deduction maximum, the T1 line 20800 deduction from total income.

Line 19 is "Line 15 plus line 18". With line 15 at 0, line 19 is line 18, at most line 17 and so
at most line 10, and line 20 is line 18 itself. Not triggered by the returns modelled: transfers
(line 15).
"""

UNUSED_RRSP_CONTRIBUTIONS_CARRIED_FORWARD = CATALOG.declare(
    "unused_rrsp_contributions_carried_forward", Decimal, non_negative=True
)
"""Unused RRSP contributions carried forward, Schedule 7 line 23 "Line 21 minus line 22 Your unused
contributions available to carry forward to a future year": the contributions available to deduct
less the RRSP deduction, a product of the return for the next year's line 1.

Line 21 is "Enter your contributions available to deduct from line 10 of the previous page."; line
22 "Enter your RRSP deduction from line 20 of the previous page.". Never negative, as line 20 is
at most line 10.
"""

FHSA_CONTRIBUTIONS_IN_2025 = CATALOG.declare(
    "fhsa_contributions_in_2025", Decimal, non_negative=True
)
"""Total contributions made to your FHSAs in 2025, Schedule 15 Step 2 line 1 and line 68935 (box
18 of your 2025 T4FHSA slips): a starting amount."""

FHSA_CONTRIBUTIONS_IN_2025_AFTER_FIRST_QUALIFYING_WITHDRAWAL = CATALOG.declare(
    "fhsa_contributions_in_2025_after_first_qualifying_withdrawal", Decimal, non_negative=True
)
"""Total contributions made to your FHSAs in 2025 after your first qualifying withdrawal,
Schedule 15 Step 2 line 2 and line 68940: a starting amount; line 10 "Amount from line 2" is
this same artifact."""

FHSA_CONTRIBUTIONS_IN_2025_AFTER_FIRST_QUALIFYING_WITHDRAWAL_CHECKED = CATALOG.declare(
    "fhsa_contributions_in_2025_after_first_qualifying_withdrawal_checked",
    Decimal,
    non_negative=True,
)
"""Total contributions made to your FHSAs in 2025 after your first qualifying withdrawal, checked,
Schedule 15 line 2 "Total contributions made to your FHSAs in 2025 after your first qualifying
withdrawal": the amount of `ca/fhsa_contributions_in_2025_after_first_qualifying_withdrawal` after
the check that it is not more than line 1, `ca/fhsa_contributions_in_2025` (`core/at_most`). It is
the part of line 1 made after the first qualifying withdrawal, so a larger amount is refused, not
capped. Line 3 and line 11 read this amount."""

FHSA_CONTRIBUTIONS_IN_2025_BEFORE_FIRST_QUALIFYING_WITHDRAWAL = CATALOG.declare(
    "fhsa_contributions_in_2025_before_first_qualifying_withdrawal", Decimal
)
"""Contributions in 2025 before your first qualifying withdrawal, Schedule 15 Step 2 line 3 "Line 1
minus line 2 =": the 2025 contributions less those made after the first qualifying withdrawal. The
line prints no floor, so the kind is signed."""

FHSA_VARIABLE_B_AMOUNT = CATALOG.declare("fhsa_variable_b_amount", Decimal, non_negative=True)
"""Variable "B" amount of your annual FHSA limit for 2024, Schedule 15 Step 2 line 4 (from your
2025 FHSA participation room statement): a starting amount."""

FHSA_CONTRIBUTIONS_PLUS_VARIABLE_B_AMOUNT = CATALOG.declare(
    "fhsa_contributions_plus_variable_b_amount", Decimal
)
"""Contributions plus variable "B", Schedule 15 Step 2 line 5 "Line 3 plus line 4 =": line 3 plus
the variable "B" amount of line 4. Signed, as line 3 is."""

FHSA_DESIGNATED_WITHDRAWALS_IN_2025 = CATALOG.declare(
    "fhsa_designated_withdrawals_in_2025", Decimal, non_negative=True
)
"""Total designated withdrawals from your FHSAs in 2025, Schedule 15 Step 2 line 6 and line
68945 (box 38 of your 2025 T4FHSA slips): a starting amount."""

FHSA_CONTRIBUTIONS_IN_2024 = CATALOG.declare(
    "fhsa_contributions_in_2024", Decimal, non_negative=True
)
"""Total contributions made to your FHSAs in 2024, Schedule 15 Step 2 line 7 (from your 2025
FHSA participation room statement): a starting amount."""

FHSA_CONTRIBUTIONS_IN_2024_BEFORE_FIRST_QUALIFYING_WITHDRAWAL = CATALOG.declare(
    "fhsa_contributions_in_2024_before_first_qualifying_withdrawal", Decimal, non_negative=True
)
"""Contributions to your FHSAs in 2024 before your first qualifying withdrawal, Schedule 15 Step
2 line 8 (from your 2025 FHSA participation room statement): a starting amount."""

FHSA_CONTRIBUTIONS_IN_2024_BEFORE_FIRST_QUALIFYING_WITHDRAWAL_CHECKED = CATALOG.declare(
    "fhsa_contributions_in_2024_before_first_qualifying_withdrawal_checked",
    Decimal,
    non_negative=True,
)
"""Contributions to your FHSAs in 2024 before your first qualifying withdrawal, checked, Schedule
15 line 8 "Contributions to your FHSAs in 2024 before your first qualifying withdrawal": the amount
of `ca/fhsa_contributions_in_2024_before_first_qualifying_withdrawal` after the check that it is not
more than line 7, `ca/fhsa_contributions_in_2024` (`core/at_most`). It is the part of line 7 made
before the first qualifying withdrawal, so a larger amount is refused, not capped. Line 9 reads this
amount."""

FHSA_CONTRIBUTIONS_IN_2024_AFTER_FIRST_QUALIFYING_WITHDRAWAL = CATALOG.declare(
    "fhsa_contributions_in_2024_after_first_qualifying_withdrawal", Decimal
)
"""Contributions in 2024 after your first qualifying withdrawal, Schedule 15 Step 2 line 9 "Line 7
minus line 8 =": the 2024 contributions less those made before the first qualifying withdrawal. The
line prints no floor, so the kind is signed."""

FHSA_CONTRIBUTIONS_AFTER_FIRST_QUALIFYING_WITHDRAWAL = CATALOG.declare(
    "fhsa_contributions_after_first_qualifying_withdrawal", Decimal
)
"""Contributions after your first qualifying withdrawal, Schedule 15 Step 2 line 11 "Line 9 plus
line 10 =": line 9 plus line 10 "Amount from line 2", the same artifact as line 2. Signed, as line 9
is."""

FHSA_EXCESS_DESIGNATED_WITHDRAWALS = CATALOG.declare(
    "fhsa_excess_designated_withdrawals", Decimal, non_negative=True
)
"""Excess designated withdrawals, Schedule 15 Step 2 line 12 "Line 6 minus line 11 (if negative,
enter "0") =": the designated withdrawals in 2025 beyond the contributions after the first
qualifying withdrawal, not below zero."""

FHSA_CONTRIBUTIONS_LIMIT = CATALOG.declare("fhsa_contributions_limit", Decimal, non_negative=True)
"""Contributions limit, Schedule 15 Step 2 line 13 "Line 5 minus line 12 (if negative, enter "0")
=": the contributions plus variable "B" less the excess designated withdrawals, not below zero."""

FHSA_ANNUAL_AMOUNT = CATALOG.declare("fhsa_annual_amount", Decimal, non_negative=True)
"""Annual FHSA amount, Schedule 15 Step 2 line 14 "8,000.00": the printed amount, from its dataset;
line 30 prints the same figure."""

FHSA_CARRYFORWARD_FOR_2025 = CATALOG.declare(
    "fhsa_carryforward_for_2025", Decimal, non_negative=True
)
"""Your FHSA carryforward for 2025, Schedule 15 Step 2 line 15 (from your 2025 FHSA
participation room statement): a starting amount."""

FHSA_ANNUAL_AMOUNT_WITH_CARRYFORWARD = CATALOG.declare(
    "fhsa_annual_amount_with_carryforward", Decimal, non_negative=True
)
"""Annual FHSA amount with carryforward, Schedule 15 Step 2 line 16 "Line 14 plus line 15 =": the
printed amount plus the FHSA carryforward for 2025."""

FHSA_RRSP_TRANSFERS_IN_2024_AND_PRIOR_YEARS = CATALOG.declare(
    "fhsa_rrsp_transfers_in_2024_and_prior_years", Decimal, non_negative=True
)
"""Total transfers from your RRSPs to your FHSAs in 2024 and prior years, Schedule 15 Step 2
line 17 (from your 2025 FHSA participation room statement): a starting amount; line 25 is this
same artifact."""

FHSA_RRSP_TRANSFERS_IN_2025 = CATALOG.declare(
    "fhsa_rrsp_transfers_in_2025", Decimal, non_negative=True
)
"""Total transfers from your RRSPs to your FHSAs in 2025, Schedule 15 Step 2 line 18 and line
68950 (boxes 32 and 34 of your 2025 T4FHSA slips): a starting amount."""

FHSA_TOTAL_RRSP_TRANSFERS = CATALOG.declare("fhsa_total_rrsp_transfers", Decimal, non_negative=True)
"""Total transfers from your RRSPs to your FHSAs, Schedule 15 Step 2 line 19 "Line 17 plus line 18
=": the transfers of 2024 and prior years plus those of 2025."""

FHSA_DESIGNATED_TRANSFERS_IN_2024_AND_PRIOR_YEARS = CATALOG.declare(
    "fhsa_designated_transfers_in_2024_and_prior_years", Decimal, non_negative=True
)
"""Total designated transfers from your FHSAs to your RRSPs or RRIFs in 2024 and prior years,
Schedule 15 Step 2 line 20 (from your 2025 FHSA participation room statement): a starting
amount; line 26 is this same artifact."""

FHSA_DESIGNATED_TRANSFERS_IN_2025 = CATALOG.declare(
    "fhsa_designated_transfers_in_2025", Decimal, non_negative=True
)
"""Total designated transfers from your FHSAs to your RRSPs or RRIFs in 2025, Schedule 15 Step 2
line 21 and line 68955 (box 36 of your 2025 T4FHSA slips): a starting amount."""

FHSA_TOTAL_DESIGNATED_TRANSFERS = CATALOG.declare(
    "fhsa_total_designated_transfers", Decimal, non_negative=True
)
"""Total designated transfers from your FHSAs to your RRSPs or RRIFs, Schedule 15 Step 2 line 22
"Line 20 plus line 21 =": the transfers of 2024 and prior years plus those of 2025."""

FHSA_NET_RRSP_TRANSFER_AMOUNT = CATALOG.declare("fhsa_net_rrsp_transfer_amount", Decimal)
"""Net RRSP-to-FHSA transfer amount, Schedule 15 Step 2 line 23 "Line 19 minus line 22 =": the
transfers to FHSAs less the designated transfers back. The line prints no floor, so the kind is
signed; lines 24 and 49 are this same artifact."""

FHSA_NET_RRSP_TRANSFER_AMOUNT_FOR_2024_AND_PRIOR_YEARS = CATALOG.declare(
    "fhsa_net_rrsp_transfer_amount_for_2024_and_prior_years", Decimal
)
"""Net RRSP-to-FHSA transfer amount for 2024 and prior years, Schedule 15 Step 2 line 27 "Line 25
minus line 26 =": the transfers of 2024 and prior years less the designated transfers of those
years. The line prints no floor, so the kind is signed."""

FHSA_VARIABLE_H_AMOUNT = CATALOG.declare("fhsa_variable_h_amount", Decimal, non_negative=True)
"""Variable "H" amount of your annual FHSA limit for 2024, Schedule 15 Step 2 line 28 (from your
2025 FHSA participation room statement): a starting amount."""

FHSA_NET_TRANSFER_AMOUNT_LESS_VARIABLE_H_AMOUNT = CATALOG.declare(
    "fhsa_net_transfer_amount_less_variable_h_amount", Decimal, non_negative=True
)
"""Net transfer amount less variable "H", Schedule 15 Step 2 line 29 "Line 27 minus line 28 (if
negative, enter "0") =": line 27 less the variable "H" amount of line 28, not below zero."""

FHSA_ANNUAL_AMOUNT_FOR_2024 = CATALOG.declare(
    "fhsa_annual_amount_for_2024", Decimal, non_negative=True
)
"""Annual FHSA amount for 2024, Schedule 15 Step 2 line 30 "8,000.00": the printed amount, from the
same dataset as line 14."""

FHSA_CARRYFORWARD_FOR_2024 = CATALOG.declare(
    "fhsa_carryforward_for_2024", Decimal, non_negative=True
)
"""Your FHSA carryforward for 2024, Schedule 15 Step 2 line 31 (from your 2024 FHSA
participation room statement): a starting amount."""

FHSA_ANNUAL_AMOUNT_FOR_2024_WITH_CARRYFORWARD = CATALOG.declare(
    "fhsa_annual_amount_for_2024_with_carryforward", Decimal, non_negative=True
)
"""Annual FHSA amount for 2024 with carryforward, Schedule 15 Step 2 line 32 "Line 30 plus line 31
=": the printed amount plus the FHSA carryforward for 2024."""

FHSA_TRANSFER_AMOUNT_AT_MOST_LIMIT = CATALOG.declare(
    "fhsa_transfer_amount_at_most_limit", Decimal, non_negative=True
)
"""Transfer amount at most the 2024 limit, Schedule 15 Step 2 line 33 "Enter whichever is less:
amount from line 29 or line 32.": the lesser of the two."""

FHSA_VARIABLE_F_AMOUNT = CATALOG.declare("fhsa_variable_f_amount", Decimal, non_negative=True)
"""Variable "F" amount of your annual FHSA limit for 2024, Schedule 15 Step 2 line 34 (from your
2025 FHSA participation room statement): a starting amount."""

FHSA_TRANSFER_AMOUNT_PLUS_VARIABLE_F_AMOUNT = CATALOG.declare(
    "fhsa_transfer_amount_plus_variable_f_amount", Decimal, non_negative=True
)
"""Transfer amount plus variable "F", Schedule 15 Step 2 line 35 "Line 33 plus line 34 =": line 33
plus the variable "F" amount of line 34."""

FHSA_NET_TRANSFER_AMOUNT_AFTER_PRIOR_YEARS = CATALOG.declare(
    "fhsa_net_transfer_amount_after_prior_years", Decimal
)
"""Net transfer amount after prior years, Schedule 15 Step 2 line 36 "Line 24 minus line 35 =": the
net RRSP-to-FHSA transfer amount less line 35. The line prints no floor, so the kind is signed."""

FHSA_ANNUAL_AMOUNT_AFTER_TRANSFERS = CATALOG.declare(
    "fhsa_annual_amount_after_transfers", Decimal, non_negative=True
)
"""Annual FHSA amount after transfers, Schedule 15 Step 2 line 39 "Line 37 minus line 38 (if
negative, enter "0") =": line 37 "Amount from line 16" less line 38 "Amount from line 36", not below
zero."""

FHSA_MAXIMUM_PARTICIPATION_PERIOD_ENDED = CATALOG.declare(
    "fhsa_maximum_participation_period_ended", int, non_negative=True
)
"""Whether the maximum participation period (MPP) of your FHSAs ended in a prior year, Schedule
15 Step 2: a count of 0 or 1, a starting amount. At 1 the schedule says "do not complete this
step" and line 40 is "0"."""

FHSA_MAXIMUM_PARTICIPATION_PERIOD_ENDED_CHECKED = CATALOG.declare(
    "fhsa_maximum_participation_period_ended_checked", int, non_negative=True
)
"""Maximum participation period of your FHSAs ended in a prior year, Schedule 15 Step 2: the answer
of `ca/fhsa_maximum_participation_period_ended` after the check that it is 0 or 1
(`ca/yes_or_no_count`), a count of 1 or 0. A count of 2 or more is refused, not capped."""

FHSA_ANNUAL_LIMIT_FROM_STEP_2 = CATALOG.declare(
    "fhsa_annual_limit_from_step_2", Decimal, non_negative=True
)
"""Annual FHSA limit from Step 2, Schedule 15 Step 2 line 40 "Enter whichever is less: amount from
line 13 of the previous page or line 39. Annual FHSA limit for 2025": the lesser of the two, when
the maximum participation period has not ended."""

FHSA_ANNUAL_LIMIT_AFTER_MAXIMUM_PARTICIPATION_PERIOD = CATALOG.declare(
    "fhsa_annual_limit_after_maximum_participation_period", Decimal, non_negative=True
)
"""Annual FHSA limit after the maximum participation period, Schedule 15 Step 2 line 40 "Your 2025
annual FHSA limit is "0". Enter "0" on line 40": the printed 0, from its dataset, for a maximum
participation period that ended in a prior year."""

FHSA_ANNUAL_LIMIT = CATALOG.declare("fhsa_annual_limit", Decimal, non_negative=True)
"""Annual FHSA limit for 2025, Schedule 15 Step 2 line 41 "Annual FHSA limit from line 40": the
result of Step 2, or the printed 0 when the maximum participation period ended in a prior year."""

FHSA_ANNUAL_LIMITS_FOR_2024_AND_PRIOR_YEARS = CATALOG.declare(
    "fhsa_annual_limits_for_2024_and_prior_years", Decimal, non_negative=True
)
"""Your total annual FHSA limits for 2024 and prior years, Schedule 15 Step 3 line 42 (from your
2025 FHSA participation room statement): a starting amount."""

FHSA_TOTAL_ANNUAL_LIMITS = CATALOG.declare("fhsa_total_annual_limits", Decimal, non_negative=True)
"""Total annual FHSA limits, Schedule 15 Step 3 line 43 "Line 41 plus line 42 =": the limit for 2025
plus the limits for 2024 and prior years."""

FHSA_DEDUCTIONS_FOR_2024_AND_PRIOR_YEARS = CATALOG.declare(
    "fhsa_deductions_for_2024_and_prior_years", Decimal, non_negative=True
)
"""Your total FHSA deductions for 2024 and prior years, Schedule 15 Step 3 line 44 (from your
2025 FHSA participation room statement): a starting amount; line 47 is this same artifact."""

FHSA_DEDUCTIONS_FOR_2024_AND_PRIOR_YEARS_CHECKED = CATALOG.declare(
    "fhsa_deductions_for_2024_and_prior_years_checked", Decimal, non_negative=True
)
"""Your total FHSA deductions for 2024 and prior years, checked, Schedule 15 line 44 "Your total
FHSA deductions for 2024 and prior years": the amount of
`ca/fhsa_deductions_for_2024_and_prior_years` after the check that it is not more than line 42,
`ca/fhsa_annual_limits_for_2024_and_prior_years` (`core/at_most`). The form prints no number for
that bound: the deductions are made against the limits of those years, the reading the form
implies, so the refusal above line 42 is that reading, not a form figure. Lines 45 and 48 read this
amount."""

FHSA_ANNUAL_LIMITS_LESS_DEDUCTIONS = CATALOG.declare("fhsa_annual_limits_less_deductions", Decimal)
"""Annual FHSA limits less deductions, Schedule 15 Step 3 line 45 "Line 43 minus line 44 =": the
total limits less the deductions of 2024 and prior years. The line prints no floor, so the kind is
signed."""

FHSA_LIFETIME_LIMIT = CATALOG.declare("fhsa_lifetime_limit", Decimal, non_negative=True)
"""Lifetime FHSA limit, Schedule 15 Step 3 line 46 "40,000.00": the printed amount, from its
dataset."""

FHSA_LIFETIME_LIMIT_LESS_DEDUCTIONS = CATALOG.declare(
    "fhsa_lifetime_limit_less_deductions", Decimal
)
"""Lifetime limit less deductions, Schedule 15 Step 3 line 48 "Line 46 minus line 47 =": the
lifetime FHSA limit less the deductions of 2024 and prior years. The line prints no floor, so the
kind is signed."""

FHSA_LIFETIME_LIMIT_LESS_DEDUCTIONS_AND_TRANSFERS = CATALOG.declare(
    "fhsa_lifetime_limit_less_deductions_and_transfers", Decimal, non_negative=True
)
"""Lifetime limit less deductions and transfers, Schedule 15 Step 3 line 50 "Line 48 minus line 49
(if negative, enter "0") =": line 48 less line 49 "Net RRSP-to-FHSA transfer amount from line 24",
not below zero."""

FHSA_MAXIMUM_DEDUCTION = CATALOG.declare("fhsa_maximum_deduction", Decimal)
"""Maximum FHSA deduction available for 2025, Schedule 15 Step 3 line 51 "Enter whichever is less:
amount from line 45 or line 50.": the lesser of the two; signed, as line 45 is."""

FHSA_UNUSED_CONTRIBUTIONS_BROUGHT_FORWARD = CATALOG.declare(
    "fhsa_unused_contributions_brought_forward", Decimal, non_negative=True
)
"""Your unused FHSA contributions available to deduct in future years, Schedule 15 Step 3 line
52 (from your 2025 FHSA participation room statement): a starting amount."""

FHSA_UNUSED_CONTRIBUTIONS_PLUS_CONTRIBUTIONS = CATALOG.declare(
    "fhsa_unused_contributions_plus_contributions", Decimal
)
"""Unused FHSA contributions plus contributions, Schedule 15 Step 3 line 54 "Line 52 plus line 53
=": the unused contributions brought forward plus line 53 "Amount from line 3 of page 2", the same
artifact as line 3. Signed, as line 3 is."""

FHSA_CONTRIBUTIONS_AVAILABLE = CATALOG.declare("fhsa_contributions_available", Decimal)
"""FHSA contributions available to deduct, Schedule 15 Step 3 line 56 "Line 54 minus line 55 =":
line 54 less line 55 "Amount from line 12 of page 2", the same artifact as line 12. The line prints
no floor, so the kind is signed."""

FHSA_CONTRIBUTIONS_DEDUCTED = CATALOG.declare(
    "fhsa_contributions_deducted", Decimal, non_negative=True
)
"""FHSA contributions you are deducting for 2025, Schedule 15 Step 3 line 57: the amount the
filer chooses to deduct, a starting amount, refused when above line 51 (as Schedule 7 line 18 is
refused above line 17)."""

FHSA_DEDUCTION = CATALOG.declare("fhsa_deduction", Decimal, non_negative=True)
"""FHSA deduction, T1 line 37 and line 20805, Schedule 15 Step 3 line 57 "Enter this amount on
line 20805 of your return. FHSA deduction for 2025": the contributions deducted, at most line
51, a deduction from total income."""

FHSA_UNUSED_CONTRIBUTIONS_CARRIED_FORWARD = CATALOG.declare(
    "fhsa_unused_contributions_carried_forward", Decimal
)
"""Your unused FHSA contributions available to deduct in future years, Schedule 15 Step 3 line
58 "Line 56 minus line 57 =": what the return produces for the next year's line 52. The line
prints no floor, so the kind is signed."""

FHSA_FIRST_OPENED_IN_YEAR = CATALOG.declare("fhsa_first_opened_in_year", int, non_negative=True)
"""First FHSA opened in the year, Schedule 15 Step 1 line 68930 "Tick this box if you opened your
first FHSA in 2025 or became a successor holder in 2025 and did not open another FHSA of your own in
2025 or a prior year.": a 0 or 1 tick, carried as entered, which no step reads."""

FHSA_QUALIFYING_WITHDRAWALS = CATALOG.declare(
    "fhsa_qualifying_withdrawals", Decimal, non_negative=True
)
"""Qualifying withdrawals from an FHSA, Schedule 15 Step 4 line 59 and line 68960 "Total amount of
qualifying withdrawals made in 2025 (box 20 of your 2025 T4FHSA slips)": a memo carried as entered,
which no step reads."""

FHSA_HOME_ADDRESS_SAME = CATALOG.declare("fhsa_home_address_same", int, non_negative=True)
"""Home bought or built under the FHSA at the return address, Schedule 15 Step 4 line 68965 "Tick
this box if the address on page 1 of your return is the same as the address of the home that you
bought or built under the FHSA.": a 0 or 1 tick, carried as entered, which no step reads."""
