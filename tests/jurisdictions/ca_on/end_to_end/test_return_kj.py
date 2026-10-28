"""CA-ON 2025 end to end: return KJ, Form T1032 Note 1 with eligible veterans benefits (item e) read
from the box 128 amount of line 2, and only the part of the payments received as a consequence of a
death left in line 1.

The worked return `returns/2025_return_kj.yaml` is checked by `test_worked_returns.py`. This module
computes the same receiving spouse's return from its starting figures: line 1 is 8,000.00 with
2,000.00 of box 128, 3,000.00 of RRIF payments (500.00 of them received on a death) and 1,000.00 of
RCA life annuity; the result of Note 1 is 8,000.00 - (3,000.00 + 2,000.00 - 500.00) = 3,500.00, less
than $4,000, so lines 18 to 31 are recalculated.
"""

from __future__ import annotations

from typing import Any

import pytest

from tax_calculator.domain.errors import InputAboveBoundError
from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.catalog import (
    PENSION_INCOME_CREDIT,
    T1032_LINE_33,
    T1032_LINE_34,
    T1032_NOTE_1_APPLIES,
    T1032_NOTE_1_LINE_29,
    T1032_NOTE_1_LINE_30,
    T1032_NOTE_1_PAYMENTS_TO_REMOVE,
    T1032_NOTE_1_RESULT,
)
from tests.jurisdictions.ca_on.end_to_end.support import CA_ON, D, service, starting

FORM = "ca/t1032"
RETURN = "ca-on/return"

# The receiving spouse's return of KJ: the transferring spouse's line 1 is 8,000.00 (box 128 of
# 2,000.00 and RRIF payments of 3,000.00 among them, 500.00 of the RRIF payments received on a
# death), its RCA life annuity (line 4) 1,000.00; 2,000.00 is elected on line 11600. Note 1 removes
# 2,000.00 + 3,000.00 - 500.00 = 4,500.00 from line 1: the result 3,500.00 is line 17 of the
# recalculation, line 29 is 2,000.00 x 1,000.00 / 3,500.00 = 571.43 and line 33 is 1,428.57.
KJ: dict[str, Any] = {
    "eligible_pension": "8000",
    "veterans_box_128": "2000",
    "rca_box_17": "1000",
    "rca_payments_qualify": 1,
    "receiving_under_65": 1,
    "transferring_65": 1,
    "payments": "3000",
    "payments_due_to_death": "500",
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
    (worksheet,) = run(**{**KJ, **overrides})[FORM]
    return worksheet


def return_worksheet(**overrides: Any) -> Worksheet:
    (worksheet,) = run(**{**KJ, **overrides})[RETURN]
    return worksheet


# --- Note 1 applies -------------------------------------------------------------------------------


def test_note_1_removes_box_128_and_the_payments_not_received_on_a_death() -> None:
    found = form()

    assert found.get(T1032_NOTE_1_APPLIES).value == 1
    assert found.get(T1032_NOTE_1_PAYMENTS_TO_REMOVE).value == D("4500.00")
    assert found.get(T1032_NOTE_1_RESULT).value == D("3500.00")
    assert found.get(T1032_NOTE_1_LINE_29).value == D("571.43")
    assert found.get(T1032_NOTE_1_LINE_30).value == D("1428.57")
    assert found.get(T1032_LINE_33).value == D("1428.57")
    assert found.get(T1032_LINE_34).value == D("1428.57")


def test_the_return_takes_line_33_through_line_34_as_its_pension_income_amount() -> None:
    assert return_worksheet().get(PENSION_INCOME_CREDIT).value == D("1428.57")


def test_box_128_is_not_entered_a_second_time_with_the_payments() -> None:
    # The same 5,000.00 entered for a) to d) alone, with no box 128, removes the same amount.
    found = form(veterans_box_128="0", payments="5000")

    assert found.get(T1032_NOTE_1_RESULT).value == D("3500.00")


# --- refusals ------------------------------------------------------------------------------------


def test_the_part_received_on_a_death_above_the_payments_is_refused_not_capped() -> None:
    with pytest.raises(InputAboveBoundError):
        run(**{**KJ, "payments_due_to_death": "5000.01"})
