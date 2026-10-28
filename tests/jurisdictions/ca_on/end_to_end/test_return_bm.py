"""CA-ON 2025 end to end: return bm."""

from __future__ import annotations

from typing import Any

import pytest

from tax_calculator.domain.errors import InputAboveBoundError
from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.catalog import (
    AMT_MINIMUM_TAX_AFTER_REGULAR_TAX,
    CREDITS_AGAINST_FEDERAL_TAX,
    FEDERAL_TAX_WITH_ITC_RECAPTURE,
    INVESTMENT_TAX_CREDIT,
    ITC_AGRICULTURAL_SRED_CREDIT,
    ITC_AMOUNT_H,
    ITC_AMOUNT_I,
    ITC_AMOUNT_J,
    ITC_AMOUNT_K,
    ITC_APPRENTICESHIP_CREDIT,
    ITC_APPRENTICESHIP_WAGES_TOTAL,
    ITC_APPRENTICESHIP_WAGES_WITH_T3,
    ITC_AVAILABLE,
    ITC_CLAIM_LIMIT,
    ITC_CRITICAL_MINERAL_CREDIT,
    ITC_MINERAL_EXPLORATION_CREDIT,
    ITC_NONREFUNDABLE_CREDITS,
    ITC_PART_D_AMOUNT_5,
    ITC_PART_D_AMOUNT_11_APPLIES,
    ITC_PART_D_SUBTOTAL,
    ITC_QUALIFIED_PROPERTY_CREDIT,
    ITC_REFUNDABLE_CREDITS,
    ITC_SRED_CREDIT,
    ITC_SRED_REPAYMENT_CREDIT,
    ITC_SRED_REPAYMENT_CREDIT_2014_AND_PRIOR,
    ITC_SRED_REPAYMENT_CREDIT_2015_AND_AFTER,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, compute

# The lines of the return that the investment tax credit reads, all zero: the filer has no income,
# deduction or credit beyond the investment tax credit lines of Parts A, B and D.
NO_OTHER_LINES: dict[str, Any] = {
    "employment_income": "0",
    "share_dispositions": (),
    "unused_rrsp_contributions": "0",
    "rrsp_contributions": "0",
    "rrsp_deduction_limit": "0",
    "rrsp_amount_deducted": "0",
    "union_dues": "0",
}

# The acceptance figures of the ticket: 10,000 of qualified property (line 67140) and no other
# entries, federal tax (line 40600) of 5,000.00, no line 41000 or 41400 and no AMT. The federal tax
# comes from the employment income of 56135.20: the engine gives 5000.00 for it (56135 gives
# 4999.97 and 56136 gives 5000.11, and the cents from 56135.15 to 56135.21 each give 5000.00), and
# it gives 0 for Form T691 Part 5 line 7, so no AMT applies and the limit is amount I.
ACCEPTANCE: dict[str, Any] = {
    **NO_OTHER_LINES,
    "employment_income": "56135.20",
    "itc_qualified_property": "10000",
}

# The AMT case: employment income of 40000 gives line 40600 of 2837.98 (the engine), and a tax
# shelter loss of 300000 gives Form T691 Part 5 line 7 of 28904.25 (more than 0, so AMT applies)
# and the minimum amount of line 103 of 31742.23. With an opening balance of 5000.00, G is 5000.00,
# I is the lesser of G and H, 2837.98, and J is 2837.98 minus 31742.23, not below zero, so 0.00 and
# K is 0.00. The condition applies, so the limit is K, 0.00, and not I.
AMT_APPLIES: dict[str, Any] = {
    **NO_OTHER_LINES,
    "employment_income": "40000",
    "amt_tax_shelter_losses": "300000",
    "itc_opening_balance": "5000",
}


def return_bm(**overrides: Any) -> Worksheet:
    """Return BM's Parts A, B and D lines, as in `returns/2025_return_bm.yaml`, with overrides."""
    inputs: dict[str, Any] = {
        **NO_OTHER_LINES,
        "itc_sred_expenditures": "40000",
        "itc_agricultural_sred_contributions": "10000",
        "itc_sred_partnership_allocation": "2000",
        "itc_qualified_property": "10000",
        "itc_mineral_exploration_expenditures": "20000",
        "itc_critical_mineral_expenditures": "5000",
        "itc_apprentices": ("25000", "15000"),
        "itc_apprenticeship_t3_box_40": "5000",
        "itc_sred_repayment_2014_and_prior": "1000",
        "itc_sred_repayment_2015_and_after": "2000",
    }
    return compute(**{**inputs, **overrides})


def test_return_bm_amount_1_is_the_sred_expenditures_at_15_percent() -> None:
    # Return BM, Part A line 1: line 67120 of 40000.00 times 0.15 is 6000.00.
    worksheet = return_bm()

    assert worksheet.get(ITC_SRED_CREDIT).value == D("6000.00")


def test_return_bm_amount_2_is_the_agricultural_contributions_at_15_percent() -> None:
    # Return BM, Part A line 2: line 67130 of 10000.00 times 0.15 is 1500.00.
    worksheet = return_bm()

    assert worksheet.get(ITC_AGRICULTURAL_SRED_CREDIT).value == D("1500.00")


def test_return_bm_amount_4_is_the_qualified_property_at_10_percent() -> None:
    # Return BM, Part A line 4: line 67140 of 10000.00 times 0.10 is 1000.00.
    worksheet = return_bm()

    assert worksheet.get(ITC_QUALIFIED_PROPERTY_CREDIT).value == D("1000.00")


def test_return_bm_amount_a_adds_amounts_1_to_4_with_the_partnership_allocation() -> None:
    # Return BM, Part A amount A: 6000.00 plus 1500.00 plus the partnership allocation of 2000.00
    # (line 67135, read as it is) plus 1000.00, 10500.00.
    worksheet = return_bm()

    assert worksheet.get(ITC_REFUNDABLE_CREDITS).value == D("10500.00")


def test_return_bm_amounts_b_and_c_are_at_15_and_30_percent() -> None:
    # Return BM, Part B: line 67170 of 20000.00 times 0.15 is amount B, 3000.00; line 67175 of
    # 5000.00 times 0.30 is amount C, 1500.00.
    worksheet = return_bm()

    assert worksheet.get(ITC_MINERAL_EXPLORATION_CREDIT).value == D("3000.00")
    assert worksheet.get(ITC_CRITICAL_MINERAL_CREDIT).value == D("1500.00")


def test_return_bm_table_1_column_3_is_the_lesser_of_each_apprentice_and_20000() -> None:
    # Return BM, Table 1: the apprentice of 25000.00 counts 20000.00, the one of 15000.00 counts
    # 15000.00, so column 3 totals 35000.00.
    worksheet = return_bm()

    assert worksheet.get(ITC_APPRENTICESHIP_WAGES_TOTAL).value == D("35000.00")


def test_return_bm_one_apprentice_over_20000_is_counted_at_20000() -> None:
    # Table 1 column 3 for a single apprentice of 25000.00: the lesser of that and 20000.00.
    worksheet = return_bm(itc_apprentices=("25000",))

    assert worksheet.get(ITC_APPRENTICESHIP_WAGES_TOTAL).value == D("20000.00")


def test_return_bm_line_67180_adds_the_t3_box_40_amount_and_amount_d_is_10_percent() -> None:
    # Return BM, Part B line 67180: 35000.00 plus the T3 box 40 amount of 5000.00 is 40000.00, and
    # amount D is 40000.00 times 0.10, 4000.00.
    worksheet = return_bm()

    assert worksheet.get(ITC_APPRENTICESHIP_WAGES_WITH_T3).value == D("40000.00")
    assert worksheet.get(ITC_APPRENTICESHIP_CREDIT).value == D("4000.00")


def test_return_bm_amount_e_adds_the_2014_and_prior_and_2015_and_after_repayments() -> None:
    # Return BM, Part B repayments: line 67184 of 1000.00 times 0.20 is amount 1, 200.00; line
    # 67185 of 2000.00 times 0.15 is amount 2, 300.00; amount E is 500.00.
    worksheet = return_bm()

    assert worksheet.get(ITC_SRED_REPAYMENT_CREDIT_2014_AND_PRIOR).value == D("200.00")
    assert worksheet.get(ITC_SRED_REPAYMENT_CREDIT_2015_AND_AFTER).value == D("300.00")
    assert worksheet.get(ITC_SRED_REPAYMENT_CREDIT).value == D("500.00")


def test_return_bm_amount_f_adds_amounts_b_c_d_and_e() -> None:
    # Return BM, Part B amount F: 3000.00 plus 1500.00 plus 4000.00 plus 500.00, 9000.00.
    worksheet = return_bm()

    assert worksheet.get(ITC_NONREFUNDABLE_CREDITS).value == D("9000.00")


def test_the_ticket_acceptance_qualified_property_of_10000_gives_amount_4_and_a_of_1000() -> None:
    # The acceptance figure: 10,000 of qualified property (line 67140) and no other entries
    # gives amount 4 of 1,000.00, and amount A of 1,000.00.
    worksheet = compute(**{**NO_OTHER_LINES, "itc_qualified_property": "10000"})

    assert worksheet.get(ITC_QUALIFIED_PROPERTY_CREDIT).value == D("1000.00")
    assert worksheet.get(ITC_REFUNDABLE_CREDITS).value == D("1000.00")


def test_return_bm_part_d_subtotal_adds_amounts_a_and_f_into_g() -> None:
    # Return BM, Part D: amount 2 is amount A, 10500.00, and amount 3 is amount F, 9000.00, so
    # amount 4 is 19500.00. No opening balance (amount 1) is entered, so amount 5 is 19500.00, and
    # with no graduated rate estate allocation (amount 6), G is 19500.00.
    worksheet = return_bm()

    assert worksheet.get(ITC_PART_D_SUBTOTAL).value == D("19500.00")
    assert worksheet.get(ITC_PART_D_AMOUNT_5).value == D("19500.00")
    assert worksheet.get(ITC_AVAILABLE).value == D("19500.00")


def test_return_bm_with_no_income_amount_i_is_0_and_any_claim_is_refused() -> None:
    # Return BM, Part D with no income: the federal tax of line 40600 is 0, so amount H is 0.00 and
    # I, the lesser of G and H, is 0.00. No AMT applies (the condition counts 0), so the limit is I,
    # and the claim of 0 gives line 41200 of 0.00. A claim of 1 is above the limit and refused.
    worksheet = return_bm()

    assert worksheet.get(ITC_AMOUNT_H).value == D("0.00")
    assert worksheet.get(ITC_AMOUNT_I).value == D("0.00")
    assert worksheet.get(ITC_PART_D_AMOUNT_11_APPLIES).value == 0
    assert worksheet.get(ITC_CLAIM_LIMIT).value == D("0.00")
    assert worksheet.get(INVESTMENT_TAX_CREDIT).value == D("0.00")
    with pytest.raises(InputAboveBoundError, match=r"ca/itc_claim 1 is above ca/itc_claim_limit 0"):
        return_bm(itc_claim="1")


def test_the_ticket_acceptance_figures_give_federal_tax_5000_and_amount_i_of_1000() -> None:
    # The acceptance figures: 10,000 of qualified property and no other entries, with federal tax
    # (line 40600) of 5000.00, no AMT (the condition counts 0): amount A is 1000.00, G is 1000.00,
    # H is 5000.00 and I, the lesser of G and H, is 1000.00.
    worksheet = compute(**ACCEPTANCE)

    assert worksheet.get(FEDERAL_TAX_WITH_ITC_RECAPTURE).value == D("5000.00")
    assert worksheet.get(ITC_REFUNDABLE_CREDITS).value == D("1000.00")
    assert worksheet.get(ITC_AVAILABLE).value == D("1000.00")
    assert worksheet.get(ITC_AMOUNT_H).value == D("5000.00")
    assert worksheet.get(ITC_PART_D_AMOUNT_11_APPLIES).value == 0
    assert worksheet.get(ITC_AMOUNT_I).value == D("1000.00")
    assert worksheet.get(ITC_CLAIM_LIMIT).value == D("1000.00")


def test_a_claim_of_1000_on_the_acceptance_figures_is_line_41200_of_1000() -> None:
    # Amount 15 is the claim up to the limit: a claim of 1000 against I of 1000.00 gives line 41200
    # of 1000.00.
    worksheet = compute(**{**ACCEPTANCE, "itc_claim": "1000"})

    assert worksheet.get(INVESTMENT_TAX_CREDIT).value == D("1000.00")


def test_line_138_adds_line_41200_to_the_credits_against_federal_tax() -> None:
    # T1 line 138 (line 41600) "Add lines 135 to 137.": line 135 (41000) and line 137 (41400) are 0
    # on these figures, so line 138 is line 136 (41200), 1000.00, the claim of 1000 up to I.
    worksheet = compute(**{**ACCEPTANCE, "itc_claim": "1000"})

    assert worksheet.get(CREDITS_AGAINST_FEDERAL_TAX).value == D("1000.00")


def test_a_claim_above_amount_i_on_the_acceptance_figures_is_refused() -> None:
    # The claim of 1001 is above the limit I of 1000.00 and refused, not capped, as Form T691 Part
    # 3 line 12 is.
    with pytest.raises(
        InputAboveBoundError, match=r"ca/itc_claim 1001 is above ca/itc_claim_limit 1000"
    ):
        compute(**{**ACCEPTANCE, "itc_claim": "1001"})


def test_when_t691_part_5_line_7_is_positive_amount_k_limits_the_claim_not_amount_i() -> None:
    # With AMT applying, amount I is 2837.98 (the lesser of G, 5000.00, and H, 2837.98), but J is
    # 0.00 and K, the lesser of G and J, is 0.00: the count of the condition is 1, so the limit is
    # K.
    worksheet = compute(**AMT_APPLIES)

    assert worksheet.get(AMT_MINIMUM_TAX_AFTER_REGULAR_TAX).value == D("28904.25")
    assert worksheet.get(ITC_AVAILABLE).value == D("5000.00")
    assert worksheet.get(ITC_AMOUNT_I).value == D("2837.98")
    assert worksheet.get(ITC_PART_D_AMOUNT_11_APPLIES).value == 1
    assert worksheet.get(ITC_AMOUNT_J).value == D("0")
    assert worksheet.get(ITC_AMOUNT_K).value == D("0")
    assert worksheet.get(ITC_CLAIM_LIMIT).value == D("0")


def test_a_negative_amount_g_refuses_the_return_because_the_form_prints_no_floor() -> None:
    # Form T2038 prints no floor on amount G (amount 5 less amount 6); here the graduated rate
    # estate allocation of 2000 exceeds amount 5, 1000.00, so G and I are -1000.00. Form T691 Part
    # 3 line 12 claim of 0 is then above I and refused.
    with pytest.raises(InputAboveBoundError, match=r"ca/itc_amount_i -1000"):
        compute(**{**ACCEPTANCE, "itc_graduated_rate_estate_allocation": "2000"})


def test_a_claim_within_amount_i_but_above_amount_k_is_refused_when_t691_applies() -> None:
    # The claim of 1000 is within I, 2837.98, but above K, 0.00, the limit when Form T691 Part 5
    # line 7 is positive, so it is refused naming the limit K.
    with pytest.raises(
        InputAboveBoundError, match=r"ca/itc_claim 1000 is above ca/itc_claim_limit 0"
    ):
        compute(**{**AMT_APPLIES, "itc_claim": "1000"})
