"""CA-ON 2025 end to end: return iy, Canadian tuition fees paid to each institution (Schedule 11).

Schedule 11 line 1 and line 32000 print "(fees for each institution must be more than $100)". The
form takes one total of fees, so the caller also gives the number of institutions, and the total
must be more than that count times $100. Return Y's inputs, with no other tuition amount.
"""

from __future__ import annotations

import pytest

from tax_calculator.domain.errors import InputAboveBoundError, InputBelowBoundError
from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.catalog import (
    CANADIAN_TUITION_FEES,
    CANADIAN_TUITION_FEES_CHECKED,
    REFUND_OR_BALANCE_OWING,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, compute


def return_iy(canadian_tuition_fees: str, canadian_tuition_institutions: int) -> Worksheet:
    """Return Y's inputs, as in `returns/2025_return_y.yaml`, with the Canadian fees given."""
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
        canadian_tuition_fees=canadian_tuition_fees,
        canadian_tuition_institutions=canadian_tuition_institutions,
    )


def test_one_institution_with_101_is_more_than_its_100_minimum() -> None:
    # Schedule 11 line 1: one institution's fees must be more than $100, and $101 is.
    worksheet = return_iy("101", 1)

    assert worksheet.get(CANADIAN_TUITION_FEES_CHECKED).value == D("101")


def test_one_institution_with_exactly_100_is_refused() -> None:
    # "more than $100": $100 is not more than $100, so it is an input error, not dropped.
    with pytest.raises(InputBelowBoundError, match="ca/canadian_tuition_fees"):
        return_iy("100", 1)


def test_one_institution_with_60_is_refused() -> None:
    # $60 is below the $100 the form requires for each institution.
    with pytest.raises(InputBelowBoundError, match="ca/canadian_tuition_fees"):
        return_iy("60", 1)


def test_one_institution_with_100_01_is_more_than_100() -> None:
    worksheet = return_iy("100.01", 1)

    assert worksheet.get(CANADIAN_TUITION_FEES_CHECKED).value == D("100.01")


def test_two_institutions_with_201_are_more_than_their_200_minimum() -> None:
    worksheet = return_iy("201", 2)

    assert worksheet.get(CANADIAN_TUITION_FEES_CHECKED).value == D("201")


def test_two_institutions_with_exactly_200_are_refused() -> None:
    with pytest.raises(InputBelowBoundError, match="ca/canadian_tuition_fees"):
        return_iy("200", 2)


def test_zero_institutions_with_no_fees_is_the_default_and_refunds_5409_31() -> None:
    # No institution, no fees: the total and its minimum are both 0, so nothing is refused, and
    # the return is Return Y, a refund of 5409.31 as in `returns/2025_return_y.yaml`.
    worksheet = return_iy("0", 0)

    assert worksheet.get(CANADIAN_TUITION_FEES_CHECKED).value == D("0")
    assert worksheet.get(REFUND_OR_BALANCE_OWING).value == D("-5409.31")


def test_zero_institutions_with_fees_is_refused() -> None:
    # With no institution the fees must be 0; $101 for no institution is above that.
    with pytest.raises(InputAboveBoundError, match="ca/canadian_tuition_fees"):
        return_iy("101", 0)


def test_one_institution_with_no_fees_is_refused() -> None:
    # $0 is not more than one institution's $100, so the fees entered are an input error.
    with pytest.raises(InputBelowBoundError, match="ca/canadian_tuition_fees"):
        return_iy("0", 1)


def test_the_fees_entered_are_the_input_and_the_checked_fees_are_the_output() -> None:
    worksheet = return_iy("101", 1)

    assert worksheet.get(CANADIAN_TUITION_FEES).value == D("101")
    assert worksheet.get(CANADIAN_TUITION_FEES_CHECKED).value == D("101")
