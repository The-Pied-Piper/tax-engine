"""CA-ON 2025 end to end: T1 line 22000 "Allowable deduction" against line 21999 "Total",
under "Line 45: Support payments made".

Guide 5000-G, "Lines 21999 and 22000 - Support payments made": line 21999 is "the total amount of
support payments that you paid under a court order or written agreement", and line 22000 is "the
deductible part of the support payments that you made". The deductible part is a part of the total
paid, so a deduction above the total is an input error, not capped (`core/at_most`).
"""

from __future__ import annotations

import pytest

from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.domain.errors import InputAboveBoundError
from tax_engine.jurisdictions.ca.catalog import DEDUCTIONS_FROM_TOTAL_INCOME
from tests.jurisdictions.ca_on.end_to_end.support import D, step_3


def test_a_deduction_one_cent_above_the_total_paid_is_refused_naming_both_kinds() -> None:
    # Line 22000 "the deductible part" of line 21999 "the total amount": 6000.01 against a total of
    # 6000 is an input error, not capped to 6000.
    with pytest.raises(InputAboveBoundError) as raised:
        step_3(support_payments_made_total="6000", support_payments_deduction="6000.01")

    assert str(raised.value) == (
        "ca-on/return, instance 1: "
        "ca/support_payments_deduction 6000.01 is above ca/support_payments_made_total 6000"
    )


def test_a_deduction_of_5000_with_line_21999_unset_is_refused_against_0() -> None:
    # Line 21999 left at 0 (not entered) with a deduction on line 22000 of 5000: above the total
    # paid of 0, so refused, not accepted because nothing is entered on line 21999.
    with pytest.raises(InputAboveBoundError) as raised:
        step_3(support_payments_deduction="5000")

    assert str(raised.value) == (
        "ca-on/return, instance 1: "
        "ca/support_payments_deduction 5000 is above ca/support_payments_made_total 0"
    )


def test_a_deduction_equal_to_the_total_paid_is_accepted_and_deducted() -> None:
    # Line 22000 equal to line 21999 is "the deductible part" of the total: accepted as entered,
    # and the sum on line 23300 takes it. The check is the trace line of `core/at_most`.
    worksheet = step_3(support_payments_made_total="5000", support_payments_deduction="5000")

    assert worksheet.get(DEDUCTIONS_FROM_TOTAL_INCOME).value == D("5000")
    rendered = EnglishTraceRenderer().render_all(worksheet.trace)
    assert (
        "support_payments_deduction_checked: support_payments_deduction 5000, "
        "at most support_payments_made_total 5000"
    ) in rendered
    # The sum's line holds the checked amount among the other parts, so it is a substring of a line.
    assert any("+ support_payments_deduction_checked 5000 " in line for line in rendered)


@pytest.mark.parametrize("total_paid", ["0", "1000"])
def test_a_deduction_of_0_is_accepted_whatever_the_total_paid(total_paid: str) -> None:
    # No deductible part (line 22000 is 0): accepted with line 21999 at 0 or at any other amount.
    worksheet = step_3(support_payments_made_total=total_paid, support_payments_deduction="0")

    assert worksheet.get(DEDUCTIONS_FROM_TOTAL_INCOME).value == D("0")
    rendered = EnglishTraceRenderer().render_all(worksheet.trace)
    assert (
        "support_payments_deduction_checked: support_payments_deduction 0, "
        f"at most support_payments_made_total {total_paid}"
    ) in rendered
