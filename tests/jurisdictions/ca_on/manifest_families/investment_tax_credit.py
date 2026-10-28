"""The CA-ON manifest entries of one family of lines (see `test_manifest.py`)."""

from __future__ import annotations

from tax_calculator.domain.capabilities.apply_rate import ApplyRate
from tax_calculator.domain.capabilities.at_most import AtMost
from tax_calculator.domain.capabilities.choose_by_count import ChooseByCount
from tax_calculator.domain.capabilities.lesser_of import LesserOf
from tax_calculator.domain.capabilities.subtract import Subtract
from tax_calculator.domain.capabilities.subtract_not_below_zero import SubtractNotBelowZero
from tax_calculator.domain.capabilities.sum import Sum
from tax_calculator.domain.manifest import CapabilitySelection
from tax_calculator.jurisdictions.ca.capabilities.apprenticeship_wages_total import (
    ApprenticeshipWagesTotal,
)
from tax_calculator.jurisdictions.ca.capabilities.count_by_conditions import CountByConditions
from tax_calculator.jurisdictions.ca.catalog import (
    AMT_MINIMUM_AMOUNT,
    AMT_MINIMUM_TAX_AFTER_REGULAR_TAX,
    FEDERAL_FOREIGN_TAX_CREDIT,
    FEDERAL_TAX,
    INVESTMENT_TAX_CREDIT,
    INVESTMENT_TAX_CREDIT_REFUND,
    ITC_AGRICULTURAL_SRED_CONTRIBUTIONS,
    ITC_AGRICULTURAL_SRED_CREDIT,
    ITC_AMOUNT_H,
    ITC_AMOUNT_I,
    ITC_AMOUNT_J,
    ITC_AMOUNT_K,
    ITC_AMOUNT_L,
    ITC_AMOUNT_M,
    ITC_AMOUNT_N,
    ITC_APPRENTICES,
    ITC_APPRENTICESHIP_CREDIT,
    ITC_APPRENTICESHIP_T3_BOX_40,
    ITC_APPRENTICESHIP_WAGES_TOTAL,
    ITC_APPRENTICESHIP_WAGES_WITH_T3,
    ITC_AVAILABLE,
    ITC_CARRYBACK_FIRST_PREVIOUS_YEAR,
    ITC_CARRYBACK_REQUESTED,
    ITC_CARRYBACK_SECOND_PREVIOUS_YEAR,
    ITC_CARRYBACK_THIRD_PREVIOUS_YEAR,
    ITC_CLAIM,
    ITC_CLAIM_LIMIT,
    ITC_CRITICAL_MINERAL_CREDIT,
    ITC_CRITICAL_MINERAL_EXPENDITURES,
    ITC_GRADUATED_RATE_ESTATE_ALLOCATION,
    ITC_MINERAL_EXPLORATION_CREDIT,
    ITC_MINERAL_EXPLORATION_EXPENDITURES,
    ITC_NONREFUNDABLE_CREDITS,
    ITC_OPENING_BALANCE,
    ITC_PART_D_AMOUNT_5,
    ITC_PART_D_AMOUNT_9,
    ITC_PART_D_AMOUNT_11_APPLIES,
    ITC_PART_D_AMOUNT_13,
    ITC_PART_D_SUBTOTAL,
    ITC_PART_E_AMOUNT_3,
    ITC_PART_E_AMOUNT_6,
    ITC_PART_E_AMOUNT_9,
    ITC_PART_E_AMOUNT_12,
    ITC_PART_E_AMOUNT_14,
    ITC_PART_E_AMOUNT_16,
    ITC_PART_E_AMOUNT_17,
    ITC_QUALIFIED_PROPERTY,
    ITC_QUALIFIED_PROPERTY_CREDIT,
    ITC_REFUND_DESIGNATION,
    ITC_REFUNDABLE_CREDITS,
    ITC_SRED_CREDIT,
    ITC_SRED_EXPENDITURES,
    ITC_SRED_PARTNERSHIP_ALLOCATION,
    ITC_SRED_REPAYMENT_2014_AND_PRIOR,
    ITC_SRED_REPAYMENT_2015_AND_AFTER,
    ITC_SRED_REPAYMENT_CREDIT,
    ITC_SRED_REPAYMENT_CREDIT_2014_AND_PRIOR,
    ITC_SRED_REPAYMENT_CREDIT_2015_AND_AFTER,
    LABOUR_SPONSORED_FUNDS_CREDIT,
    POLITICAL_CREDIT,
)

# The caller's lines of Form T2038(IND) Parts A, B, D and E, as the form takes them (manifest parts
# 01b_investment_tax_credit.yaml): Part A lines 67120, 67130, 67135 and 67140, Part B lines 67170
# and 67175, the apprentices of Table 1, the T3 box 40 amount on line 67180, lines 67184 and 67185,
# and the Part D amount 1 (the opening balance), amount 6 (the graduated rate estate allocation) and
# the claim on amount 15; and the Part E carryback designations on lines 67200, 67210 and 67220 and
# the refund designated as amount 17.
INPUTS = frozenset(
    {
        "ca/itc_sred_expenditures",
        "ca/itc_agricultural_sred_contributions",
        "ca/itc_sred_partnership_allocation",
        "ca/itc_qualified_property",
        "ca/itc_mineral_exploration_expenditures",
        "ca/itc_critical_mineral_expenditures",
        "ca/itc_apprentices",
        "ca/itc_apprenticeship_t3_box_40",
        "ca/itc_sred_repayment_2014_and_prior",
        "ca/itc_sred_repayment_2015_and_after",
        "ca/itc_opening_balance",
        "ca/itc_graduated_rate_estate_allocation",
        "ca/itc_claim",
        "ca/itc_carryback_third_previous_year",
        "ca/itc_carryback_second_previous_year",
        "ca/itc_carryback_first_previous_year",
        "ca/itc_refund_designation",
    }
)

# No declared outputs: Form T2038(IND) Part A "Total current-year refundable credits (add amounts 1
# to 4)" and Part B "Total current-year non-refundable tax credits (add amounts B, C, D and E)" are
# read by Part D ("Current-year refundable tax credit (amount A in Part A)" at amount 2 and
# "Current-year non-refundable tax credit (amount F in Part B)" at amount 3), and the claim on
# amount 15 is read by T1 line 138 and by Form T691 Part 5 line 9.
OUTPUTS: frozenset[str] = frozenset()

STEPS = {
    # Form T2038(IND) Part A line 1, "ITC for qualified expenditures for SR&ED (amount from line 559
    # of Form T661 plus applicable amount from box 40* of your T3 slip, minus amounts from lines
    # 67130 and 67135)" "× 0.15 =" amount 1: the caller's line 67120 at the rate of its dataset.
    CapabilitySelection(
        name="core/apply_rate",
        params={"rate": "ca/itc_part_a_line_1_rate"},
        consumes={"base": "ca/itc_sred_expenditures"},
        produces={"output": "ca/itc_sred_credit"},
    ),
    # Form T2038(IND) Part A line 2, "80% of total contributions made to agricultural organizations
    # for SR&ED" "× 0.15 =" amount 2: the caller's line 67130 at the rate of its dataset.
    CapabilitySelection(
        name="core/apply_rate",
        params={"rate": "ca/itc_part_a_line_2_rate"},
        consumes={"base": "ca/itc_agricultural_sred_contributions"},
        produces={"output": "ca/itc_agricultural_sred_credit"},
    ),
    # Form T2038(IND) Part A line 4, "ITC for total investments in qualified property (include
    # applicable amount from box 40* of your T3 slip)" "× 0.10 =" amount 4: the caller's line 67140
    # at the rate of its dataset.
    CapabilitySelection(
        name="core/apply_rate",
        params={"rate": "ca/itc_part_a_line_4_rate"},
        consumes={"base": "ca/itc_qualified_property"},
        produces={"output": "ca/itc_qualified_property_credit"},
    ),
    # Form T2038(IND) Part A "Total current-year refundable credits (add amounts 1 to 4)", amount A:
    # amounts 1, 2, 3 and 4 in line order, amount 3 being the caller's line 67135 "ITC allocated
    # from a partnership for SR&ED", read as it is.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/itc_sred_credit",
                "ca/itc_agricultural_sred_credit",
                "ca/itc_sred_partnership_allocation",
                "ca/itc_qualified_property_credit",
            )
        },
        produces={"output": "ca/itc_refundable_credits"},
    ),
    # Form T2038(IND) Part B line 67170, "Mineral exploration tax credit (METC)" "× 0.15 =" amount
    # B: the caller's flow-through mining expenditures at the rate of its dataset.
    CapabilitySelection(
        name="core/apply_rate",
        params={"rate": "ca/itc_part_b_amount_b_rate"},
        consumes={"base": "ca/itc_mineral_exploration_expenditures"},
        produces={"output": "ca/itc_mineral_exploration_credit"},
    ),
    # Form T2038(IND) Part B line 67175, "Critical mineral exploration tax credit (CMETC)"
    # "× 0.30 =" amount C: the caller's flow-through critical mineral expenditures at the rate of
    # its dataset.
    CapabilitySelection(
        name="core/apply_rate",
        params={"rate": "ca/itc_part_b_amount_c_rate"},
        consumes={"base": "ca/itc_critical_mineral_expenditures"},
        produces={"output": "ca/itc_critical_mineral_credit"},
    ),
    # Form T2038(IND) Part B Table 1, column 3, "The lesser of eligible salary and wages** payable
    # in the year or $20,000.": the total over the apprentices, each one's lesser taken with the
    # maximum dataset's amount.
    CapabilitySelection(
        name="ca/apprenticeship_wages_total",
        params={"maximum": "ca/itc_apprentice_wages_maximum"},
        consumes={"apprentices": "ca/itc_apprentices"},
        produces={"output": "ca/itc_apprenticeship_wages_total"},
    ),
    # Form T2038(IND) Part B line 67180, "Total apprenticeship job creation tax credit (Total of
    # amounts in column 3 plus applicable amount from box 40* of your T3 slip)": the total of
    # column 3 plus the caller's T3 box 40 amount.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/itc_apprenticeship_wages_total",
                "ca/itc_apprenticeship_t3_box_40",
            )
        },
        produces={"output": "ca/itc_apprenticeship_wages_with_t3"},
    ),
    # Form T2038(IND) Part B line 67180 "× 0.10 =" amount D, "The credit is 10% of the total of the
    # amounts in Table 1, column 3.": the total of line 67180 at the rate of its dataset.
    CapabilitySelection(
        name="core/apply_rate",
        params={"rate": "ca/itc_part_b_amount_d_rate"},
        consumes={"base": "ca/itc_apprenticeship_wages_with_t3"},
        produces={"output": "ca/itc_apprenticeship_credit"},
    ),
    # Form T2038(IND) Part B, "Repayment of assistance that reduced qualified SR&ED expenditures
    # incurred in 2014 and prior years (amount from line 560 of Form T661)" 67184 "× 0.20 =" amount
    # 1: the caller's line 67184 at the rate of its dataset.
    CapabilitySelection(
        name="core/apply_rate",
        params={"rate": "ca/itc_part_b_repayment_line_1_rate"},
        consumes={"base": "ca/itc_sred_repayment_2014_and_prior"},
        produces={"output": "ca/itc_sred_repayment_credit_2014_and_prior"},
    ),
    # Form T2038(IND) Part B, "Repayment of assistance that reduced qualified SR&ED expenditures
    # incurred in 2015 and subsequent years (amount from line 560 of Form T661)" 67185 "× 0.15 ="
    # amount 2: the caller's line 67185 at the rate of its dataset.
    CapabilitySelection(
        name="core/apply_rate",
        params={"rate": "ca/itc_part_b_repayment_line_2_rate"},
        consumes={"base": "ca/itc_sred_repayment_2015_and_after"},
        produces={"output": "ca/itc_sred_repayment_credit_2015_and_after"},
    ),
    # Form T2038(IND) Part B "Total repayment of assistance for SR&ED (add amounts 1 and 2)", amount
    # E: amounts 1 and 2 in line order.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/itc_sred_repayment_credit_2014_and_prior",
                "ca/itc_sred_repayment_credit_2015_and_after",
            )
        },
        produces={"output": "ca/itc_sred_repayment_credit"},
    ),
    # Form T2038(IND) Part B "Total current-year non-refundable tax credits (add amounts B, C, D and
    # E)", amount F: amounts B, C, D and E in line order.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/itc_mineral_exploration_credit",
                "ca/itc_critical_mineral_credit",
                "ca/itc_apprenticeship_credit",
                "ca/itc_sred_repayment_credit",
            )
        },
        produces={"output": "ca/itc_nonrefundable_credits"},
    ),
    # Form T2038(IND) Part D amount 4, "Subtotal (add amounts 2 and 3)": amount A, "Current-year
    # refundable tax credit (amount A in Part A)", and amount F, "Current-year non-refundable tax
    # credit (amount F in Part B)", in line order.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/itc_refundable_credits",
                "ca/itc_nonrefundable_credits",
            )
        },
        produces={"output": "ca/itc_part_d_subtotal"},
    ),
    # Form T2038(IND) Part D amount 5, "Amount 1 plus amount 4": the opening balance and carry
    # forward from prior years, "ITC opening balance and carry forward from prior years (net of
    # expired amounts)", and amount 4.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/itc_opening_balance",
                "ca/itc_part_d_subtotal",
            )
        },
        produces={"output": "ca/itc_part_d_amount_5"},
    ),
    # Form T2038(IND) Part D "Total available investment tax credit (amount 5 minus amount 6)", G:
    # amount 6, "Adjustment for a graduated rate estate, enter the amount of ITC allocated to
    # beneficiaries from box 40 of your T3 slip". No floor is printed, so G is not floored at 0.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/itc_part_d_amount_5",
            "less": "ca/itc_graduated_rate_estate_allocation",
        },
        produces={"output": "ca/itc_available"},
    ),
    # Form T2038(IND) Part D amount 9, "Subtotal (amount 7 minus amount 8, if negative, enter "0")":
    # amount 7, "Federal tax (amount from line 40600 of your income tax and benefit return)", less
    # amount 8, "Federal political contribution tax credit (amount from line 41000 of your income
    # tax and benefit return)", and never below zero.
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca/federal_tax",
            "less": "ca/political_credit",
        },
        produces={"output": "ca/itc_part_d_amount_9"},
    ),
    # Form T2038(IND) Part D amount H, "Subtotal (amount 9 minus amount 10, if negative, enter
    # "0")": amount 10, "Labour-sponsored funds tax credit (amount from line 41400 of your income
    # tax and benefit return)", and never below zero.
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca/itc_part_d_amount_9",
            "less": "ca/labour_sponsored_funds_credit",
        },
        produces={"output": "ca/itc_amount_h"},
    ),
    # Form T2038(IND) Part D amount I, "Enter the lesser of amount G or H".
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={"amounts": ("ca/itc_available", "ca/itc_amount_h")},
        produces={"output": "ca/itc_amount_i"},
    ),
    # Form T2038(IND) Part D amount 13, "Subtotal (add amounts 11 and 12)": amount 11, "Enter amount
    # H", and amount 12, "Federal foreign tax credit (amount from line 40500 of your income tax and
    # benefit return)". Amount 11 is read as H. The form continues at amount 11 only when Form T691
    # Part 5 line 7 is greater than 0, so the claim limit uses amount J (through K) only then.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/itc_amount_h",
                "ca/federal_foreign_tax_credit",
            )
        },
        produces={"output": "ca/itc_part_d_amount_13"},
    ),
    # Form T2038(IND) Part D amount J, "Subtotal (amount 13 minus amount 14, if negative, enter
    # "0")": amount 14, "The minimum amount from line 103 on Part 1 of Form T691", and never below
    # zero.
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca/itc_part_d_amount_13",
            "less": "ca/amt_minimum_amount",
        },
        produces={"output": "ca/itc_amount_j"},
    ),
    # Form T2038(IND) Part D amount K, "Enter the lesser of amount G or J".
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={"amounts": ("ca/itc_available", "ca/itc_amount_j")},
        produces={"output": "ca/itc_amount_k"},
    ),
    # Form T2038(IND) Part D "If you have to complete Form T691, Alternative Minimum Tax and the
    # amount you calculate on line 7 of Part 5 in Form T691 is greater than "0", continue at
    # amount 11." The condition "T691 Part 5 line 7 is greater than 0" counts 1 when line 7 (the
    # minimum tax after the regular tax) is more than 0, and 0 otherwise.
    CapabilitySelection(
        name="ca/count_by_conditions",
        params={"conditions": "ca/itc_part_d_amount_11_conditions"},
        consumes={
            "counts": (),
            "amounts": ("ca/amt_minimum_tax_after_regular_tax",),
        },
        produces={"output": "ca/itc_part_d_amount_11_applies"},
    ),
    # Form T2038(IND) Part D: "If alternative minimum tax (AMT) does not apply to you, continue at
    # amount 15." so the claim is limited by amount I when the condition does not apply, and by
    # amount K when it does (continue at amount 11).
    CapabilitySelection(
        name="core/choose_by_count",
        params={},
        consumes={
            "count": "ca/itc_part_d_amount_11_applies",
            "when_none": "ca/itc_amount_i",
            "when_any": "ca/itc_amount_k",
        },
        produces={"output": "ca/itc_claim_limit"},
    ),
    # Form T2038(IND) Part D amount 15, "Enter your claim on this line:" and "You can claim an ITC
    # up to, but not more than I or K, whichever applies": the claim the filer chooses, up to the
    # limit and refused above it (as Form T691 Part 3 line 12 is), which is line 41200 of the
    # return, "Enter amount 15 on line 41200 of your income tax and benefit return".
    CapabilitySelection(
        name="core/at_most",
        params={},
        consumes={
            "amount": "ca/itc_claim",
            "bound": "ca/itc_claim_limit",
        },
        produces={"output": "ca/investment_tax_credit"},
    ),
    # Form T2038(IND) Part E amount 3, "Subtotal (amount 1 minus amount 2)": amount 1, "Total
    # available ITC (amount G in Part D)", less amount 2, "ITC opening balance and carry-forward
    # from prior years (amount 1 in Part D)". No floor is printed, so amount 3 is not floored at 0.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/itc_available",
            "less": "ca/itc_opening_balance",
        },
        produces={"output": "ca/itc_part_e_amount_3"},
    ),
    # Form T2038(IND) Part E amount 6, "Subtotal (amount 4 minus amount 5, if negative enter "0")":
    # amount 4, "Maximum ITC you could have claimed in Part D (amount I or K, whichever applies)",
    # less amount 5, "ITC opening balance and carry-forward from prior years (amount 1 in Part D)",
    # and never below zero.
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca/itc_claim_limit",
            "less": "ca/itc_opening_balance",
        },
        produces={"output": "ca/itc_part_e_amount_6"},
    ),
    # Form T2038(IND) Part E "Total credit available for carryback (amount 3 minus amount 6)", L:
    # amount 3 less amount 6. No floor is printed.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/itc_part_e_amount_3",
            "less": "ca/itc_part_e_amount_6",
        },
        produces={"output": "ca/itc_amount_l"},
    ),
    # Form T2038(IND) Part E, "Total credit designated for carryback (Add lines 67200, 67210, and
    # 67220. The total cannot be more than amount L)": the three lines added in line order, the
    # third previous year (67200), the second (67210) and the first (67220).
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/itc_carryback_third_previous_year",
                "ca/itc_carryback_second_previous_year",
                "ca/itc_carryback_first_previous_year",
            )
        },
        produces={"output": "ca/itc_carryback_requested"},
    ),
    # Form T2038(IND) Part E amount M, "Total credit designated for carryback (Add lines 67200,
    # 67210, and 67220. The total cannot be more than amount L)": the requested total, refused
    # above L (as Part D amount 15 is refused above its limit), not capped.
    CapabilitySelection(
        name="core/at_most",
        params={},
        consumes={
            "amount": "ca/itc_carryback_requested",
            "bound": "ca/itc_amount_l",
        },
        produces={"output": "ca/itc_amount_m"},
    ),
    # Form T2038(IND) Part E amount 9, "Total current-year refundable credit available (amount 7
    # minus amount 8)": amount 7, "Current year refundable credit (amount A in Part A)", less amount
    # 8, "Adjustment (amount 6 in Part D)". No floor is printed.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/itc_refundable_credits",
            "less": "ca/itc_graduated_rate_estate_allocation",
        },
        produces={"output": "ca/itc_part_e_amount_9"},
    ),
    # Form T2038(IND) Part E amount 12, "Subtotal (amount 10 minus amount 11)": amount 10, "Amount
    # 15 from Part D" (the claim on line 41200), less amount 11, "ITC opening balance and
    # carry-forward from prior years (amount 1 in Part D)". No floor is printed.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/investment_tax_credit",
            "less": "ca/itc_opening_balance",
        },
        produces={"output": "ca/itc_part_e_amount_12"},
    ),
    # Form T2038(IND) Part E amount 14, "Subtotal (amount 12 plus amount 13)": amount 12, and amount
    # 13, "Total credit designated for carryback (amount M in Part E)".
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/itc_part_e_amount_12",
                "ca/itc_amount_m",
            )
        },
        produces={"output": "ca/itc_part_e_amount_14"},
    ),
    # Form T2038(IND) Part E amount 16, "Total (amount 14 minus amount 15, if negative, enter "0")":
    # amount 14 less amount 15, "Current-year non-refundable tax credit (amount F in Part B)", and
    # never below zero.
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca/itc_part_e_amount_14",
            "less": "ca/itc_nonrefundable_credits",
        },
        produces={"output": "ca/itc_part_e_amount_16"},
    ),
    # Form T2038(IND) Part E amount N, "Total credit available for refund (amount 9 minus amount
    # 16)": amount 9 less amount 16. No floor is printed.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/itc_part_e_amount_9",
            "less": "ca/itc_part_e_amount_16",
        },
        produces={"output": "ca/itc_amount_n"},
    ),
    # Form T2038(IND) Part E, "Amount you designate as a refund of ITC (cannot be more than amount
    # N)": the refund the filer designates, refused above N (as Part D amount 15 is refused above
    # its limit), not capped.
    CapabilitySelection(
        name="core/at_most",
        params={},
        consumes={
            "amount": "ca/itc_refund_designation",
            "bound": "ca/itc_amount_n",
        },
        produces={"output": "ca/itc_part_e_amount_17"},
    ),
    # Form T2038(IND) Part E "Refund of ITC (multiply amount 17 by amount 18)", O: amount 17 times
    # amount 18, "The refundable rate" 0.40, of the rate dataset, rounded half-up to the cent. Line
    # 45400 of the return is amount O, "Enter amount O on line 45400 of your income tax and benefit
    # return".
    CapabilitySelection(
        name="core/apply_rate",
        params={"rate": "ca/itc_part_e_refundable_rate"},
        consumes={"base": "ca/itc_part_e_amount_17"},
        produces={"output": "ca/investment_tax_credit_refund"},
    ),
}

WIRING = {
    (
        ApplyRate,
        frozenset({ITC_SRED_EXPENDITURES}),
        frozenset({ITC_SRED_CREDIT}),
    ),
    (
        ApplyRate,
        frozenset({ITC_AGRICULTURAL_SRED_CONTRIBUTIONS}),
        frozenset({ITC_AGRICULTURAL_SRED_CREDIT}),
    ),
    (
        ApplyRate,
        frozenset({ITC_QUALIFIED_PROPERTY}),
        frozenset({ITC_QUALIFIED_PROPERTY_CREDIT}),
    ),
    (
        Sum,
        frozenset(
            {
                ITC_SRED_CREDIT,
                ITC_AGRICULTURAL_SRED_CREDIT,
                ITC_SRED_PARTNERSHIP_ALLOCATION,
                ITC_QUALIFIED_PROPERTY_CREDIT,
            }
        ),
        frozenset({ITC_REFUNDABLE_CREDITS}),
    ),
    (
        ApplyRate,
        frozenset({ITC_MINERAL_EXPLORATION_EXPENDITURES}),
        frozenset({ITC_MINERAL_EXPLORATION_CREDIT}),
    ),
    (
        ApplyRate,
        frozenset({ITC_CRITICAL_MINERAL_EXPENDITURES}),
        frozenset({ITC_CRITICAL_MINERAL_CREDIT}),
    ),
    (
        ApprenticeshipWagesTotal,
        frozenset({ITC_APPRENTICES}),
        frozenset({ITC_APPRENTICESHIP_WAGES_TOTAL}),
    ),
    (
        Sum,
        frozenset({ITC_APPRENTICESHIP_WAGES_TOTAL, ITC_APPRENTICESHIP_T3_BOX_40}),
        frozenset({ITC_APPRENTICESHIP_WAGES_WITH_T3}),
    ),
    (
        ApplyRate,
        frozenset({ITC_APPRENTICESHIP_WAGES_WITH_T3}),
        frozenset({ITC_APPRENTICESHIP_CREDIT}),
    ),
    (
        ApplyRate,
        frozenset({ITC_SRED_REPAYMENT_2014_AND_PRIOR}),
        frozenset({ITC_SRED_REPAYMENT_CREDIT_2014_AND_PRIOR}),
    ),
    (
        ApplyRate,
        frozenset({ITC_SRED_REPAYMENT_2015_AND_AFTER}),
        frozenset({ITC_SRED_REPAYMENT_CREDIT_2015_AND_AFTER}),
    ),
    (
        Sum,
        frozenset(
            {ITC_SRED_REPAYMENT_CREDIT_2014_AND_PRIOR, ITC_SRED_REPAYMENT_CREDIT_2015_AND_AFTER}
        ),
        frozenset({ITC_SRED_REPAYMENT_CREDIT}),
    ),
    (
        Sum,
        frozenset(
            {
                ITC_MINERAL_EXPLORATION_CREDIT,
                ITC_CRITICAL_MINERAL_CREDIT,
                ITC_APPRENTICESHIP_CREDIT,
                ITC_SRED_REPAYMENT_CREDIT,
            }
        ),
        frozenset({ITC_NONREFUNDABLE_CREDITS}),
    ),
    (
        Sum,
        frozenset({ITC_REFUNDABLE_CREDITS, ITC_NONREFUNDABLE_CREDITS}),
        frozenset({ITC_PART_D_SUBTOTAL}),
    ),
    (
        Sum,
        frozenset({ITC_OPENING_BALANCE, ITC_PART_D_SUBTOTAL}),
        frozenset({ITC_PART_D_AMOUNT_5}),
    ),
    (
        Subtract,
        frozenset({ITC_PART_D_AMOUNT_5, ITC_GRADUATED_RATE_ESTATE_ALLOCATION}),
        frozenset({ITC_AVAILABLE}),
    ),
    (
        SubtractNotBelowZero,
        frozenset({FEDERAL_TAX, POLITICAL_CREDIT}),
        frozenset({ITC_PART_D_AMOUNT_9}),
    ),
    (
        SubtractNotBelowZero,
        frozenset({ITC_PART_D_AMOUNT_9, LABOUR_SPONSORED_FUNDS_CREDIT}),
        frozenset({ITC_AMOUNT_H}),
    ),
    (
        LesserOf,
        frozenset({ITC_AVAILABLE, ITC_AMOUNT_H}),
        frozenset({ITC_AMOUNT_I}),
    ),
    (
        Sum,
        frozenset({ITC_AMOUNT_H, FEDERAL_FOREIGN_TAX_CREDIT}),
        frozenset({ITC_PART_D_AMOUNT_13}),
    ),
    (
        SubtractNotBelowZero,
        frozenset({ITC_PART_D_AMOUNT_13, AMT_MINIMUM_AMOUNT}),
        frozenset({ITC_AMOUNT_J}),
    ),
    (
        LesserOf,
        frozenset({ITC_AVAILABLE, ITC_AMOUNT_J}),
        frozenset({ITC_AMOUNT_K}),
    ),
    (
        CountByConditions,
        frozenset({AMT_MINIMUM_TAX_AFTER_REGULAR_TAX}),
        frozenset({ITC_PART_D_AMOUNT_11_APPLIES}),
    ),
    (
        ChooseByCount,
        frozenset({ITC_PART_D_AMOUNT_11_APPLIES, ITC_AMOUNT_I, ITC_AMOUNT_K}),
        frozenset({ITC_CLAIM_LIMIT}),
    ),
    (
        AtMost,
        frozenset({ITC_CLAIM, ITC_CLAIM_LIMIT}),
        frozenset({INVESTMENT_TAX_CREDIT}),
    ),
    (
        Subtract,
        frozenset({ITC_AVAILABLE, ITC_OPENING_BALANCE}),
        frozenset({ITC_PART_E_AMOUNT_3}),
    ),
    (
        SubtractNotBelowZero,
        frozenset({ITC_CLAIM_LIMIT, ITC_OPENING_BALANCE}),
        frozenset({ITC_PART_E_AMOUNT_6}),
    ),
    (
        Subtract,
        frozenset({ITC_PART_E_AMOUNT_3, ITC_PART_E_AMOUNT_6}),
        frozenset({ITC_AMOUNT_L}),
    ),
    (
        Sum,
        frozenset(
            {
                ITC_CARRYBACK_THIRD_PREVIOUS_YEAR,
                ITC_CARRYBACK_SECOND_PREVIOUS_YEAR,
                ITC_CARRYBACK_FIRST_PREVIOUS_YEAR,
            }
        ),
        frozenset({ITC_CARRYBACK_REQUESTED}),
    ),
    (
        AtMost,
        frozenset({ITC_CARRYBACK_REQUESTED, ITC_AMOUNT_L}),
        frozenset({ITC_AMOUNT_M}),
    ),
    (
        Subtract,
        frozenset({ITC_REFUNDABLE_CREDITS, ITC_GRADUATED_RATE_ESTATE_ALLOCATION}),
        frozenset({ITC_PART_E_AMOUNT_9}),
    ),
    (
        Subtract,
        frozenset({INVESTMENT_TAX_CREDIT, ITC_OPENING_BALANCE}),
        frozenset({ITC_PART_E_AMOUNT_12}),
    ),
    (
        Sum,
        frozenset({ITC_PART_E_AMOUNT_12, ITC_AMOUNT_M}),
        frozenset({ITC_PART_E_AMOUNT_14}),
    ),
    (
        SubtractNotBelowZero,
        frozenset({ITC_PART_E_AMOUNT_14, ITC_NONREFUNDABLE_CREDITS}),
        frozenset({ITC_PART_E_AMOUNT_16}),
    ),
    (
        Subtract,
        frozenset({ITC_PART_E_AMOUNT_9, ITC_PART_E_AMOUNT_16}),
        frozenset({ITC_AMOUNT_N}),
    ),
    (
        AtMost,
        frozenset({ITC_REFUND_DESIGNATION, ITC_AMOUNT_N}),
        frozenset({ITC_PART_E_AMOUNT_17}),
    ),
    (
        ApplyRate,
        frozenset({ITC_PART_E_AMOUNT_17}),
        frozenset({INVESTMENT_TAX_CREDIT_REFUND}),
    ),
}
