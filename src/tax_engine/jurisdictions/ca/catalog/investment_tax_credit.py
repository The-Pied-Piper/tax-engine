"""The federal catalog: investment tax credit, Form T2038(IND) Parts A, B, D and E.

The caller's lines of Parts A, B and D (the SR&ED, agricultural, partnership, qualified property,
mineral exploration, critical mineral, apprenticeship T3 box 40, repayment, opening balance,
graduated rate estate and claim figures), the credit each one produces at its rate, the totals of
Parts A and B that Part D reads, and the amounts of Part D that give line 41200, the investment tax
credit (`investment_tax_credit`). Part E takes the carryback designations (lines 67200, 67210 and
67220) and the refund the filer designates (amount 17), and gives the amounts L, M, N and O, the
refund of investment tax credit on line 45400 (`investment_tax_credit_refund`). The apprentices and
their total are the kinds of `credits_against_federal_tax`.
"""

from __future__ import annotations

from decimal import Decimal

from tax_engine.jurisdictions.ca.catalog.base import CATALOG

ITC_SRED_EXPENDITURES = CATALOG.declare("itc_sred_expenditures", Decimal, non_negative=True)
"""SR&ED expenditures, Form T2038(IND) Part A line 67120 "ITC for qualified expenditures for SR&ED
(amount from line 559 of Form T661 plus applicable amount from box 40* of your T3 slip, minus
amounts from lines 67130 and 67135)": the caller's amount, as entered."""

ITC_AGRICULTURAL_SRED_CONTRIBUTIONS = CATALOG.declare(
    "itc_agricultural_sred_contributions", Decimal, non_negative=True
)
"""Agricultural SR&ED contributions, Form T2038(IND) Part A line 67130 "80% of total contributions
made to agricultural organizations for SR&ED": the caller's amount, as entered."""

ITC_SRED_PARTNERSHIP_ALLOCATION = CATALOG.declare(
    "itc_sred_partnership_allocation", Decimal, non_negative=True
)
"""ITC allocated from a partnership for SR&ED, Form T2038(IND) Part A line 67135 "ITC allocated
from a partnership for SR&ED (see boxes 186, 187, and 189 of your T5013 slips)": amount 3, read as
it is, the caller's amount from the T5013 slips."""

ITC_QUALIFIED_PROPERTY = CATALOG.declare("itc_qualified_property", Decimal, non_negative=True)
"""Qualified property, Form T2038(IND) Part A line 67140 "ITC for total investments in qualified
property (include applicable amount from box 40* of your T3 slip)": the caller's amount, as
entered."""

ITC_MINERAL_EXPLORATION_EXPENDITURES = CATALOG.declare(
    "itc_mineral_exploration_expenditures", Decimal, non_negative=True
)
"""Flow-through mining expenditures, Form T2038(IND) Part B line 67170 "Total of your flow-through
mining expenditures related to mineral exploration tax credit": the caller's amount from the
appropriate line in Part IV of Form T1229, as entered."""

ITC_CRITICAL_MINERAL_EXPENDITURES = CATALOG.declare(
    "itc_critical_mineral_expenditures", Decimal, non_negative=True
)
"""Flow-through critical mineral mining expenditures, Form T2038(IND) Part B line 67175 "Total of
your flow-through critical mineral mining expenditures related to critical mineral exploration tax
credit": the caller's amount from the appropriate line in Part IV of Form T1229, as entered."""

ITC_APPRENTICESHIP_T3_BOX_40 = CATALOG.declare(
    "itc_apprenticeship_t3_box_40", Decimal, non_negative=True
)
"""Apprenticeship T3 box 40 amount, Form T2038(IND) Part B line 67180 "Total apprenticeship job
creation tax credit (Total of amounts in column 3 plus applicable amount from box 40* of your T3
slip)": the caller's amount from box 40 of the T3 slip, as entered, added to column 3."""

ITC_SRED_REPAYMENT_2014_AND_PRIOR = CATALOG.declare(
    "itc_sred_repayment_2014_and_prior", Decimal, non_negative=True
)
"""Repayment for SR&ED expenditures of 2014 and prior years, Form T2038(IND) Part B line 67184
"Repayment of assistance that reduced qualified SR&ED expenditures incurred in 2014 and prior
years (amount from line 560 of Form T661)": the caller's amount, as entered."""

ITC_SRED_REPAYMENT_2015_AND_AFTER = CATALOG.declare(
    "itc_sred_repayment_2015_and_after", Decimal, non_negative=True
)
"""Repayment for SR&ED expenditures of 2015 and subsequent years, Form T2038(IND) Part B line 67185
"Repayment of assistance that reduced qualified SR&ED expenditures incurred in 2015 and subsequent
years (amount from line 560 of Form T661)": the caller's amount, as entered."""

ITC_SRED_CREDIT = CATALOG.declare("itc_sred_credit", Decimal, non_negative=True)
"""SR&ED credit, Form T2038(IND) Part A, amount 1: line 67120 "× 0.15 =", the caller's expenditures
times 0.15."""

ITC_AGRICULTURAL_SRED_CREDIT = CATALOG.declare(
    "itc_agricultural_sred_credit", Decimal, non_negative=True
)
"""Agricultural SR&ED credit, Form T2038(IND) Part A, amount 2: line 67130 "× 0.15 =", the caller's
contributions times 0.15."""

ITC_QUALIFIED_PROPERTY_CREDIT = CATALOG.declare(
    "itc_qualified_property_credit", Decimal, non_negative=True
)
"""Qualified property credit, Form T2038(IND) Part A, amount 4: line 67140 "× 0.10 =", the caller's
investments times 0.10."""

ITC_MINERAL_EXPLORATION_CREDIT = CATALOG.declare(
    "itc_mineral_exploration_credit", Decimal, non_negative=True
)
"""Mineral exploration tax credit, Form T2038(IND) Part B, amount B: line 67170 "× 0.15 =", the
caller's flow-through mining expenditures times 0.15."""

ITC_CRITICAL_MINERAL_CREDIT = CATALOG.declare(
    "itc_critical_mineral_credit", Decimal, non_negative=True
)
"""Critical mineral exploration tax credit, Form T2038(IND) Part B, amount C: line 67175 "× 0.30 =",
the caller's flow-through critical mineral expenditures times 0.30."""

ITC_APPRENTICESHIP_WAGES_WITH_T3 = CATALOG.declare(
    "itc_apprenticeship_wages_with_t3", Decimal, non_negative=True
)
"""Apprenticeship total for the credit, Form T2038(IND) Part B line 67180 "Total apprenticeship job
creation tax credit (Total of amounts in column 3 plus applicable amount from box 40* of your T3
slip)": the total of column 3, plus the caller's T3 box 40 amount."""

ITC_APPRENTICESHIP_CREDIT = CATALOG.declare("itc_apprenticeship_credit", Decimal, non_negative=True)
"""Apprenticeship job creation tax credit, Form T2038(IND) Part B, amount D: line 67180 "× 0.10 =",
the total of line 67180 times 0.10."""

ITC_SRED_REPAYMENT_CREDIT_2014_AND_PRIOR = CATALOG.declare(
    "itc_sred_repayment_credit_2014_and_prior", Decimal, non_negative=True
)
"""Repayment credit for 2014 and prior years, Form T2038(IND) Part B, amount 1: line 67184
"× 0.20 =", the caller's repayment times 0.20."""

ITC_SRED_REPAYMENT_CREDIT_2015_AND_AFTER = CATALOG.declare(
    "itc_sred_repayment_credit_2015_and_after", Decimal, non_negative=True
)
"""Repayment credit for 2015 and subsequent years, Form T2038(IND) Part B, amount 2: line 67185
"× 0.15 =", the caller's repayment times 0.15."""

ITC_SRED_REPAYMENT_CREDIT = CATALOG.declare("itc_sred_repayment_credit", Decimal, non_negative=True)
"""Total repayment of assistance for SR&ED, Form T2038(IND) Part B, amount E: "Total repayment of
assistance for SR&ED (add amounts 1 and 2)", the two repayment credits."""

ITC_REFUNDABLE_CREDITS = CATALOG.declare("itc_refundable_credits", Decimal, non_negative=True)
"""Total current-year refundable credits, Form T2038(IND) Part A, amount A: "Total current-year
refundable credits (add amounts 1 to 4)", the four credits of Part A, in line order. Part D amount 2
reads it as "Current-year refundable tax credit (amount A in Part A)"."""

ITC_NONREFUNDABLE_CREDITS = CATALOG.declare("itc_nonrefundable_credits", Decimal, non_negative=True)
"""Total current-year non-refundable tax credits, Form T2038(IND) Part B, amount F: "Total
current-year non-refundable tax credits (add amounts B, C, D and E)", the credits B, C, D and E.
Part D amount 3 reads it as "Current-year non-refundable tax credit (amount F in Part B)"."""

ITC_OPENING_BALANCE = CATALOG.declare("itc_opening_balance", Decimal, non_negative=True)
"""ITC opening balance, Form T2038(IND) Part D amount 1: "ITC opening balance and carry forward from
prior years (net of expired amounts)", the caller's amount, as entered."""

ITC_PART_D_SUBTOTAL = CATALOG.declare("itc_part_d_subtotal", Decimal, non_negative=True)
"""Subtotal of the current-year credits, Form T2038(IND) Part D amount 4: "Subtotal (add amounts 2
and 3)", amount A and amount F added in line order."""

ITC_PART_D_AMOUNT_5 = CATALOG.declare("itc_part_d_amount_5", Decimal, non_negative=True)
"""Amount 5, Form T2038(IND) Part D: "Amount 1 plus amount 4", the opening balance and carry
forward plus amount 4."""

ITC_GRADUATED_RATE_ESTATE_ALLOCATION = CATALOG.declare(
    "itc_graduated_rate_estate_allocation", Decimal, non_negative=True
)
"""Graduated rate estate allocation, Form T2038(IND) Part D amount 6: "Adjustment for a graduated
rate estate, enter the amount of ITC allocated to beneficiaries from box 40 of your T3 slip", the
caller's amount, as entered."""

ITC_AVAILABLE = CATALOG.declare("itc_available", Decimal)
"""Total available investment tax credit, Form T2038(IND) Part D amount G: "Total available
investment tax credit (amount 5 minus amount 6)", amount 5 less amount 6. The form prints no floor
at 0, so it is not declared non-negative."""

ITC_PART_D_AMOUNT_9 = CATALOG.declare("itc_part_d_amount_9", Decimal, non_negative=True)
"""Subtotal of the federal tax, Form T2038(IND) Part D amount 9: "Subtotal (amount 7 minus amount
8, if negative, enter "0")", the federal tax of line 40600 less the political contribution tax
credit of line 41000, not below zero."""

ITC_AMOUNT_H = CATALOG.declare("itc_amount_h", Decimal, non_negative=True)
"""Amount H, Form T2038(IND) Part D: "Subtotal (amount 9 minus amount 10, if negative, enter "0")",
amount 9 less the labour-sponsored funds tax credit of line 41400, not below zero."""

ITC_AMOUNT_I = CATALOG.declare("itc_amount_i", Decimal)
"""Amount I, Form T2038(IND) Part D: "Enter the lesser of amount G or H", the lesser of amount G and
amount H. Amount G is not floored, so amount I is not declared non-negative."""

ITC_PART_D_AMOUNT_13 = CATALOG.declare("itc_part_d_amount_13", Decimal, non_negative=True)
"""Subtotal, Form T2038(IND) Part D amount 13: "Subtotal (add amounts 11 and 12)", amount 11
(amount H) and amount 12, the federal foreign tax credit of line 40500."""

ITC_AMOUNT_J = CATALOG.declare("itc_amount_j", Decimal, non_negative=True)
"""Amount J, Form T2038(IND) Part D: "Subtotal (amount 13 minus amount 14, if negative, enter "0")",
amount 13 less the minimum amount from line 103 of Part 1 of Form T691, not below zero."""

ITC_AMOUNT_K = CATALOG.declare("itc_amount_k", Decimal)
"""Amount K, Form T2038(IND) Part D: "Enter the lesser of amount G or J", the lesser of amount G and
amount J. Amount G is not floored, so amount K is not declared non-negative."""

ITC_PART_D_AMOUNT_11_APPLIES = CATALOG.declare(
    "itc_part_d_amount_11_applies", int, non_negative=True
)
"""Continue at amount 11, Form T2038(IND) Part D: "If you have to complete Form T691, Alternative
Minimum Tax and the amount you calculate on line 7 of Part 5 in Form T691 is greater than "0",
continue at amount 11.", the count of the condition: 1 when Form T691 Part 5 line 7 is more than 0,
and 0 otherwise."""

ITC_CLAIM_LIMIT = CATALOG.declare("itc_claim_limit", Decimal)
"""Claim limit, Form T2038(IND) Part D amount 15: "You can claim an ITC up to, but not more than I
or K, whichever applies", amount I when the count of amount 11 is 0 and amount K when it is 1. It
takes the sign of amount G, so it is not declared non-negative."""

ITC_CLAIM = CATALOG.declare("itc_claim", Decimal, non_negative=True)
"""Claim, Form T2038(IND) Part D amount 15: "Enter your claim on this line:", the credit the filer
chooses (an election), as entered, never negative. It is claimed up to the claim limit."""

INVESTMENT_TAX_CREDIT = CATALOG.declare("investment_tax_credit", Decimal, non_negative=True)
"""Investment tax credit, T1 line 136 and line 41200 "Investment tax credit (complete Form
T2038(IND))": Form T2038(IND) Part D amount 15, "Enter amount 15 on line 41200 of your income tax
and benefit return", the claim up to the claim limit, refused above it and not capped."""

ITC_CARRYBACK_THIRD_PREVIOUS_YEAR = CATALOG.declare(
    "itc_carryback_third_previous_year", Decimal, non_negative=True
)
"""Carryback to the third previous year, Form T2038(IND) Part E line 67200 "Third previous year":
the part of amount L the filer carries back to the third previous tax year, the caller's election,
as entered, never negative."""

ITC_CARRYBACK_SECOND_PREVIOUS_YEAR = CATALOG.declare(
    "itc_carryback_second_previous_year", Decimal, non_negative=True
)
"""Carryback to the second previous year, Form T2038(IND) Part E line 67210 "Second previous
year": the part of amount L the filer carries back to the second previous tax year, the caller's
election, as entered, never negative."""

ITC_CARRYBACK_FIRST_PREVIOUS_YEAR = CATALOG.declare(
    "itc_carryback_first_previous_year", Decimal, non_negative=True
)
"""Carryback to the first previous year, Form T2038(IND) Part E line 67220 "First previous year":
the part of amount L the filer carries back to the first previous tax year, the caller's election,
as entered, never negative."""

ITC_PART_E_AMOUNT_3 = CATALOG.declare("itc_part_e_amount_3", Decimal)
"""Amount 3, Form T2038(IND) Part E: "Subtotal (amount 1 minus amount 2)", the total available ITC
of amount G in Part D less the opening balance. The form prints no floor at 0, so amount 3 is not
declared non-negative."""

ITC_PART_E_AMOUNT_6 = CATALOG.declare("itc_part_e_amount_6", Decimal, non_negative=True)
"""Amount 6, Form T2038(IND) Part E: "Subtotal (amount 4 minus amount 5, if negative enter "0")",
the maximum ITC claimable in Part D (amount I or K) less the opening balance, not below zero."""

ITC_AMOUNT_L = CATALOG.declare("itc_amount_l", Decimal)
"""Amount L, Form T2038(IND) Part E: "Total credit available for carryback (amount 3 minus amount
6)", amount 3 less amount 6. The form prints no floor at 0, so amount L is not declared
non-negative."""

ITC_CARRYBACK_REQUESTED = CATALOG.declare("itc_carryback_requested", Decimal, non_negative=True)
"""Carryback requested, Form T2038(IND) Part E "Total credit designated for carryback (Add lines
67200, 67210, and 67220. The total cannot be more than amount L)": lines 67200, 67210 and 67220
added in line order, before the check against amount L."""

ITC_AMOUNT_M = CATALOG.declare("itc_amount_m", Decimal, non_negative=True)
"""Amount M, Form T2038(IND) Part E: "Total credit designated for carryback (Add lines 67200,
67210, and 67220. The total cannot be more than amount L)", the requested carryback total, refused
above amount L and not capped."""

ITC_PART_E_AMOUNT_9 = CATALOG.declare("itc_part_e_amount_9", Decimal)
"""Amount 9, Form T2038(IND) Part E: "Total current-year refundable credit available (amount 7 minus
amount 8)", amount A of Part A less the graduated rate estate adjustment of Part D amount 6. The
form prints no floor at 0, so amount 9 is not declared non-negative."""

ITC_PART_E_AMOUNT_12 = CATALOG.declare("itc_part_e_amount_12", Decimal)
"""Amount 12, Form T2038(IND) Part E: "Subtotal (amount 10 minus amount 11)", amount 15 of Part D
less the opening balance. The form prints no floor at 0, so amount 12 is not declared
non-negative."""

ITC_PART_E_AMOUNT_14 = CATALOG.declare("itc_part_e_amount_14", Decimal)
"""Amount 14, Form T2038(IND) Part E: "Subtotal (amount 12 plus amount 13)", amount 12 plus amount
M, the carryback requested. The form prints no floor at 0, so amount 14 is not declared
non-negative."""

ITC_PART_E_AMOUNT_16 = CATALOG.declare("itc_part_e_amount_16", Decimal, non_negative=True)
"""Amount 16, Form T2038(IND) Part E: "Total (amount 14 minus amount 15, if negative, enter "0")",
amount 14 less amount F of Part B, the current-year non-refundable tax credit, not below zero."""

ITC_AMOUNT_N = CATALOG.declare("itc_amount_n", Decimal)
"""Amount N, Form T2038(IND) Part E: "Total credit available for refund (amount 9 minus amount
16)", amount 9 less amount 16. The form prints no floor at 0, so amount N is not declared
non-negative."""

ITC_REFUND_DESIGNATION = CATALOG.declare("itc_refund_designation", Decimal, non_negative=True)
"""Amount 17, Form T2038(IND) Part E: "Amount you designate as a refund of ITC (cannot be more than
amount N)", the refund the filer chooses (an election), as entered, never negative. It is refused
above amount N and not capped."""

ITC_PART_E_AMOUNT_17 = CATALOG.declare("itc_part_e_amount_17", Decimal, non_negative=True)
"""Amount 17 of Form T2038(IND) Part E, as the return holds it: the refund designation, refused
above amount N ("Amount you designate as a refund of ITC (cannot be more than amount N)"), the
base the refundable rate multiplies."""

INVESTMENT_TAX_CREDIT_REFUND = CATALOG.declare(
    "investment_tax_credit_refund", Decimal, non_negative=True
)
"""Refund of investment tax credit, T1 line 158 and line 45400 "Refund of investment tax credit
(complete Form T2038(IND))": Form T2038(IND) Part E amount O, "Refund of ITC (multiply amount 17 by
amount 18)", amount 17 times the refundable rate of 0.40, rounded half-up to the cent. Line 45400
of the return is amount O, "Enter amount O on line 45400 of your income tax and benefit return"."""
