"""CA-ON 2025 end to end: return KH, Form T1032 line 31 and the transferring spouse's line 31400
when Note 1 recalculates lines 18 to 31 (the receiving spouse was under 65, the transferring spouse
was 65 or older and received RRIF, RRSP or other annuity payments, money purchase RPP or SPP
payments, PRPP payments, advanced life deferred annuity payments or eligible veterans benefits).

The worked return `returns/2025_return_kh.yaml` is checked by `test_worked_returns.py`. This module
computes line 31 and the transferring spouse's line 31400 on their own, from the starting figures
of the return, for each way Note 1 goes: line 31 is line 1 less line 30 unless Note 1 recalculates
lines 18 to 31 (the conditions above line 33 all apply and line 1 less the payments is under
$4,000), and then line 30 is the recalculated one.
"""

from __future__ import annotations

from typing import Any

import pytest

from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog import (
    PENSION_INCOME_CREDIT,
    T1032_LINE_30,
    T1032_LINE_31,
    T1032_LINE_31_AFTER_NOTE_1,
    T1032_LINE_31400_TRANSFERRING,
    T1032_NOTE_1_LINE_30,
    T1032_NOTE_1_LINE_31,
    T1032_NOTE_1_RECALCULATION,
)
from tests.jurisdictions.ca_on.end_to_end.support import CA_ON, D, service, starting

FORM = "ca/t1032"
RETURN = "ca-on/return"

# The transferring spouse's return of KH: line 1 is 3,500.00 (RRIF payments of 300.00 among them),
# the RCA life annuity (line 4) 200.00, so line 8 is 200.00, line 17 is 3,700.00 and line 21
# 1,850.00; 1,600.00 is elected on line 21000. Without Note 1, line 30 is 1,600.00 - (200.00 /
# 3,700.00) x 1,600.00 = 1,513.51 and line 31 is 1,986.49. Every election below is within the
# recalculated line 21 as well as the original one, as the form requires of line 22.
KH: dict[str, Any] = {
    "payments": "300",
    "transferring_65": 1,
    "receiving_under_65": 1,
}


def run(
    *,
    payments: str,
    transferring_65: int,
    receiving_under_65: int,
    payments_due_to_death: str = "0",
    eligible_pension: str = "3500",
    receiving_pension: str = "0",
    elected_amount: str = "1600",
) -> dict[str, tuple[Worksheet, ...]]:
    """Every form's worksheets of the transferring spouse's return with the starting figures of
    the form and of line 33 given. Line 32 is `receiving_pension`."""
    artifacts = starting(
        "0",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        other_income="200",
        other_pensions_and_superannuation=eligible_pension,
        t1032_line_22=elected_amount,
        spouse_or_common_law_partner_on_december_31=1,
        t1032_eligible_pension_income=eligible_pension,
        t1032_t4a_rca_box_17="200",
        t1032_rca_payments_qualify=1,
        t1032_filer_is_transferring_spouse=1,
        t1032_receiving_spouse_pension_amount=receiving_pension,
        t1032_income_tax_deducted_on_pension="400",
        income_tax_deducted="500",
        t1032_receiving_spouse_under_65=receiving_under_65,
        t1032_transferring_spouse_65_or_older=transferring_65,
        t1032_note_1_payments=payments,
        t1032_note_1_payments_due_to_death=payments_due_to_death,
    )
    return service().compute(CA_ON, 2025, *artifacts)


def form(**overrides: Any) -> Worksheet:
    (worksheet,) = run(**{**KH, **overrides})[FORM]
    return worksheet


def return_worksheet(**overrides: Any) -> Worksheet:
    (worksheet,) = run(**{**KH, **overrides})[RETURN]
    return worksheet


# --- Note 1 recalculates lines 18 to 31 ----------------------------------------------------------


def test_line_31_is_recalculated_from_the_recalculated_line_30_when_note_1_recalculates() -> None:
    found = form()

    assert found.get(T1032_NOTE_1_RECALCULATION).value == 1
    assert found.get(T1032_LINE_30).value == D("1513.51")
    assert found.get(T1032_LINE_31).value == D("1986.49")
    assert found.get(T1032_NOTE_1_LINE_30).value == D("1500.00")
    assert found.get(T1032_NOTE_1_LINE_31).value == D("2000.00")
    assert found.get(T1032_LINE_31_AFTER_NOTE_1).value == D("2000.00")


def test_line_31400_is_the_lesser_of_2000_and_the_recalculated_line_31() -> None:
    assert form().get(T1032_LINE_31400_TRANSFERRING).value == D("2000.00")
    assert return_worksheet().get(PENSION_INCOME_CREDIT).value == D("2000.00")


def test_the_recalculated_line_31_below_2000_is_line_31400_as_it_is() -> None:
    # Line 1 is 3,000.00 less RRIF payments of 100.00: the result 2,900.00 is line 17 and half of
    # it, 1,450.00, is the recalculated line 21, which is what is elected. Line 29 = 200.00 /
    # 2,900.00 x 1,450.00 = 100.00 and line 30 = 1,350.00, so line 31 = 3,000.00 - 1,350.00 =
    # 1,650.00, under $2,000. Without Note 1 it would be 1,640.63.
    found = form(eligible_pension="3000", payments="100", elected_amount="1450")

    assert found.get(T1032_LINE_31).value == D("1640.63")
    assert found.get(T1032_NOTE_1_LINE_31).value == D("1650.00")
    assert found.get(T1032_LINE_31400_TRANSFERRING).value == D("1650.00")


def test_payments_received_on_a_death_are_not_removed_before_line_31_is_recalculated() -> None:
    # The result is line 1, 3,500.00 (under $4,000), so it is line 17: line 29 = 200.00 / 3,500.00
    # x 1,600.00 = 91.43, line 30 = 1,508.57 and line 31 = 3,500.00 - 1,508.57 = 1,991.43.
    found = form(payments_due_to_death="300")

    assert found.get(T1032_NOTE_1_RECALCULATION).value == 1
    assert found.get(T1032_NOTE_1_LINE_31).value == D("1991.43")
    assert found.get(T1032_LINE_31400_TRANSFERRING).value == D("1991.43")


# --- Note 1 does not recalculate: line 31 is as it was --------------------------------------------


def test_line_31_is_not_recalculated_when_the_result_is_4000_or_more() -> None:
    found = form(eligible_pension="8000", payments="3000")

    assert found.get(T1032_NOTE_1_RECALCULATION).value == 0
    assert found.get(T1032_LINE_31_AFTER_NOTE_1).value == found.get(T1032_LINE_31).value


@pytest.mark.parametrize(
    "overrides",
    [
        # The receiving spouse was 65 or older.
        {"receiving_under_65": 0},
        # The transferring spouse was under 65.
        {"transferring_65": 0},
        # None of the amounts a) to e) was received.
        {"payments": "0"},
        # Line 32 is $2,000 or more: not "less than $2,000".
        {"receiving_pension": "2000"},
    ],
)
def test_line_31_is_not_recalculated_when_a_condition_above_line_33_fails(
    overrides: dict[str, Any],
) -> None:
    found = form(**overrides)

    assert found.get(T1032_NOTE_1_RECALCULATION).value == 0
    assert found.get(T1032_LINE_31_AFTER_NOTE_1).value == D("1986.49")
    assert found.get(T1032_LINE_31400_TRANSFERRING).value == D("1986.49")
