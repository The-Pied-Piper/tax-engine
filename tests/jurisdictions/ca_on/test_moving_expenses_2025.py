"""The 2025 moving expenses deduction (Form T1-M, one copy for each move; T1 line 21900), checked
against CRA's form and the two datasets it prints.

2025 Form T1-M (Moving Expenses Deduction), Part 2 "If the amount on line 3 is less than 40
kilometres, you cannot deduct your moving expenses." and page 1 "To qualify, your new home must be
at least 40 kilometres closer (by the shortest public route) to your new work location or school."
(the 40 kilometres of the `ca/moving_distance_threshold` dataset, a distance taken as printed; the
form's gate is "at least", so a line 3 of exactly 40 claims). Part 4 "Costs to maintain your old
home when vacant (maximum $5,000)" (line 14), the `ca/moving_old_home_maintenance_cap` dataset,
taken as printed. Part 4 "Add lines 4, 8, 11, 15, 20 and 23." (line 24), "Line 24 minus line 25 (if
negative, enter "0")" (line 26), "Enter whichever is less: amount from line 27 or line 28." and
"Enter this amount on line 21900 of your return." (line 29), "Line 27 minus line 28 (if negative,
enter "0")" (line 30). T1-2025 Ontario edition (form 5006-R), "Line 44 and line 21900: Moving
expenses (complete Form T1-M)" and "Line 53 and line 23300: Add lines 35 to 52."

Both printed figures are dollars-and-cents boxes once they are amounts (line 14 and line 29), so the
amounts round half-up to the cent through the dataset's rule, the owner's decision, as the form
states no rounding rule; the core sums and differences stay exact.

The lines are tested here on the registered kinds, one rule at a time: the worked returns and their
end-to-end tests are in `end_to_end/test_return_dk.py` and `returns/2025_return_dk.yaml` (and the
Ontario return BG, which carries one move for the alternative minimum tax).

Line 28 "Net eligible income" is taken from the income lines of the return: the employment and other
employment income (lines 10100 and 10400), the taxable scholarships and the self-employment nets
(lines 13500 to 14300). The printed words say the amount is "included on" those lines, so line 28 is
at most their total, checked per move: an amount above it is refused, not capped (`core/at_most`),
and the checked amount is the one lines 29 and 30 read. The printed form and guide print no other
limit on line 28 (`docs/cra-forms-2025/t1-m-25e.pdf` and `5000-g-25e.txt`).
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any

import pytest

import tax_engine.registrations
from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.errors import InputAboveBoundError
from tax_engine.domain.parameters.amount import AMOUNT, Amount
from tax_engine.domain.parameters.credit import CREDIT, Credit
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog import (
    AMT_DEDUCTIONS_TOTAL,
    DEDUCTIONS_FROM_TOTAL_INCOME,
    MOVING_BUSINESS_INCOME,
    MOVING_DISTANCE_DIFFERENCE,
    MOVING_ELIGIBLE_INCOME_LINES,
    MOVING_EXPENSES_CLAIM,
    MOVING_EXPENSES_DEDUCTION,
    MOVING_LEASE_AND_INCIDENTAL_SUBTOTAL,
    MOVING_NET_ELIGIBLE_INCOME_CHECKED,
    MOVING_NET_EXPENSES,
    MOVING_OLD_HOME_MAINTENANCE_CHECKED,
    MOVING_UNUSED_EXPENSES,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, run

SOURCE = YamlParameterSource(tax_engine.registrations.JURISDICTIONS.roots())
DISTANCE_THRESHOLD = "ca/moving_distance_threshold"
MAINTENANCE_CAP = "ca/moving_old_home_maintenance_cap"

# The return's employment income of the worked moves: 40,000, so each move's line 28 of 40,000 is at
# the bound (`ca/moving_eligible_income_lines`) and is accepted.
EMPLOYMENT_INCOME = "40000"

# One move of the worked example: distances of 100 and 10 kilometres (line 3 is 90), transportation
# and storage of 2,000 (line 4), travel expenses of 500 (line 5), nothing reimbursed, and net
# eligible income of 40,000 (line 28): line 24 is 2,500, line 26 is 2,500, line 29 is 2,500.00 and
# line 30 is 0.00.
WORKED_EXAMPLE = {
    "old_home_distance": "100",
    "new_home_distance": "10",
    "transportation_and_storage": "2000",
    "travel_expenses": "500",
    "net_eligible_income": "40000",
}

# A T2125 statement of gross sales 50,000 and office expenses 20,000 on business line 1: a net of
# 30,000 that counts in the bound of line 28.
BUSINESS_NET_30000 = {
    "business": {"gross_sales": "50000", "office_expenses": "20000"},
    "business_income_line": 1,
}


def form_worksheets(*moves: Mapping[str, Any]) -> tuple[Worksheet, ...]:
    """The worksheet of each copy of Form T1-M for `moves`, in order (none for no moves)."""
    return run(EMPLOYMENT_INCOME, (), "0", "0", "0", "0", "0", moving_moves=moves)["ca/t1_m"]


def return_worksheet(*moves: Mapping[str, Any]) -> Worksheet:
    """The return's worksheet for `moves`, with no other entry of its own."""
    return run(EMPLOYMENT_INCOME, (), "0", "0", "0", "0", "0", moving_moves=moves)["ca-on/return"][
        0
    ]


def income_run(
    *moves: Mapping[str, Any], employment: str = EMPLOYMENT_INCOME, **income: Any
) -> tuple[Worksheet, ...]:
    """The copies of Form T1-M for `moves` with the return's other income lines given by `income`
    (business statements, other employment income, taxable scholarships)."""
    return run(employment, (), "0", "0", "0", "0", "0", moving_moves=moves, **income)["ca/t1_m"]


def move(**overrides: str) -> dict[str, str]:
    """The worked example's move, with `overrides` changing or adding its inputs."""
    return {**WORKED_EXAMPLE, **overrides}


# --- the datasets -------------------------------------------------------------------------------


def test_2025_distance_threshold_is_40_kilometres() -> None:
    data = SOURCE.get(DISTANCE_THRESHOLD, 2025, AMOUNT)

    assert data.values == Amount(D("40"))
    # Line 29 is a dollars-and-cents box: half-up to the cent, the gated amount being line 29.
    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_old_home_maintenance_cap_is_5000() -> None:
    data = SOURCE.get(MAINTENANCE_CAP, 2025, CREDIT)

    assert data.values == Credit(D("5000"))
    # Line 14 is a dollars-and-cents box: half-up to the cent.
    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


# --- the line 3 gate ----------------------------------------------------------------------------


def test_the_worked_example_gives_line_26_of_2500_line_29_of_2500_and_line_30_of_0() -> None:
    (worksheet,) = form_worksheets(WORKED_EXAMPLE)

    assert worksheet.get(MOVING_DISTANCE_DIFFERENCE).value == D("90")
    assert worksheet.get(MOVING_NET_EXPENSES).value == D("2500.00")
    assert worksheet.get(MOVING_EXPENSES_CLAIM).value == D("2500.00")
    assert worksheet.get(MOVING_UNUSED_EXPENSES).value == D("0.00")


def test_a_line_3_of_35_claims_nothing_on_line_29() -> None:
    # Old home 75 kilometres from the new work location, new home 40: line 3 is 35, under 40.
    (worksheet,) = form_worksheets(move(old_home_distance="75", new_home_distance="40"))

    assert worksheet.get(MOVING_DISTANCE_DIFFERENCE).value == D("35")
    assert worksheet.get(MOVING_EXPENSES_CLAIM).value == D("0")


def test_a_line_3_of_35_carries_nothing_on_line_30() -> None:
    # Line 24 is 2,500 and line 28 is 0 (no net eligible income): without the 40 kilometre test
    # line 27 minus line 28 would carry 2,500.00; the form is not completed under 40 kilometres.
    (worksheet,) = form_worksheets(
        move(old_home_distance="75", new_home_distance="40", net_eligible_income="0")
    )

    assert worksheet.get(MOVING_DISTANCE_DIFFERENCE).value == D("35")
    assert worksheet.get(MOVING_EXPENSES_CLAIM).value == D("0")
    assert worksheet.get(MOVING_UNUSED_EXPENSES).value == D("0")


def test_a_line_3_of_exactly_40_carries_line_27_minus_line_28_on_line_30() -> None:
    (worksheet,) = form_worksheets(
        move(old_home_distance="100", new_home_distance="60", net_eligible_income="0")
    )

    assert worksheet.get(MOVING_UNUSED_EXPENSES).value == D("2500.00")


def test_a_line_3_of_exactly_40_is_at_least_40_and_claims() -> None:
    (worksheet,) = form_worksheets(move(old_home_distance="100", new_home_distance="60"))

    assert worksheet.get(MOVING_DISTANCE_DIFFERENCE).value == D("40")
    assert worksheet.get(MOVING_EXPENSES_CLAIM).value == D("2500.00")


def test_a_negative_line_3_claims_nothing() -> None:
    # Line 3 is "Line 1 minus line 2" with no floor; a negative difference is under 40.
    (worksheet,) = form_worksheets(move(old_home_distance="10", new_home_distance="50"))

    assert worksheet.get(MOVING_DISTANCE_DIFFERENCE).value == D("-40")
    assert worksheet.get(MOVING_EXPENSES_CLAIM).value == D("0")


# --- lines 24 to 30 ----------------------------------------------------------------------------


def test_6000_of_expenses_against_4000_of_income_gives_4000_and_carries_2000() -> None:
    # Line 26 is 6,000 and line 27 too; line 29 is the lesser of 6,000 and 4,000; line 30 is the
    # rest, 2,000, which is carried forward.
    (worksheet,) = form_worksheets(
        move(transportation_and_storage="6000", travel_expenses="0", net_eligible_income="4000")
    )

    assert worksheet.get(MOVING_EXPENSES_CLAIM).value == D("4000.00")
    assert worksheet.get(MOVING_UNUSED_EXPENSES).value == D("2000.00")


def test_a_reimbursement_above_line_24_gives_line_26_of_0_and_claims_nothing() -> None:
    # Line 24 is 2,500; line 25 is 3,000; line 24 minus line 25 is below zero, so line 26 is 0.
    (worksheet,) = form_worksheets(move(reimbursement="3000"))

    assert worksheet.get(MOVING_NET_EXPENSES).value == D("0")
    assert worksheet.get(MOVING_EXPENSES_CLAIM).value == D("0")
    assert worksheet.get(MOVING_UNUSED_EXPENSES).value == D("0")


def test_line_28_caps_line_29_and_the_rest_is_carried_forward() -> None:
    (worksheet,) = form_worksheets(move(net_eligible_income="1000"))

    assert worksheet.get(MOVING_EXPENSES_CLAIM).value == D("1000.00")
    assert worksheet.get(MOVING_UNUSED_EXPENSES).value == D("1500.00")


def test_line_14_of_5000_is_taken_as_entered() -> None:
    # Costs to maintain the old home of 5,000, the maximum: line 15 is 5,000 and line 26 and line 29
    # are 5,000 too (line 28 of 40,000 does not cap them).
    (worksheet,) = form_worksheets(
        move(old_home_maintenance="5000", transportation_and_storage="0", travel_expenses="0")
    )

    assert worksheet.get(MOVING_OLD_HOME_MAINTENANCE_CHECKED).value == D("5000")
    assert worksheet.get(MOVING_LEASE_AND_INCIDENTAL_SUBTOTAL).value == D("5000")
    assert worksheet.get(MOVING_EXPENSES_CLAIM).value == D("5000.00")


def test_line_14_one_cent_above_5000_is_refused_not_capped() -> None:
    with pytest.raises(InputAboveBoundError) as raised:
        form_worksheets(move(old_home_maintenance="5000.01"))

    assert str(raised.value) == (
        "ca/t1_m, instance 1: ca/moving_old_home_maintenance 5000.01 is above "
        "ca/moving_old_home_maintenance_cap 5000.00"
    )


# --- the moves and T1 line 21900 ----------------------------------------------------------------


def test_each_move_has_its_own_copy_of_the_form() -> None:
    worksheets = form_worksheets(
        WORKED_EXAMPLE, move(new_home_distance="50", old_home_distance="200")
    )

    assert len(worksheets) == 2


def test_two_moves_of_2500_and_1000_give_line_21900_of_3500() -> None:
    # The second move: 200 and 50 kilometres (line 3 is 150), transportation and storage of 1,000,
    # and net eligible income of 40,000, so its line 29 is 1,000.00.
    second = {
        "old_home_distance": "200",
        "new_home_distance": "50",
        "transportation_and_storage": "1000",
        "net_eligible_income": "40000",
    }
    worksheet = return_worksheet(WORKED_EXAMPLE, second)

    assert worksheet.get(MOVING_EXPENSES_DEDUCTION).value == D("3500.00")


def test_no_moves_give_line_21900_of_0() -> None:
    assert form_worksheets() == ()
    assert return_worksheet().get(MOVING_EXPENSES_DEDUCTION).value == D("0")


def test_line_23300_includes_line_21900() -> None:
    with_move = return_worksheet(WORKED_EXAMPLE).get(DEDUCTIONS_FROM_TOTAL_INCOME).value
    without = return_worksheet().get(DEDUCTIONS_FROM_TOTAL_INCOME).value

    assert with_move - without == D("2500.00")


def test_the_alternative_minimum_tax_reads_the_computed_line_21900() -> None:
    # Form T691 Part 1 line 56 "Moving expenses deduction from line 21900": the same 2,500.00 of
    # line 21900 is in the alternative minimum tax's deductions, with no caller's stand-in.
    with_move = return_worksheet(WORKED_EXAMPLE).get(AMT_DEDUCTIONS_TOTAL).value
    without = return_worksheet().get(AMT_DEDUCTIONS_TOTAL).value

    assert with_move - without == D("2500.00")


# --- line 28 is at most the income lines it is taken from --------------------------------------
# Form T1-M Part 4 line 28 "Net eligible income": the amounts on lines 10100 and 10400, the net
# self-employment amounts on lines 13500 to 14300 (a loss counting 0) and the scholarships of a
# student, at most the income they are taken from. The refusal is an input error, not a cap.


def test_line_28_equal_to_the_employment_income_claims_as_before() -> None:
    # Line 28 of 40,000 and employment income of 40,000: at the bound, so the claim is unchanged.
    (worksheet,) = form_worksheets(WORKED_EXAMPLE)

    assert worksheet.get(MOVING_EXPENSES_CLAIM).value == D("2500.00")
    assert worksheet.get(MOVING_UNUSED_EXPENSES).value == D("0.00")


def test_line_28_equal_to_the_employment_income_is_the_checked_amount_read_by_line_29() -> None:
    (worksheet,) = form_worksheets(WORKED_EXAMPLE)

    assert worksheet.get(MOVING_ELIGIBLE_INCOME_LINES).value == D("40000")
    assert worksheet.get(MOVING_NET_ELIGIBLE_INCOME_CHECKED).value == D("40000")
    rendered = EnglishTraceRenderer().render_all(worksheet.trace)
    assert (
        "moving_net_eligible_income_checked: moving_net_eligible_income 40000, "
        "at most moving_eligible_income_lines 40000"
    ) in rendered


def test_line_28_one_cent_above_the_employment_income_is_refused_not_capped() -> None:
    # 40,000.01 against 40,000.00 of income lines is an input error: it is not capped to 40,000.00.
    with pytest.raises(InputAboveBoundError) as raised:
        form_worksheets(move(net_eligible_income="40000.01"))

    assert str(raised.value) == (
        "ca/t1_m, instance 1: ca/moving_net_eligible_income 40000.01 is above "
        "ca/moving_eligible_income_lines 40000"
    )


def test_line_28_within_the_self_employment_income_passes_and_is_checked() -> None:
    # A business net of 30,000 is the only income: line 28 of 30,000 is at the bound.
    (worksheet,) = income_run(
        move(net_eligible_income="30000"), employment="0", business_statements=(BUSINESS_NET_30000,)
    )

    assert worksheet.get(MOVING_BUSINESS_INCOME).value == D("30000")
    assert worksheet.get(MOVING_NET_ELIGIBLE_INCOME_CHECKED).value == D("30000")
    assert worksheet.get(MOVING_EXPENSES_CLAIM).value == D("2500.00")


def test_line_28_above_the_self_employment_income_is_refused() -> None:
    with pytest.raises(InputAboveBoundError) as raised:
        income_run(
            move(net_eligible_income="30001"),
            employment="0",
            business_statements=(BUSINESS_NET_30000,),
        )

    assert str(raised.value) == (
        "ca/t1_m, instance 1: ca/moving_net_eligible_income 30001 is above "
        "ca/moving_eligible_income_lines 30000"
    )


def test_a_business_loss_counts_0_in_the_bound_and_does_not_reduce_the_employment_income() -> None:
    # A statement with 5,000 of expenses and no sales is a loss of 5,000 on business line 1. It
    # counts 0, so the bound is the employment income of 10,000 and not 5,000.
    loss = {"business": {"office_expenses": "5000"}, "business_income_line": 1}
    (worksheet,) = income_run(
        move(net_eligible_income="10000"), employment="10000", business_statements=(loss,)
    )

    assert worksheet.get(MOVING_BUSINESS_INCOME).value == D("0")
    assert worksheet.get(MOVING_ELIGIBLE_INCOME_LINES).value == D("10000")
    assert worksheet.get(MOVING_NET_ELIGIBLE_INCOME_CHECKED).value == D("10000")


def test_a_business_loss_alone_leaves_a_bound_of_0_so_any_line_28_is_refused() -> None:
    loss = {"business": {"office_expenses": "5000"}, "business_income_line": 1}
    with pytest.raises(InputAboveBoundError) as raised:
        income_run(move(net_eligible_income="1"), employment="0", business_statements=(loss,))

    assert str(raised.value) == (
        "ca/t1_m, instance 1: ca/moving_net_eligible_income 1 is above "
        "ca/moving_eligible_income_lines 0"
    )


@pytest.mark.parametrize(
    ("income", "amount"),
    [("other_employment_income", "5000"), ("taxable_scholarships", "3000")],
)
def test_each_income_line_counts_in_the_bound(income: str, amount: str) -> None:
    # Line 10400 (other employment income) and the taxable scholarships of a student are income
    # lines of the bound too: line 28 of exactly that amount is accepted.
    (worksheet,) = income_run(move(net_eligible_income=amount), employment="0", **{income: amount})

    assert worksheet.get(MOVING_NET_ELIGIBLE_INCOME_CHECKED).value == D(amount)
    with pytest.raises(
        InputAboveBoundError, match=re.escape(f"is above ca/moving_eligible_income_lines {amount}")
    ):
        income_run(move(net_eligible_income=f"{amount}1"), employment="0", **{income: amount})


def test_the_bound_adds_every_income_line_of_the_return() -> None:
    # Employment 10,000 + other employment 5,000 + scholarships 3,000 + a business net of 30,000
    # = 48,000: line 28 of 48,000 is accepted and 48,001 is refused.
    income: dict[str, Any] = {
        "other_employment_income": "5000",
        "taxable_scholarships": "3000",
        "business_statements": (BUSINESS_NET_30000,),
    }
    (worksheet,) = income_run(move(net_eligible_income="48000"), employment="10000", **income)

    assert worksheet.get(MOVING_ELIGIBLE_INCOME_LINES).value == D("48000")
    assert worksheet.get(MOVING_NET_ELIGIBLE_INCOME_CHECKED).value == D("48000")
    with pytest.raises(InputAboveBoundError) as raised:
        income_run(move(net_eligible_income="48001"), employment="10000", **income)

    assert str(raised.value) == (
        "ca/t1_m, instance 1: ca/moving_net_eligible_income 48001 is above "
        "ca/moving_eligible_income_lines 48000"
    )


def test_one_of_two_moves_above_the_bound_refuses_the_return_naming_the_second_move() -> None:
    # Both moves draw on the same 40,000 of income: the first is at the bound, the second is 1 more.
    with pytest.raises(InputAboveBoundError) as raised:
        run(
            EMPLOYMENT_INCOME,
            (),
            "0",
            "0",
            "0",
            "0",
            "0",
            moving_moves=(WORKED_EXAMPLE, move(net_eligible_income="40001")),
        )

    assert str(raised.value) == (
        "ca/t1_m, instance 2: ca/moving_net_eligible_income 40001 is above "
        "ca/moving_eligible_income_lines 40000"
    )
