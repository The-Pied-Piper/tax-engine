"""CA-ON 2025 end to end: return mf, Form T746 "Calculating Your Deduction for Refund of Unused
RRSP, PRPP, and SPP Contributions" as its own form, and its deduction on T1 line 23200.

The worked return `returns/2025_return_mf.yaml` (unused contributions of 4,000.00 for 2024, a T4RSP
box 20 refund of 3,000.00 withdrawn in 2025) is checked by `test_worked_returns.py`. This module
computes each example on its own: the row form `ca/t746_year` (lines 1 to 4, run once for each year
listed), the summary form `ca/t746` (run once: the total of line 4, line 12 and line 13, the
lesser of lines 4 and 12) and the deduction in the line 23200 sum of the return. Line 3 above line
2 is refused, not capped, and a negative amount is refused as for every other input.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

import pytest

from tax_calculator.domain.errors import InputAboveBoundError, NegativeArtifactError
from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.catalog import (
    DEDUCTIONS_FROM_TOTAL_INCOME,
    NET_INCOME,
    T746_CONDITIONS_MET,
    T746_CONTRIBUTIONS_DEDUCTED_CHECKED,
    T746_DEDUCTION,
    T746_DEDUCTION_ON_RETURN,
    T746_LINE_13,
    T746_UNUSED_CONTRIBUTIONS,
    T746_UNUSED_CONTRIBUTIONS_OF_YEAR,
    T746_WITHDRAWALS,
)
from tests.jurisdictions.ca_on.end_to_end.support import CA_ON, D, service, starting

T746 = "ca/t746"
T746_YEAR = "ca/t746_year"
RETURN = "ca-on/return"

# The figures of return MF: the unused contributions of 2024 (line 2 of 10,000.00, line 3 of
# 6,000.00) and the T4RSP box 20 refund; the employment income is 3,000.00.
MF_YEARS = ({"year": 2024, "contributions": "10000", "deducted": "6000"},)
EXPECTED = "expected_to_fully_deduct_contributions"
NOT_INTENDING = "did_not_make_contributions_intending_to_withdraw"
MF_AMOUNTS = {"t4rsp_box_20": "3000", EXPECTED: "1"}


def run(
    *,
    years: Iterable[Mapping[str, Any]] = MF_YEARS,
    amounts: Mapping[str, str] = MF_AMOUNTS,
    rrsp_income: str = "3000",
    **overrides: Any,
) -> dict[str, tuple[Worksheet, ...]]:
    """Every form's worksheets of return MF, with the years, the withdrawals and the T1 line 12900
    amount given: employment income of 3,000.00 and no other income."""
    artifacts = starting(
        "3000",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        rrsp_income=rrsp_income,
        t746_years=list(years),
        t746_amounts=amounts,
        t746_withdrawal_year=2025,
        **overrides,
    )
    return service().compute(CA_ON, 2025, *artifacts)


def return_mf(**overrides: Any) -> Worksheet:
    (worksheet,) = run(**overrides)[RETURN]
    return worksheet


def summary(**overrides: Any) -> Worksheet:
    (worksheet,) = run(**overrides)[T746]
    return worksheet


# --- the deduction of return MF ------------------------------------------------------------------


def test_return_mf_deducts_the_3000_withdrawn_as_the_lesser_of_lines_4_and_12() -> None:
    worksheet = summary()

    assert worksheet.get(T746_UNUSED_CONTRIBUTIONS).value == D("4000.00")
    assert worksheet.get(T746_WITHDRAWALS).value == D("3000.00")
    assert worksheet.get(T746_DEDUCTION).value == D("3000.00")


def test_the_deduction_is_in_line_23200_so_net_income_is_the_employment_income() -> None:
    worksheet = return_mf()

    assert worksheet.get(T746_DEDUCTION_ON_RETURN).value == D("3000.00")
    assert worksheet.get(DEDUCTIONS_FROM_TOTAL_INCOME).value == D("3000.00")
    assert worksheet.get(NET_INCOME).value == D("3000.00")


def test_a_refund_above_the_unused_contributions_deducts_line_4_only() -> None:
    worksheet = summary(amounts={**MF_AMOUNTS, "t4rsp_box_20": "5000"}, rrsp_income="5000")

    assert worksheet.get(T746_WITHDRAWALS).value == D("5000.00")
    assert worksheet.get(T746_DEDUCTION).value == D("4000.00")


def test_line_12_adds_the_five_withdrawals_of_lines_6_to_10() -> None:
    amounts = {
        EXPECTED: "1",
        "t4rsp_box_20": "100",
        "t4rsp_box_22": "200",
        "t4rif_box_24": "300",
        "t4a_box_194": "400",
        "t4a_box_18_spp": "500",
    }

    assert summary(amounts=amounts).get(T746_WITHDRAWALS).value == D("1500.00")
    assert summary(amounts=amounts).get(T746_DEDUCTION).value == D("1500.00")


# --- the two conditions of "For you to claim the deduction" -------------------------------------


@pytest.mark.parametrize(
    ("expected", "not_intending", "met", "deduction"),
    [
        ("1", "0", 1, "3000.00"),
        ("0", "1", 1, "3000.00"),
        ("1", "1", 1, "3000.00"),
        ("0", "0", 0, "0.00"),
    ],
)
def test_the_deduction_is_allowed_when_one_or_both_conditions_are_yes(
    expected: str, not_intending: str, met: int, deduction: str
) -> None:
    worksheet = summary(
        amounts={"t4rsp_box_20": "3000", EXPECTED: expected, NOT_INTENDING: not_intending}
    )

    assert worksheet.get(T746_CONDITIONS_MET).value == met
    assert worksheet.get(T746_LINE_13).value == D("3000.00")
    assert worksheet.get(T746_DEDUCTION).value == D(deduction)


def test_with_neither_condition_yes_nothing_reaches_line_23200_but_the_refund_is_still_income() -> (
    None
):
    worksheet = return_mf(amounts={"t4rsp_box_20": "3000"})

    assert worksheet.get(T746_DEDUCTION_ON_RETURN).value == D("0.00")
    assert worksheet.get(NET_INCOME).value == D("6000.00")


def test_the_answers_are_required_to_be_1_or_0() -> None:
    with pytest.raises(InputAboveBoundError, match="t746_expected_to_fully_deduct_contributions"):
        summary(amounts={"t4rsp_box_20": "3000", EXPECTED: "2"})


# --- the years -----------------------------------------------------------------------------------


def test_each_year_listed_has_its_own_line_4_and_the_total_is_the_most_recent_form_s_line_4() -> (
    None
):
    years = (
        {"year": 2023, "contributions": "2000", "deducted": "500"},
        {"year": 2024, "contributions": "3000", "deducted": "500"},
    )
    result = run(years=years)

    lines_4 = [each.get(T746_UNUSED_CONTRIBUTIONS_OF_YEAR).value for each in result[T746_YEAR]]
    assert lines_4 == [D("1500.00"), D("2500.00")]
    (worksheet,) = result[T746]
    assert worksheet.get(T746_UNUSED_CONTRIBUTIONS).value == D("4000.00")


def test_with_no_year_listed_line_4_is_0_and_nothing_is_deducted() -> None:
    result = run(years=())

    assert result[T746_YEAR] == ()
    (worksheet,) = result[T746]
    assert worksheet.get(T746_UNUSED_CONTRIBUTIONS).value == D("0.00")
    assert worksheet.get(T746_DEDUCTION).value == D("0.00")


def test_with_no_t746_entered_the_line_23200_sum_has_nothing_from_the_form() -> None:
    worksheet = return_mf(years=(), amounts={}, rrsp_income="0")

    assert worksheet.get(T746_DEDUCTION_ON_RETURN).value == D("0.00")
    assert worksheet.get(DEDUCTIONS_FROM_TOTAL_INCOME).value == D("0.00")


# --- the refusals --------------------------------------------------------------------------------


def test_line_3_equal_to_line_2_leaves_nothing_unused() -> None:
    years = ({"year": 2024, "contributions": "6000", "deducted": "6000"},)
    result = run(years=years)

    (year,) = result[T746_YEAR]
    assert year.get(T746_UNUSED_CONTRIBUTIONS_OF_YEAR).value == D("0.00")
    assert year.get(T746_CONTRIBUTIONS_DEDUCTED_CHECKED).value == D("6000")


def test_line_3_above_line_2_is_refused_not_capped() -> None:
    years = ({"year": 2024, "contributions": "6000", "deducted": "6000.01"},)

    with pytest.raises(InputAboveBoundError):
        run(years=years)


def test_a_negative_withdrawal_is_refused() -> None:
    with pytest.raises(NegativeArtifactError):
        run(amounts={"t4rsp_box_20": "-1"})


def test_a_negative_line_2_is_refused() -> None:
    years = ({"year": 2024, "contributions": "-1", "deducted": "0"},)

    with pytest.raises(NegativeArtifactError):
        run(years=years)
