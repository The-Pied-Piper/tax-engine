"""CA-ON 2025 end to end: return mt, Form T1212 "Statement of Deferred Security Options Benefits"
as its own form, and the security options deduction of T1 line 24900.

The worked return `returns/2025_return_mt.yaml` (employment income of 3,000.00, T1212 line 1 of
12,000.00 and line 2 of 2,000.00) is checked by `test_worked_returns.py`. This module computes each
example on its own: the form `ca/t1212` (run once: line 3 and the 50% of line 2 of footnote (1)),
the line 24900 of the return, which adds that 50% amount, and the Form T691 Part 1 line 29, which is
the same amount. A line 2 above line 1 is refused, never capped.
"""

from __future__ import annotations

from typing import Any

import pytest

from tax_calculator.domain.errors import CapabilityContractError
from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.catalog import (
    AMT_T1212_LINE_29_DEFERRED_SECURITY_OPTIONS,
    SECURITY_OPTIONS_DEDUCTIONS,
    T1212_LINE_3_CLOSING_BALANCE,
    T1212_LINE_24900_AMOUNT,
    TAXABLE_INCOME,
)
from tests.jurisdictions.ca_on.end_to_end.support import CA_ON, D, service, starting

T1212 = "ca/t1212"
RETURN = "ca-on/return"


def run(
    *, line_1: str = "12000", line_2: str = "2000", **overrides: Any
) -> dict[str, tuple[Worksheet, ...]]:
    """Every form's worksheets of return MT with the T1212 lines 1 and 2 given: employment income
    of 3,000.00 and no other income."""
    artifacts = starting(
        "3000",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        t1212_line_1_opening_balance=line_1,
        t1212_line_2_benefits_no_longer_deferred=line_2,
        **overrides,
    )
    return service().compute(CA_ON, 2025, *artifacts)


def return_mt(**overrides: Any) -> Worksheet:
    (worksheet,) = run(**overrides)[RETURN]
    return worksheet


def t1212_form(**overrides: Any) -> Worksheet:
    (worksheet,) = run(**overrides)[T1212]
    return worksheet


def test_line_3_is_line_1_less_line_2() -> None:
    assert t1212_form().get(T1212_LINE_3_CLOSING_BALANCE).value == D("10000.00")


def test_line_3_equals_line_1_when_line_2_is_nil() -> None:
    assert t1212_form(line_2="0").get(T1212_LINE_3_CLOSING_BALANCE).value == D("12000")


def test_line_3_is_nil_when_line_2_is_all_of_line_1() -> None:
    assert t1212_form(line_1="3000", line_2="3000").get(T1212_LINE_3_CLOSING_BALANCE).value == D(
        "0"
    )


def test_footnote_1_is_50_percent_of_line_2() -> None:
    assert t1212_form().get(T1212_LINE_24900_AMOUNT).value == D("1000.00")


def test_the_50_percent_amount_rounds_half_up_to_the_cent() -> None:
    # 50% of 0.01 is 0.005, a tie, up to 0.01.
    assert t1212_form(line_1="1", line_2="0.01").get(T1212_LINE_24900_AMOUNT).value == D("0.01")


def test_line_24900_of_the_return_is_the_50_percent_amount() -> None:
    assert return_mt().get(SECURITY_OPTIONS_DEDUCTIONS).value == D("1000.00")
    assert return_mt().get(TAXABLE_INCOME).value == D("2000.00")


def test_t691_line_29_is_the_same_50_percent_amount() -> None:
    assert return_mt().get(AMT_T1212_LINE_29_DEFERRED_SECURITY_OPTIONS).value == D("1000.00")


def test_no_t1212_amounts_leave_the_return_without_a_deduction() -> None:
    worksheet = return_mt(line_1="0", line_2="0")

    assert worksheet.get(SECURITY_OPTIONS_DEDUCTIONS).value == D("0")
    assert worksheet.get(TAXABLE_INCOME).value == D("3000.00")


def test_line_2_above_line_1_is_refused_not_capped() -> None:
    with pytest.raises(CapabilityContractError, match="cannot be negative"):
        run(line_1="1000", line_2="1000.01")
