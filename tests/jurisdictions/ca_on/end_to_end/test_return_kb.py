"""CA-ON 2025 end to end: return KB, Form T1032 line 33 and Note 1 (the receiving spouse was under
65, the transferring spouse was 65 or older and received RRIF, RRSP or other annuity payments, money
purchase RPP or SPP payments, PRPP payments, advanced life deferred annuity payments or eligible
veterans benefits).

The worked return `returns/2025_return_kb.yaml` is checked by `test_worked_returns.py`. This module
computes line 33 on its own, from the starting figures of the return, for each way the printed
instructions go: line 33 is line 30 unless all the conditions above it apply; then Note 1 subtracts
the payments from line 1 (not when they were received on a death), and a result of $4,000 or more
leaves line 33 as line 30 while a smaller one recalculates lines 18 to 31 with the result as
line 17.
The form prints no floor for the recalculated line 30, so a recalculation that would take line 33
below 0 is refused, not capped.
"""

from __future__ import annotations

from typing import Any

import pytest

from tax_calculator.domain.errors import CapabilityContractError, InputAboveBoundError
from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.catalog import (
    PENSION_INCOME_CREDIT,
    T1032_LINE_22_CHECKED,
    T1032_LINE_30,
    T1032_LINE_33,
    T1032_LINE_34,
    T1032_LINE_31400_RECEIVING,
    T1032_NOTE_1_APPLIES,
    T1032_NOTE_1_LINE_29,
    T1032_NOTE_1_LINE_30,
    T1032_NOTE_1_RECALCULATION,
    T1032_NOTE_1_RESULT,
)
from tests.jurisdictions.ca_on.end_to_end.support import CA_ON, D, service, starting

FORM = "ca/t1032"
RETURN = "ca-on/return"

# The receiving spouse's return of KB: the transferring spouse's line 1 is 6,000.00 (RRIF payments
# of 3,000.00 among them), its RCA life annuity (line 4) 2,000.00, so line 8 is 2,000.00, line 17
# is 8,000.00 and line 21 4,000.00; 1,500.00 is elected on line 11600. Without Note 1 line 30 is
# 1,500.00 - (2,000.00 / 8,000.00) x 1,500.00 = 1,125.00.
KB: dict[str, Any] = {
    "eligible_pension": "6000",
    "rca_box_17": "2000",
    "rca_payments_qualify": 1,
    "receiving_under_65": 1,
    "transferring_65": 1,
    "payments": "3000",
    "tax_on_pension": "1200",
}


def run(
    *,
    eligible_pension: str,
    rca_box_17: str = "0",
    rca_payments_qualify: int = 0,
    receiving_pension: str = "0",
    elected_amount: str = "1500",
    receiving_under_65: int = 0,
    transferring_65: int = 0,
    payments: str = "0",
    payments_due_to_death: str = "0",
    veterans_box_128: str = "0",
    tax_on_pension: str = "0",
) -> dict[str, tuple[Worksheet, ...]]:
    """Every form's worksheets of the receiving spouse's return with the starting figures of the
    form and of line 33 given. Line 32 is the return's own pension (`receiving_pension`)."""
    artifacts = starting(
        "0",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        other_income=rca_box_17,
        other_pensions_and_superannuation=receiving_pension,
        t1032_line_22=elected_amount,
        spouse_or_common_law_partner_on_december_31=1,
        t1032_eligible_pension_income=eligible_pension,
        t1032_t4a_rca_box_17=rca_box_17,
        t1032_rca_payments_qualify=rca_payments_qualify,
        t1032_filer_is_transferring_spouse=0,
        t1032_receiving_spouse_pension_amount=receiving_pension,
        t1032_income_tax_deducted_on_pension=tax_on_pension,
        t1032_receiving_spouse_under_65=receiving_under_65,
        t1032_transferring_spouse_65_or_older=transferring_65,
        t1032_note_1_payments=payments,
        t1032_note_1_payments_due_to_death=payments_due_to_death,
        t1032_t4a_box_128=veterans_box_128,
    )
    return service().compute(CA_ON, 2025, *artifacts)


def form(**overrides: Any) -> Worksheet:
    (worksheet,) = run(**{**KB, **overrides})[FORM]
    return worksheet


def return_worksheet(**overrides: Any) -> Worksheet:
    (worksheet,) = run(**{**KB, **overrides})[RETURN]
    return worksheet


# --- Note 1 applies -------------------------------------------------------------------------------


def test_the_worked_return_follows_note_1_and_recalculates_lines_17_to_30() -> None:
    found = form()

    assert found.get(T1032_LINE_30).value == D("1125.00")
    assert found.get(T1032_NOTE_1_APPLIES).value == 1
    assert found.get(T1032_NOTE_1_RESULT).value == D("3000.00")
    assert found.get(T1032_NOTE_1_RECALCULATION).value == 1
    assert found.get(T1032_NOTE_1_LINE_29).value == D("1000.00")
    assert found.get(T1032_NOTE_1_LINE_30).value == D("500.00")
    assert found.get(T1032_LINE_33).value == D("500.00")
    assert found.get(T1032_LINE_34).value == D("500.00")
    assert found.get(T1032_LINE_31400_RECEIVING).value == D("500.00")


def test_the_return_takes_line_33_through_line_34_as_its_pension_income_amount() -> None:
    assert return_worksheet().get(PENSION_INCOME_CREDIT).value == D("500.00")


def test_line_33_is_the_lesser_of_line_22_and_the_recalculated_line_30() -> None:
    # Without the RCA annuity the recalculated line 30 is line 22 (line 29 is 0): the lesser of two
    # equal figures. The result is 2,500.00.
    found = form(
        rca_box_17="0",
        rca_payments_qualify=0,
        eligible_pension="3500",
        payments="1000",
        elected_amount="1250",
    )

    assert found.get(T1032_NOTE_1_RESULT).value == D("2500.00")
    assert found.get(T1032_NOTE_1_LINE_30).value == found.get(T1032_LINE_22_CHECKED).value
    assert found.get(T1032_LINE_33).value == D("1250.00")


def test_an_elected_amount_above_half_the_result_is_kept_as_line_22() -> None:
    # Half the result is 1,500.00; the election of 2,000.00 is within the original line 21
    # (4,000.00) and Note 1 asks for "the amount from line 22", so it is not checked again.
    found = form(elected_amount="2000")

    assert found.get(T1032_NOTE_1_LINE_29).value == D("1333.33")
    assert found.get(T1032_NOTE_1_LINE_30).value == D("666.67")
    assert found.get(T1032_LINE_33).value == D("666.67")


def test_a_result_of_exactly_4000_leaves_line_33_as_line_30() -> None:
    # 6,000.00 - 2,000.00 = 4,000.00: "$4,000 or more".
    found = form(payments="2000")

    assert found.get(T1032_NOTE_1_RESULT).value == D("4000.00")
    assert found.get(T1032_NOTE_1_RECALCULATION).value == 0
    assert found.get(T1032_LINE_33).value == found.get(T1032_LINE_30).value


def test_a_result_of_one_cent_under_4000_recalculates_line_33() -> None:
    found = form(eligible_pension="6000.01", payments="2000.02")

    assert found.get(T1032_NOTE_1_RESULT).value == D("3999.99")
    assert found.get(T1032_NOTE_1_RECALCULATION).value == 1
    assert found.get(T1032_LINE_33).value != found.get(T1032_LINE_30).value


def test_a_result_of_4000_or_more_leaves_line_33_as_line_30() -> None:
    found = form(payments="500")

    assert found.get(T1032_NOTE_1_RESULT).value == D("5500.00")
    assert found.get(T1032_LINE_33).value == found.get(T1032_LINE_30).value == D("1125.00")


def test_payments_received_on_a_death_are_not_removed_from_line_1() -> None:
    # All the 3,000.00 of payments came from a death: the result is line 1, 6,000.00, which is
    # $4,000 or more: line 33 is line 30.
    found = form(payments_due_to_death="3000")

    assert found.get(T1032_NOTE_1_APPLIES).value == 1
    assert found.get(T1032_NOTE_1_RESULT).value == D("6000.00")
    assert found.get(T1032_LINE_33).value == D("1125.00")


def test_only_the_part_received_on_a_death_is_left_in_line_1() -> None:
    # 1,000.00 of the 3,000.00 came from a death: 2,000.00 is removed from line 1 (6,000.00), the
    # result is 4,000.00, which is $4,000 or more: line 33 is line 30. Had all 3,000.00 been removed
    # the result 3,000.00 would recalculate.
    found = form(payments_due_to_death="1000")

    assert found.get(T1032_NOTE_1_RESULT).value == D("4000.00")
    assert found.get(T1032_NOTE_1_RECALCULATION).value == 0
    assert found.get(T1032_LINE_33).value == D("1125.00")


def test_eligible_veterans_benefits_are_the_box_128_amount_of_line_2() -> None:
    # 1,000.00 of a) to d) plus 2,000.00 of box 128 (entered once, for line 2): 3,000.00 is
    # removed from line 1 (6,000.00), the result is 3,000.00, as when 3,000.00 is entered for a) to
    # d).
    found = form(payments="1000", veterans_box_128="2000")

    assert found.get(T1032_NOTE_1_APPLIES).value == 1
    assert found.get(T1032_NOTE_1_RESULT).value == D("3000.00")


def test_box_128_alone_makes_note_1_apply() -> None:
    found = form(payments="0", veterans_box_128="500")

    assert found.get(T1032_NOTE_1_APPLIES).value == 1
    assert found.get(T1032_NOTE_1_RESULT).value == D("5500.00")


# --- Note 1 does not apply: line 33 is line 30 ----------------------------------------------------


@pytest.mark.parametrize(
    "overrides",
    [
        # Line 32 is $2,000 or more: not "less than $2,000".
        {"receiving_pension": "2000"},
        # The receiving spouse was 65 or older.
        {"receiving_under_65": 0},
        # The transferring spouse was under 65.
        {"transferring_65": 0},
        # None of the amounts a) to e) was received.
        {"payments": "0"},
    ],
)
def test_line_33_is_line_30_when_any_condition_above_it_fails(overrides: dict[str, Any]) -> None:
    found = form(**overrides)

    assert found.get(T1032_NOTE_1_APPLIES).value == 0
    assert found.get(T1032_LINE_33).value == found.get(T1032_LINE_30).value


def test_a_small_result_is_not_read_when_note_1_does_not_apply() -> None:
    # Result 1,000.00 is below line 8 (2,000.00), but the transferring spouse is under 65, so
    # nothing is recalculated and line 33 is line 30.
    found = form(payments="5000", transferring_65=0)

    assert found.get(T1032_NOTE_1_APPLIES).value == 0
    assert found.get(T1032_NOTE_1_RECALCULATION).value == 0
    assert found.get(T1032_LINE_33).value == found.get(T1032_LINE_30).value


def test_a_line_32_of_one_cent_under_2000_is_less_than_2000() -> None:
    found = form(receiving_pension="1999.99")

    assert found.get(T1032_NOTE_1_APPLIES).value == 1


def test_line_34_adds_line_33_to_line_32() -> None:
    found = form(receiving_pension="500")

    assert found.get(T1032_LINE_33).value == D("500.00")
    assert found.get(T1032_LINE_34).value == D("1000.00")


# --- refusals ------------------------------------------------------------------------------------


def test_amounts_above_line_1_give_a_negative_credit_which_is_refused() -> None:
    # The form prints no bound on the amounts against line 1: the result is -0.01, line 17 of the
    # recalculation, and line 31400 of the transferring spouse, a credit amount, comes out below 0,
    # for which the form prints no floor.
    with pytest.raises(CapabilityContractError):
        run(**{**KB, "payments": "6000.01"})


@pytest.mark.parametrize("answer", ["receiving_under_65", "transferring_65"])
def test_an_answer_of_2_is_refused(answer: str) -> None:
    with pytest.raises(InputAboveBoundError):
        run(**{**KB, answer: 2})


def test_the_part_received_on_a_death_above_the_payments_is_refused_not_capped() -> None:
    with pytest.raises(InputAboveBoundError):
        run(**{**KB, "payments_due_to_death": "3000.01"})


def test_a_recalculation_that_takes_line_34_below_0_is_refused_not_floored() -> None:
    # Line 1 is 3,000.00 less 2,500.00 of payments: the result 500.00 is line 17, below line 8
    # (2,000.00), so line 29 is 250.00 x 2,000.00 / 500.00 = 1,000.00, more than line 22 (250.00).
    with pytest.raises(CapabilityContractError):
        run(
            **{
                **KB,
                "eligible_pension": "3000",
                "payments": "2500",
                "elected_amount": "250",
            }
        )
