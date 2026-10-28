"""CA-ON 2025 end to end: return LS, Form T1032 Note 1 when the amounts a) to e) are more than
line 1 and the result of Note 1 is a small or negative figure.

The worked return `returns/2025_return_ls.yaml` is checked by `test_worked_returns.py`. This module
computes the same receiving spouse's return from its starting figures: line 1 is 8,000.00 with
2,000.00 of box 128, 7,000.00 of payments a) to d) (1,500.00 of them received on a death) and 200.00
of RCA life annuity; the result of Note 1 is 8,000.00 - (7,000.00 + 2,000.00 - 1,500.00) = 500.00.
The form prints no limit on the amounts against line 1 and no floor for the result, so neither is
refused; a line 8 over a line 17 of 0 (a division by 0) and a line 34 below 0 are.
"""

from __future__ import annotations

from typing import Any

import pytest

from tax_calculator.domain.errors import CapabilityContractError, InputAboveBoundError
from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.catalog import (
    PENSION_INCOME_CREDIT,
    T1032_LINE_33,
    T1032_LINE_34,
    T1032_NOTE_1_LINE_17,
    T1032_NOTE_1_LINE_29,
    T1032_NOTE_1_LINE_30,
    T1032_NOTE_1_PAYMENTS_TO_REMOVE,
    T1032_NOTE_1_RESULT,
)
from tests.jurisdictions.ca_on.end_to_end.support import CA_ON, D, service, starting

FORM = "ca/t1032"
RETURN = "ca-on/return"

# The receiving spouse's return of LS: line 1 is 8,000.00 (box 128 of 2,000.00 and payments a) to d)
# of 7,000.00 among them, 1,500.00 of the payments received on a death), its RCA life annuity
# (line 4) 200.00; 2,000.00 is elected on line 11600. Note 1 removes 2,000.00 + 7,000.00 - 1,500.00
# = 7,500.00 from line 1 (more than line 1 is received, which the form does not bound): the result
# 500.00 is line 17 of the recalculation, line 29 is 2,000.00 x 200.00 / 500.00 = 800.00 and line
# 33 is 1,200.00.
LS: dict[str, Any] = {
    "eligible_pension": "8000",
    "veterans_box_128": "2000",
    "rca_box_17": "200",
    "rca_payments_qualify": 1,
    "receiving_under_65": 1,
    "transferring_65": 1,
    "payments": "7000",
    "payments_due_to_death": "1500",
    "tax_on_pension": "800",
}


def run(
    *,
    eligible_pension: str,
    veterans_box_128: str = "0",
    rca_box_17: str = "0",
    rca_payments_qualify: int = 0,
    receiving_pension: str = "0",
    elected_amount: str = "2000",
    receiving_under_65: int = 0,
    transferring_65: int = 0,
    payments: str = "0",
    payments_due_to_death: str = "0",
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
        t1032_t4a_box_128=veterans_box_128,
        t1032_t4a_rca_box_17=rca_box_17,
        t1032_rca_payments_qualify=rca_payments_qualify,
        t1032_filer_is_transferring_spouse=0,
        t1032_receiving_spouse_pension_amount=receiving_pension,
        t1032_income_tax_deducted_on_pension=tax_on_pension,
        t1032_receiving_spouse_under_65=receiving_under_65,
        t1032_transferring_spouse_65_or_older=transferring_65,
        t1032_note_1_payments=payments,
        t1032_note_1_payments_due_to_death=payments_due_to_death,
    )
    return service().compute(CA_ON, 2025, *artifacts)


def form(**overrides: Any) -> Worksheet:
    (worksheet,) = run(**{**LS, **overrides})[FORM]
    return worksheet


def return_worksheet(**overrides: Any) -> Worksheet:
    (worksheet,) = run(**{**LS, **overrides})[RETURN]
    return worksheet


# --- Note 1 applies -------------------------------------------------------------------------------


def test_payments_above_line_1_are_subtracted_as_printed_when_the_result_is_not_below_0() -> None:
    found = form()

    assert found.get(T1032_NOTE_1_PAYMENTS_TO_REMOVE).value == D("7500.00")
    assert found.get(T1032_NOTE_1_RESULT).value == D("500.00")
    assert found.get(T1032_NOTE_1_LINE_17).value == D("500.00")
    assert found.get(T1032_NOTE_1_LINE_29).value == D("800.00")
    assert found.get(T1032_NOTE_1_LINE_30).value == D("1200.00")
    assert found.get(T1032_LINE_33).value == D("1200.00")
    assert found.get(T1032_LINE_34).value == D("1200.00")


def test_the_return_takes_line_34_as_its_pension_income_amount() -> None:
    assert return_worksheet().get(PENSION_INCOME_CREDIT).value == D("1200.00")


def test_a_result_below_0_is_printed_arithmetic_not_a_refusal() -> None:
    # 9,000.00 with nothing received on a death is 1,000.00 above line 1 of 8,000.00: the result is
    # -1,000.00, line 17 -1,000.00, line 29 = 2,000.00 x 200.00 / -1,000.00 = -400.00, line 30 =
    # 2,400.00 and line 33 the lesser of 2,000.00 and 2,400.00.
    found = form(payments_due_to_death="0")

    assert found.get(T1032_NOTE_1_RESULT).value == D("-1000.00")
    assert found.get(T1032_NOTE_1_LINE_29).value == D("-400.00")
    assert found.get(T1032_NOTE_1_LINE_30).value == D("2400.00")
    assert found.get(T1032_LINE_33).value == D("2000.00")


def test_a_line_17_of_0_with_no_line_8_leaves_line_33_at_line_22() -> None:
    found = form(rca_box_17="0", rca_payments_qualify=0, payments="6000", payments_due_to_death="0")

    assert found.get(T1032_NOTE_1_RESULT).value == D("0.00")
    assert found.get(T1032_NOTE_1_LINE_29).value == D("0.00")
    assert found.get(T1032_LINE_33).value == D("2000.00")


# --- refusals ------------------------------------------------------------------------------------


def test_a_line_8_with_a_line_17_of_0_is_refused_not_replaced_by_0() -> None:
    # Line 25 of 200.00 over line 26 of 0.00: the form prints no answer.
    with pytest.raises(InputAboveBoundError):
        run(**{**LS, "payments": "6000", "payments_due_to_death": "0"})


def test_a_line_34_below_0_is_refused_where_it_would_reach_a_credit() -> None:
    # Result 100.00: line 29 = 2,000.00 x 200.00 / 100.00 = 4,000.00, line 30 = -2,000.00, line 33
    # -2,000.00 and line 34 -2,000.00, which the form prints no floor for and is the credit amount.
    with pytest.raises(CapabilityContractError):
        run(**{**LS, "payments": "5900", "payments_due_to_death": "0"})


def test_the_part_received_on_a_death_above_the_payments_is_refused_not_capped() -> None:
    with pytest.raises(InputAboveBoundError):
        run(**{**LS, "payments_due_to_death": "9000.01"})
