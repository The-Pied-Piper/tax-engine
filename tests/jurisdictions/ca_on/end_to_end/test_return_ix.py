"""CA-ON 2025 end to end: return ix, a tuition amount transferred from students (line 32400)."""

from __future__ import annotations

import pytest

from tax_engine.domain.errors import InputAboveBoundError
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog import (
    NON_REFUNDABLE_CREDIT_AMOUNTS,
    REFUND_OR_BALANCE_OWING,
    TOTAL_PAYABLE,
    TUITION_TRANSFERRED_FROM_CHILD_CHECKED,
    TUITION_TRANSFERRED_FROM_CHILD_MAXIMUM,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, compute


def return_ix(tuition_transferred_from_child: str, tuition_transfer_students: int) -> Worksheet:
    """Return Y's inputs, as in `returns/2025_return_ix.yaml`, with the tuition transfer given."""
    return compute(
        "60000",
        (),
        "0",
        "0",
        "10800",
        "0",
        "0",
        dependent_children=1,
        eligible_dependants=1,
        cwb_eligible_dependants=1,
        child_care_expenses_paid="6000",
        children_seven_to_sixteen=1,
        income_tax_deducted="8000",
        care_supporting_persons_adjusted_income="30000",
        tuition_transferred_from_child=tuition_transferred_from_child,
        tuition_transfer_students=tuition_transfer_students,
    )


def test_one_student_transferring_5000_is_within_the_bound_and_refunds_6134_31() -> None:
    # Line 32400 for one student: the bound is 1 x $5,000.00 (the guide's maximum for each student,
    # taking the student's own use as nothing), so $5,000 is kept as entered. It adds 5000 x 14.5%
    # = 725.00 to the federal non-refundable credits, so the total payable is Return Y's 4240.69 -
    # 725.00 = 3515.69 and the refund is 3515.69 - 9650.00 = -6134.31, negative: a refund of
    # 6134.31.
    worksheet = return_ix("5000", 1)

    assert worksheet.get(TUITION_TRANSFERRED_FROM_CHILD_MAXIMUM).value == D("5000.00")
    assert worksheet.get(TUITION_TRANSFERRED_FROM_CHILD_CHECKED).value == D("5000")
    assert worksheet.get(NON_REFUNDABLE_CREDIT_AMOUNTS).value == D("42509.75")
    assert worksheet.get(TOTAL_PAYABLE).value == D("3515.69")
    assert worksheet.get(REFUND_OR_BALANCE_OWING).value == D("-6134.31")


def test_one_student_transferring_just_over_5000_is_refused() -> None:
    # Line 32400 "maximum $5,000 for each student": 5000.01 is above one student's $5,000 and an
    # input error, not capped at $5,000.
    with pytest.raises(InputAboveBoundError, match="ca/tuition_transferred_from_child"):
        return_ix("5000.01", 1)


def test_one_student_transferring_12000_is_refused_not_capped() -> None:
    # The printed maximum per student is $5,000, so $12,000 from one student is $7,000 over it: an
    # error, where a cap at $5,000 would instead give a refund of 6134.31 and an uncapped total
    # would give 7149.31, $1,015.00 more than the form allows at 14.5%.
    with pytest.raises(InputAboveBoundError, match="ca/tuition_transferred_from_child"):
        return_ix("12000", 1)


def test_two_students_transferring_10000_are_within_the_bound_and_refund_6859_31() -> None:
    # Two students at $5,000 each are $10,000, the bound of 2 x $5,000.00, so the whole transfer is
    # kept. It adds 10000 x 14.5% = 1450.00 to the federal non-refundable credits: the total payable
    # is Return Y's 4240.69 - 1450.00 = 2790.69, and the refund is 2790.69 - 9650.00 = -6859.31.
    worksheet = return_ix("10000", 2)

    assert worksheet.get(TUITION_TRANSFERRED_FROM_CHILD_MAXIMUM).value == D("10000.00")
    assert worksheet.get(TUITION_TRANSFERRED_FROM_CHILD_CHECKED).value == D("10000")
    assert worksheet.get(NON_REFUNDABLE_CREDIT_AMOUNTS).value == D("47509.75")
    assert worksheet.get(TOTAL_PAYABLE).value == D("2790.69")
    assert worksheet.get(REFUND_OR_BALANCE_OWING).value == D("-6859.31")


def test_no_students_and_no_transfer_leave_return_y_unchanged() -> None:
    # With no student and $0 transferred the bound is $0 and the transfer is $0, which is within it:
    # the return is Return Y, a refund of 5409.31.
    worksheet = return_ix("0", 0)

    assert worksheet.get(TUITION_TRANSFERRED_FROM_CHILD_MAXIMUM).value == D("0.00")
    assert worksheet.get(TUITION_TRANSFERRED_FROM_CHILD_CHECKED).value == D("0")
    assert worksheet.get(REFUND_OR_BALANCE_OWING).value == D("-5409.31")


def test_no_students_with_any_transfer_is_refused() -> None:
    # Zero students gives a bound of $0, so $1 transferred from no student is above it.
    with pytest.raises(InputAboveBoundError, match="ca/tuition_transferred_from_child"):
        return_ix("1", 0)
