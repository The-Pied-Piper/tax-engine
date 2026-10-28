"""CA-ON 2025 end to end: return de."""

from __future__ import annotations

from typing import Any

import pytest

from tax_calculator.domain.errors import InputAboveBoundError
from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.catalog import (
    INVESTMENT_TAX_CREDIT_REFUND,
    ITC_AMOUNT_L,
    ITC_AMOUNT_M,
    ITC_AMOUNT_N,
    ITC_AVAILABLE,
    ITC_CARRYBACK_REQUESTED,
    ITC_PART_E_AMOUNT_3,
    ITC_PART_E_AMOUNT_6,
    ITC_PART_E_AMOUNT_9,
    ITC_PART_E_AMOUNT_12,
    ITC_PART_E_AMOUNT_14,
    ITC_PART_E_AMOUNT_16,
    ITC_PART_E_AMOUNT_17,
    TOTAL_CREDITS,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, compute

# The lines of the return that the investment tax credit reads, all zero: the filer has no income,
# deduction or credit beyond the investment tax credit of Parts A, B, D and E.
NO_OTHER_LINES: dict[str, Any] = {
    "employment_income": "0",
    "share_dispositions": (),
    "unused_rrsp_contributions": "0",
    "rrsp_contributions": "0",
    "rrsp_deduction_limit": "0",
    "rrsp_amount_deducted": "0",
    "union_dues": "0",
}


def return_de(
    *,
    qualified_property: str = "20000",
    third: str = "0",
    second: str = "0",
    first: str = "0",
    designation: str = "0",
) -> Worksheet:
    """Return DE as `returns/2025_return_de.yaml` gives it, with the Part E figures given.

    The Part E inputs are the carryback designations on lines 67200, 67210 and 67220 and the refund
    designated as amount 17.
    """
    return compute(
        **{
            **NO_OTHER_LINES,
            "itc_qualified_property": qualified_property,
            "itc_carryback_third_previous_year": third,
            "itc_carryback_second_previous_year": second,
            "itc_carryback_first_previous_year": first,
            "itc_refund_designation": designation,
        }
    )


def test_the_worked_example_without_a_carryback_gives_l_and_n_of_2000_and_a_refund_of_800() -> None:
    # The worked example: 20,000 of qualified property gives amount A of 2000.00, with no opening
    # balance, no federal tax and no non-refundable credit. Amount 3 is 2000.00, amount 6 is 0.00,
    # so L is 2000.00; with no carryback M is 0.00, so N is 2000.00. Designating 2000.00 as the
    # refund gives line 45400 of 800.00 (2000.00 times 0.40).
    worksheet = return_de(designation="2000")

    assert worksheet.get(ITC_AVAILABLE).value == D("2000.00")
    assert worksheet.get(ITC_PART_E_AMOUNT_3).value == D("2000.00")
    assert worksheet.get(ITC_PART_E_AMOUNT_6).value == D("0.00")
    assert worksheet.get(ITC_AMOUNT_L).value == D("2000.00")
    assert worksheet.get(ITC_AMOUNT_M).value == D("0.00")
    assert worksheet.get(ITC_PART_E_AMOUNT_9).value == D("2000.00")
    assert worksheet.get(ITC_PART_E_AMOUNT_12).value == D("0.00")
    assert worksheet.get(ITC_PART_E_AMOUNT_16).value == D("0.00")
    assert worksheet.get(ITC_AMOUNT_N).value == D("2000.00")
    assert worksheet.get(ITC_PART_E_AMOUNT_17).value == D("2000.00")
    assert worksheet.get(INVESTMENT_TAX_CREDIT_REFUND).value == D("800.00")


def test_a_carryback_of_500_to_the_third_year_leaves_n_of_1500_and_a_refund_of_600() -> None:
    # The carryback case: 500.00 designated on line 67200 gives M of 500.00, amount 14 of 500.00 and
    # amount 16 of 500.00, so N is 2000.00 less 500.00, 1500.00. Designating 1500.00 gives line
    # 45400 of 600.00 (1500.00 times 0.40): the 500.00 carried back is not refunded.
    worksheet = return_de(third="500", designation="1500")

    assert worksheet.get(ITC_CARRYBACK_REQUESTED).value == D("500.00")
    assert worksheet.get(ITC_AMOUNT_M).value == D("500.00")
    assert worksheet.get(ITC_PART_E_AMOUNT_14).value == D("500.00")
    assert worksheet.get(ITC_PART_E_AMOUNT_16).value == D("500.00")
    assert worksheet.get(ITC_AMOUNT_N).value == D("1500.00")
    assert worksheet.get(ITC_PART_E_AMOUNT_17).value == D("1500.00")
    assert worksheet.get(INVESTMENT_TAX_CREDIT_REFUND).value == D("600.00")


def test_the_carryback_lines_67200_67210_and_67220_are_added_into_amount_m() -> None:
    # Lines 67200, 67210 and 67220 are added: 200.00, 100.00 and 50.00 is 350.00, and M is that
    # total, not more than L of 2000.00.
    worksheet = return_de(third="200", second="100", first="50")

    assert worksheet.get(ITC_CARRYBACK_REQUESTED).value == D("350.00")
    assert worksheet.get(ITC_AMOUNT_M).value == D("350.00")
    assert worksheet.get(ITC_AMOUNT_N).value == D("1650.00")


def test_a_refund_designation_above_amount_n_is_refused() -> None:
    # Amount 17 "cannot be more than amount N": 2001.00 is above N of 2000.00 and is refused, not
    # capped.
    with pytest.raises(
        InputAboveBoundError, match=r"ca/itc_refund_designation 2001 is above ca/itc_amount_n 2000"
    ):
        return_de(designation="2001")


def test_a_refund_designation_above_amount_n_after_a_carryback_is_refused() -> None:
    # With 500.00 carried back, N is 1500.00, so a designation of 1501.00 is refused.
    with pytest.raises(
        InputAboveBoundError, match=r"ca/itc_refund_designation 1501 is above ca/itc_amount_n 1500"
    ):
        return_de(third="500", designation="1501")


def test_a_carryback_above_amount_l_is_refused() -> None:
    # The carryback total "cannot be more than amount L": 2001.00 is above L of 2000.00 and is
    # refused, not capped.
    with pytest.raises(
        InputAboveBoundError,
        match=r"ca/itc_carryback_requested 2001 is above ca/itc_amount_l 2000",
    ):
        return_de(third="2001")


def test_carrybacks_to_several_previous_years_totalling_more_than_amount_l_are_refused() -> None:
    # The three designations total 2100.00, above L of 2000.00, although no one of them is.
    with pytest.raises(
        InputAboveBoundError,
        match=r"ca/itc_carryback_requested 2100 is above ca/itc_amount_l 2000",
    ):
        return_de(third="1500", second="600")


def test_the_refund_is_at_the_refundable_rate_rounded_half_up_to_the_cent() -> None:
    # 0.0125 designated, at 0.40, is 0.005, which rounds half-up to the cent as 0.01.
    worksheet = return_de(designation="0.0125")

    assert worksheet.get(INVESTMENT_TAX_CREDIT_REFUND).value == D("0.01")


def test_with_no_investment_tax_credit_line_45400_is_zero() -> None:
    # With every Part A and B input 0 and no designation, every Part E amount is 0.00 and line
    # 45400 is 0.00.
    worksheet = return_de(qualified_property="0")

    assert worksheet.get(ITC_AVAILABLE).value == D("0.00")
    assert worksheet.get(ITC_AMOUNT_L).value == D("0.00")
    assert worksheet.get(ITC_AMOUNT_N).value == D("0.00")
    assert worksheet.get(INVESTMENT_TAX_CREDIT_REFUND).value == D("0.00")


def test_line_48200_includes_line_45400() -> None:
    # Line 48200 "Add lines 150 to 165. Total credits" includes line 45400: the same return with a
    # refund of 2000.00 designated has 800.00 more in total credits than with none.
    with_refund = return_de(designation="2000")
    without_refund = return_de(designation="0")

    assert with_refund.get(INVESTMENT_TAX_CREDIT_REFUND).value == D("800.00")
    assert without_refund.get(INVESTMENT_TAX_CREDIT_REFUND).value == D("0.00")
    assert with_refund.get(TOTAL_CREDITS).value - without_refund.get(TOTAL_CREDITS).value == D(
        "800.00"
    )


def test_a_negative_amount_n_refuses_even_a_designation_of_zero() -> None:
    # Amount 9 is amount 7 less amount 8 and the form prints no floor, so a graduated rate estate
    # allocation of 500.00 (amount 8) with amount A of 0.00 gives amount 9 of -500.00, and with
    # 10,000 of flow-through mining expenditures (amount F of 1500.00) amount 16 is 0.00, so N is
    # -500.00. The form's "cannot be more than amount N" then refuses any designation, as Part D
    # refuses a claim above a negative amount I.
    with pytest.raises(InputAboveBoundError, match=r"ca/itc_refund_designation 0 is above"):
        compute(
            **{
                **NO_OTHER_LINES,
                "itc_mineral_exploration_expenditures": "10000",
                "itc_graduated_rate_estate_allocation": "500",
            }
        )
