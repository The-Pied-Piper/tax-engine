"""CA-ON 2025 end to end: return mi, Form T1043 "Deduction for Excess Registered Pension Plan
Transfers You Withdrew from an RRSP, a PRPP, an SPP, or a RRIF" as its own form, and its deduction
on T1 line 23200.

The worked return `returns/2025_return_mi.yaml` (excess transfers of 8,000.00 with 1,500.00
claimed before, 17,000.00 withdrawn from an RRSP of which 12,000.00 is deductible elsewhere) is
checked by `test_worked_returns.py`. This module computes each example on its own: the form
`ca/t1043` (run once: lines 1 to 9) and the deduction in the line 23200 sum of the return. A part
above its whole (line 2 plus line 3 above line 1, line 7 above line 6) is refused, not capped, and
a negative amount is refused as for every other input.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import pytest

from tax_calculator.domain.errors import InputAboveBoundError, NegativeArtifactError
from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.catalog import (
    DEDUCTIONS_FROM_TOTAL_INCOME,
    NET_INCOME,
    T1043_DEDUCTION,
    T1043_DEDUCTION_ON_RETURN,
    T1043_EXCESS_TRANSFERRED,
    T1043_NOT_YET_CLAIMED,
    T1043_PLAN_AMOUNTS_REMAINING,
    T1043_PREVIOUSLY_CLAIMED_CHECKED,
)
from tests.jurisdictions.ca_on.end_to_end.support import CA_ON, D, service, starting

T1043 = "ca/t1043"
RETURN = "ca-on/return"

# The figures of return MI: the excess transfers (8,000.00 on the T4A slip, 9,000.00 on the receipt;
# 1,000.00 and 500.00 claimed before) and the RRSP withdrawal (17,000.00, of which 12,000.00 is
# deductible elsewhere); there is no other income.
MI_AMOUNTS = {
    "excess_transfer_on_t4a": "8000",
    "excess_amount_on_receipt": "9000",
    "claimed_as_rrsp_deduction": "1000",
    "deducted_using_form": "500",
    "plan_amounts_in_income": "17000",
    "part_deductible_elsewhere": "12000",
    "included_excess_in_income_for_year_transferred": "1",
    "including_plan_amounts_in_income_for_year_claimed": "1",
}


def run(
    *, rrsp_income: str = "17000", changes: Mapping[str, str] | None = None, **overrides: Any
) -> dict[str, tuple[Worksheet, ...]]:
    """Every form's worksheets of return MI, with the Form T1043 amounts of MI changed by `changes`
    and the T1 line 12900 amount given: no other income."""
    artifacts = starting(
        "0",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        rrsp_income=rrsp_income,
        t1043_amounts={**MI_AMOUNTS, **(changes or {})},
        **overrides,
    )
    return service().compute(CA_ON, 2025, *artifacts)


def return_mi(**overrides: Any) -> Worksheet:
    (worksheet,) = run(**overrides)[RETURN]
    return worksheet


def form(**overrides: Any) -> Worksheet:
    (worksheet,) = run(**overrides)[T1043]
    return worksheet


# --- the deduction of return MI ------------------------------------------------------------------


def test_return_mi_deducts_5000_as_the_lesser_of_lines_5_and_8() -> None:
    worksheet = form()

    assert worksheet.get(T1043_EXCESS_TRANSFERRED).value == D("8000.00")
    assert worksheet.get(T1043_PREVIOUSLY_CLAIMED_CHECKED).value == D("1500.00")
    assert worksheet.get(T1043_NOT_YET_CLAIMED).value == D("6500.00")
    assert worksheet.get(T1043_PLAN_AMOUNTS_REMAINING).value == D("5000.00")
    assert worksheet.get(T1043_DEDUCTION).value == D("5000.00")


def test_the_deduction_is_in_line_23200_so_net_income_is_the_withdrawal_less_it() -> None:
    worksheet = return_mi()

    assert worksheet.get(T1043_DEDUCTION_ON_RETURN).value == D("5000.00")
    assert worksheet.get(DEDUCTIONS_FROM_TOTAL_INCOME).value == D("5000.00")
    assert worksheet.get(NET_INCOME).value == D("12000.00")


def test_plan_amounts_of_30000_with_15000_deductible_elsewhere_leave_line_5_the_lesser() -> None:
    worksheet = form(
        rrsp_income="30000",
        changes={"plan_amounts_in_income": "30000", "part_deductible_elsewhere": "15000"},
    )

    assert worksheet.get(T1043_PLAN_AMOUNTS_REMAINING).value == D("15000.00")
    assert worksheet.get(T1043_NOT_YET_CLAIMED).value == D("6500.00")
    assert worksheet.get(T1043_DEDUCTION).value == D("6500.00")


def test_line_1_is_the_lesser_of_the_t4a_excess_transfer_and_the_receipt_excess_amount() -> None:
    worksheet = form(changes={"excess_amount_on_receipt": "7000"})

    assert worksheet.get(T1043_EXCESS_TRANSFERRED).value == D("7000.00")
    assert worksheet.get(T1043_NOT_YET_CLAIMED).value == D("5500.00")


def test_with_no_t1043_entered_the_line_23200_sum_has_nothing_from_the_form() -> None:
    worksheet = return_mi(
        rrsp_income="0",
        changes={key: "0" for key in MI_AMOUNTS},
    )

    assert worksheet.get(T1043_DEDUCTION_ON_RETURN).value == D("0.00")
    assert worksheet.get(DEDUCTIONS_FROM_TOTAL_INCOME).value == D("0.00")


# --- the two conditions "you have to meet both" -------------------------------------------------


def test_a_no_to_the_first_condition_leaves_a_deduction_of_0() -> None:
    worksheet = form(changes={"included_excess_in_income_for_year_transferred": "0"})

    assert worksheet.get(T1043_NOT_YET_CLAIMED).value == D("6500.00")
    assert worksheet.get(T1043_PLAN_AMOUNTS_REMAINING).value == D("5000.00")
    assert worksheet.get(T1043_DEDUCTION).value == D("0.00")


def test_a_no_to_the_second_condition_leaves_a_deduction_of_0() -> None:
    worksheet = return_mi(changes={"including_plan_amounts_in_income_for_year_claimed": "0"})

    assert worksheet.get(T1043_DEDUCTION_ON_RETURN).value == D("0.00")
    assert worksheet.get(DEDUCTIONS_FROM_TOTAL_INCOME).value == D("0.00")
    assert worksheet.get(NET_INCOME).value == D("17000.00")


def test_a_no_to_both_conditions_leaves_a_deduction_of_0() -> None:
    worksheet = form(
        changes={
            "included_excess_in_income_for_year_transferred": "0",
            "including_plan_amounts_in_income_for_year_claimed": "0",
        }
    )

    assert worksheet.get(T1043_DEDUCTION).value == D("0.00")


@pytest.mark.parametrize(
    "answer",
    [
        "included_excess_in_income_for_year_transferred",
        "including_plan_amounts_in_income_for_year_claimed",
    ],
)
def test_an_answer_other_than_1_or_0_is_refused(answer: str) -> None:
    with pytest.raises(InputAboveBoundError):
        run(changes={answer: "2"})


# --- the refusals --------------------------------------------------------------------------------


def test_lines_2_and_3_adding_up_to_line_1_leave_nothing_not_yet_claimed() -> None:
    worksheet = form(changes={"claimed_as_rrsp_deduction": "7500", "deducted_using_form": "500"})

    assert worksheet.get(T1043_PREVIOUSLY_CLAIMED_CHECKED).value == D("8000.00")
    assert worksheet.get(T1043_NOT_YET_CLAIMED).value == D("0.00")
    assert worksheet.get(T1043_DEDUCTION).value == D("0.00")


def test_line_4_above_line_1_is_refused_not_capped() -> None:
    with pytest.raises(InputAboveBoundError):
        run(changes={"claimed_as_rrsp_deduction": "7500", "deducted_using_form": "500.01"})


def test_line_7_equal_to_line_6_leaves_nothing_on_line_8() -> None:
    worksheet = form(changes={"part_deductible_elsewhere": "17000"})

    assert worksheet.get(T1043_PLAN_AMOUNTS_REMAINING).value == D("0.00")
    assert worksheet.get(T1043_DEDUCTION).value == D("0.00")


def test_line_7_above_line_6_is_refused_not_capped() -> None:
    with pytest.raises(InputAboveBoundError):
        run(changes={"part_deductible_elsewhere": "17000.01"})


def test_a_negative_amount_is_refused() -> None:
    with pytest.raises(NegativeArtifactError):
        run(changes={"plan_amounts_in_income": "-1"})
