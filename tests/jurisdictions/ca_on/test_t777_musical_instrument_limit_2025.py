"""The musical instrument expenses limit of Guide T4044 (2025) "Part 2 - Musical instrument
expenses", end to end.

Guide T4044: "the amount of musical instrument expenses you can deduct cannot be more than your
income for the year from your employment as a musician after deducting all other employment
expenses." Each test fills Form T777 with a musician whose income is 10,000 and whose other
employment expenses (line 8) are 7,000, so the limit is 3,000, and changes the figures:
- lines 12 and 13 together (the capital cost allowance is among the amounts deducted for the
  instrument) are refused above the limit, never capped;
- every other page 1 line takes from the limit;
- lines 20700 and 21200 of the return take from it too, as they do in the line 16 chart;
- the income as a musician is a part of the employment income of the return, so more than it is
  refused;
- the limit is never below zero.
"""

from __future__ import annotations

import pytest

from tax_engine.domain.errors import InputAboveBoundError
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog import (
    CCA_ADDITIONS,
    CCA_CLAIMED,
    CCA_CLASS_NUMBER,
    CCA_UCC_AT_START,
    T777_EMPLOYMENT_EXPENSES_OTHER_THAN_MUSICAL_INSTRUMENT,
    T777_LINE_13,
    T777_MUSICAL_INSTRUMENT_EXPENSES_CHECKED,
    T777_MUSICAL_INSTRUMENT_EXPENSES_DEDUCTED,
    T777_MUSICAL_INSTRUMENT_EXPENSES_MAXIMUM_DEDUCTION,
    T777_MUSICIAN_EMPLOYMENT_INCOME_CHECKED,
)
from tests.jurisdictions.ca_on.end_to_end.support import CA_ON, D, service, starting
from tests.jurisdictions.ca_on.end_to_end.test_return_ee import run as run_class_8
from tests.jurisdictions.ca_on.end_to_end.test_return_hi import t777_form

BOUND = "t777_musical_instrument_expenses_maximum_deduction"
MUSICIAN = {"musician_employment_income": "10000", "other_expenses": "7000"}


def form(**changes: str) -> Worksheet:
    """The T777 worksheet of the musician with the figures `changes`, on a return with 10,000 of
    employment income."""
    return t777_form(employment="10000", **{**MUSICIAN, **changes})


def test_the_limit_is_the_musician_income_minus_all_the_other_employment_expenses() -> None:
    worksheet = form(musical_instrument_expenses="1200")

    assert worksheet.get(T777_EMPLOYMENT_EXPENSES_OTHER_THAN_MUSICAL_INSTRUMENT).value == D("7000")
    assert worksheet.get(T777_MUSICAL_INSTRUMENT_EXPENSES_MAXIMUM_DEDUCTION).value == D("3000")
    assert worksheet.get(T777_MUSICAL_INSTRUMENT_EXPENSES_CHECKED).value == D("1200")


def test_a_deduction_at_the_limit_is_accepted() -> None:
    worksheet = form(musical_instrument_expenses="3000")

    assert worksheet.get(T777_MUSICAL_INSTRUMENT_EXPENSES_DEDUCTED).value == D("3000")
    assert worksheet.get(T777_MUSICAL_INSTRUMENT_EXPENSES_CHECKED).value == D("3000")


def test_a_deduction_of_one_cent_above_the_limit_is_refused() -> None:
    with pytest.raises(InputAboveBoundError, match=BOUND):
        form(musical_instrument_expenses="3000.01")


@pytest.mark.parametrize(
    "line",
    [
        "accounting_and_legal_fees",
        "advertising_and_promotion",
        "lodging",
        "parking",
        "office_supplies",
    ],
)
def test_each_other_expense_of_lines_1_to_11_takes_from_the_limit(line: str) -> None:
    # The other expenses are 7,000 + 100 = 7,100, so the limit is 2,900.
    worksheet = form(**{line: "100"}, musical_instrument_expenses="2900")

    assert worksheet.get(T777_MUSICAL_INSTRUMENT_EXPENSES_MAXIMUM_DEDUCTION).value == D("2900")
    with pytest.raises(InputAboveBoundError, match=BOUND):
        form(**{line: "100"}, musical_instrument_expenses="2900.01")


def test_the_meals_line_takes_from_the_limit_after_its_50_percent() -> None:
    # Line 4: 400 x 50% = 200, so the other expenses are 7,200 and the limit 2,800.
    worksheet = form(food_beverages_entertainment="400", musical_instrument_expenses="2800")

    assert worksheet.get(T777_MUSICAL_INSTRUMENT_EXPENSES_MAXIMUM_DEDUCTION).value == D("2800.00")
    with pytest.raises(InputAboveBoundError, match=BOUND):
        form(food_beverages_entertainment="400", musical_instrument_expenses="2800.01")


def test_expenses_above_the_income_leave_a_limit_of_zero_and_no_deduction() -> None:
    worksheet = form(other_expenses="10500")

    assert worksheet.get(T777_MUSICAL_INSTRUMENT_EXPENSES_MAXIMUM_DEDUCTION).value == D("0")
    with pytest.raises(InputAboveBoundError, match=BOUND):
        form(other_expenses="10500", musical_instrument_expenses="0.01")


def test_no_musician_income_and_no_deduction_is_accepted() -> None:
    worksheet = t777_form(employment="10000", other_expenses="500")

    assert worksheet.get(T777_MUSICAL_INSTRUMENT_EXPENSES_CHECKED).value == D("0")


def test_a_deduction_with_no_musician_income_is_refused() -> None:
    with pytest.raises(InputAboveBoundError, match=BOUND):
        t777_form(employment="10000", musical_instrument_expenses="1")


def test_the_capital_cost_allowance_of_line_13_counts_with_line_12() -> None:
    # Class 8 at 20% of 9,000 is 1,800 (line 13); with 1,200 on line 12 that is 3,000, the limit of
    # an income of 3,000 and no other expenses.
    worksheet = run_class_8(
        class_8=[{CCA_CLASS_NUMBER: "8", CCA_UCC_AT_START: "9000", CCA_CLAIMED: "1800"}],
        musician_income="1800",
    )

    assert worksheet.get(T777_LINE_13).value == D("1800.00")
    assert worksheet.get(T777_MUSICAL_INSTRUMENT_EXPENSES_CHECKED).value == D("1800.00")


def test_a_capital_cost_allowance_above_the_limit_is_refused() -> None:
    with pytest.raises(InputAboveBoundError, match=BOUND):
        run_class_8(
            class_8=[
                {
                    CCA_CLASS_NUMBER: "8",
                    CCA_UCC_AT_START: "9000",
                    CCA_ADDITIONS: "0",
                    CCA_CLAIMED: "1800",
                }
            ],
            musician_income="1799.99",
        )


def with_return_deductions(
    *, union_dues: str = "0", rpp_deduction: str = "0", **changes: str
) -> Worksheet:
    """The T777 worksheet of the musician on a return with the union dues of line 21200 and the
    registered pension plan deduction of line 20700 given."""
    artifacts = starting(
        "10000",
        (),
        "0",
        "0",
        "0",
        "0",
        union_dues,
        rpp_deduction=rpp_deduction,
        t777_amounts={**MUSICIAN, **changes},
    )
    (worksheet,) = service().compute(CA_ON, 2025, *artifacts)["ca/t777"]
    return worksheet


@pytest.mark.parametrize("deduction", ["union_dues", "rpp_deduction"])
def test_lines_20700_and_21200_take_from_the_limit(deduction: str) -> None:
    # Line 52 of the line 16 chart adds both to line 15 for "all other employment expenses", so 500
    # of either leaves a limit of 2,500.
    worksheet = with_return_deductions(**{deduction: "500"}, musical_instrument_expenses="2500")

    assert worksheet.get(T777_MUSICAL_INSTRUMENT_EXPENSES_MAXIMUM_DEDUCTION).value == D("2500")
    with pytest.raises(InputAboveBoundError, match=BOUND):
        with_return_deductions(**{deduction: "500"}, musical_instrument_expenses="2500.01")


def test_the_musician_income_is_a_part_of_the_employment_income_of_the_return() -> None:
    # The return's employment income is 10,000: all of it as a musician is accepted.
    worksheet = form()

    assert worksheet.get(T777_MUSICIAN_EMPLOYMENT_INCOME_CHECKED).value == D("10000")


def test_a_musician_income_of_one_cent_above_the_employment_income_is_refused() -> None:
    with pytest.raises(InputAboveBoundError, match="t777_work_space_employment_income"):
        form(musician_employment_income="10000.01")


def test_the_other_employment_income_of_line_10400_counts_in_the_whole() -> None:
    # Line 51 of the line 16 chart reads T1 lines 10100 and 10400 as the employment income.
    artifacts = starting(
        "6000",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        other_employment_income="4000",
        t777_amounts={**MUSICIAN},
    )
    (worksheet,) = service().compute(CA_ON, 2025, *artifacts)["ca/t777"]

    assert worksheet.get(T777_MUSICIAN_EMPLOYMENT_INCOME_CHECKED).value == D("10000")
