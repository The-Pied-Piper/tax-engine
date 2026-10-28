"""CA-ON 2025 end to end: return KK, Form T1032 Note 1 checks (the amounts a) to e) compared with
line 1 only when Note 1 applies, and line 8 compared with the line 17 of the
recalculation).

The worked return `returns/2025_return_kk.yaml` is checked by `test_worked_returns.py`. This module
runs the transferring spouse's return of KH (line 1 of 3,500.00, an RCA life annuity of 200.00,
1,600.00 elected) with other starting figures of Note 1:

- the amounts a) to e) count only where Note 1 applies (the conditions above line 33 all apply) and
  are not bounded by line 1, which the form does not print;
- line 8 over a line 17 of 0 (a division by 0) is refused; line 8 above a line 17 above 0 is printed
  arithmetic, and a line 34 it takes below 0 is refused; line 8 of 0 over a line 17 of 0 is not,
  the form then says to enter line 22 on line 30;
- the elected amount stays as entered when it is above the recalculated line 21: the form asks for
  that check on line 22 once, against the first line 21.
"""

from __future__ import annotations

from typing import Any

import pytest

from tax_calculator.domain.errors import CapabilityContractError, InputAboveBoundError
from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.catalog import T1032_LINE_31400_TRANSFERRING
from tests.jurisdictions.ca_on.end_to_end.support import CA_ON, D, service, starting

FORM = "ca/t1032"

# The transferring spouse's return of KH: line 1 is 3,500.00 and the RCA life annuity (line 4)
# 200.00, so line 8 is 200.00, line 17 is 3,700.00 and line 21 is 1,850.00; 1,600.00 is elected.
KK: dict[str, Any] = {
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
    rca_box_17: str = "200",
    elected_amount: str = "1600",
) -> dict[str, tuple[Worksheet, ...]]:
    """Every form's worksheets of the transferring spouse's return with the starting figures of
    the form and of line 33 given."""
    artifacts = starting(
        "0",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        other_income=rca_box_17,
        other_pensions_and_superannuation=eligible_pension,
        t1032_line_22=elected_amount,
        spouse_or_common_law_partner_on_december_31=1,
        t1032_eligible_pension_income=eligible_pension,
        t1032_t4a_rca_box_17=rca_box_17,
        t1032_rca_payments_qualify=1,
        t1032_filer_is_transferring_spouse=1,
        t1032_receiving_spouse_pension_amount="0",
        t1032_income_tax_deducted_on_pension="400",
        income_tax_deducted="500",
        t1032_receiving_spouse_under_65=receiving_under_65,
        t1032_transferring_spouse_65_or_older=transferring_65,
        t1032_note_1_payments=payments,
        t1032_note_1_payments_due_to_death=payments_due_to_death,
    )
    return service().compute(CA_ON, 2025, *artifacts)


def form(**overrides: Any) -> Worksheet:
    (worksheet,) = run(**{**KK, **overrides})[FORM]
    return worksheet


# --- the amounts a) to e) are compared with line 1 only when Note 1 applies ----------------


@pytest.mark.parametrize(
    "overrides",
    [
        # The receiving spouse was 65 or older.
        {"receiving_under_65": 0},
        # The transferring spouse was under 65.
        {"transferring_65": 0},
    ],
)
def test_amounts_above_line_1_are_not_refused_when_a_condition_above_line_33_fails(
    overrides: dict[str, Any],
) -> None:
    # Line 1 is 3,500.00 and 5,000.00 of payments are entered; Note 1 is not followed.
    found = form(payments="5000", **overrides)

    assert found.get(T1032_LINE_31400_TRANSFERRING).value == D("1986.49")


def test_a_death_part_above_the_amounts_is_not_refused_when_note_1_does_not_apply() -> None:
    # 500.00 received on a death is more than the 100.00 of amounts a) to d), which Note 1 would
    # refuse; the receiving spouse is 65 or older, so Note 1 is not followed.
    found = form(payments="100", payments_due_to_death="500", receiving_under_65=0)

    assert found.get(T1032_LINE_31400_TRANSFERRING).value == D("1986.49")


def test_amounts_above_line_1_give_a_negative_credit_which_is_refused() -> None:
    # The form prints no bound against line 1; the result -0.01 is line 17 and the transferring
    # spouse's line 31400 comes out below 0.
    with pytest.raises(CapabilityContractError):
        run(**{**KK, "payments": "3500.01"})


# --- line 8 is compared with the line 17 of the recalculation ------------------------------------


def test_line_8_equal_to_the_recalculated_line_17_is_followed() -> None:
    # 3,500.00 less 3,300.00 of payments is 200.00, which is line 17 and line 8: line 29 =
    # 200.00 / 200.00 x 1,600.00 = 1,600.00, line 30 = 0.00 and line 31 = 3,500.00. The elected
    # 1,600.00 is above the recalculated line 21 (100.00) and stays as entered.
    found = form(payments="3300")

    assert found.get(T1032_LINE_31400_TRANSFERRING).value == D("2000.00")


def test_line_8_above_the_recalculated_line_17_gives_a_negative_line_34_which_is_refused() -> None:
    # 3,500.00 less 3,400.00 is 100.00, below line 8 (200.00): line 30 is 1,600.00 -
    # 200.00 / 100.00 x 1,600.00 = -1,600.00, line 33 the same and line 34, the credit amount,
    # below 0.
    with pytest.raises(CapabilityContractError):
        run(**{**KK, "payments": "3400"})


def test_line_8_above_a_recalculated_line_17_of_0_is_refused() -> None:
    # 3,500.00 less 3,500.00 is 0.00: line 27 would divide 200.00 by 0.00.
    with pytest.raises(InputAboveBoundError):
        run(**{**KK, "payments": "3500"})


def test_line_8_of_0_with_a_recalculated_line_17_of_0_enters_line_22_on_line_30() -> None:
    # No amount on line 8 (no RCA payments): "enter the amount from line 22 on line 30", 1,600.00,
    # so line 31 is 3,500.00 - 1,600.00 = 1,900.00.
    found = form(payments="3500", rca_box_17="0")

    assert found.get(T1032_LINE_31400_TRANSFERRING).value == D("1900.00")


def test_line_8_above_the_recalculated_line_17_is_followed_when_nothing_is_elected() -> None:
    # Line 22 is 0.00, so line 28 is 0.00 and line 29 is 0.00 whatever line 27 is, line 30 is 0.00
    # and line 31 is 3,500.00: nothing is refused.
    found = form(payments="3400", elected_amount="0")

    assert found.get(T1032_LINE_31400_TRANSFERRING).value == D("2000.00")
    assert form(payments="3500", elected_amount="0").get(T1032_LINE_31400_TRANSFERRING).value == D(
        "2000.00"
    )
