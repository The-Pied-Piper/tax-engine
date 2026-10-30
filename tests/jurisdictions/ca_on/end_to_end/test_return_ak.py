"""CA-ON 2025 end to end: return ak."""

from __future__ import annotations

from typing import Any

import pytest

from tax_engine.domain.errors import InvalidTextError
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog import REFUND_OR_BALANCE_OWING, TOTAL_CREDITS
from tax_engine.jurisdictions.ca_on.catalog import (
    COOP_CLAIMED_AS_PARTNERSHIP_MEMBER,
    COOP_EDUCATION_CREDIT,
    COOP_EDUCATION_PLACEMENT_COUNT,
    COOP_PARTNERSHIP_BUSINESS_NUMBER,
    ONTARIO_CREDITS,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, compute, return_r


def return_ak(**overrides: Any) -> Worksheet:
    """Return AK's inputs, as in `returns/2025_return_ak.yaml`: Return R's filer in a partnership.

    Return R's inputs (Return M's taxpayer with two work placements of eligible expenditures 8000
    and 15000 and total salaries and wages paid in 2024 of 500000); the credit is claimed as a
    member of a partnership (line 63265 is 1) and the business number (line 63270) is
    "123456789", a chosen figure.
    """
    inputs: dict[str, Any] = {
        "dependent_children": 1,
        "eligible_dependants": 1,
        "cwb_eligible_dependants": 1,
        "child_care_expenses_paid": "6000",
        "children_seven_to_sixteen": 1,
        "income_tax_deducted": "8000",
        "fertility_expenses": "24000",
        "seniors_transit_paid": "1200",
        "flow_through_share_slips": ("6000", "4000"),
        "coop_education_payroll": "500000",
        "coop_education_placements": ("8000", "15000"),
        "coop_claimed_as_partnership_member": 1,
        "coop_partnership_business_number": "123456789",
    }
    return compute("60000", (), "0", "0", "10800", "0", "0", **{**inputs, **overrides})


def test_return_aks_partnership_lines_are_carried_on_the_return_as_entered() -> None:
    # ON479 "Line 63265: Are you claiming this credit as a member of a partnership? 1 Yes or 2
    # No" and "Line 63270: If yes, enter your nine-digit business number. (enter 9 digits)": the
    # form computes nothing from them, so line 63265 is the 1 entered (yes) and line 63270 the
    # text "123456789" entered, a string and not a number.
    worksheet = return_ak()

    assert worksheet.get(COOP_CLAIMED_AS_PARTNERSHIP_MEMBER).value == 1
    assert type(worksheet.get(COOP_CLAIMED_AS_PARTNERSHIP_MEMBER).value) is int
    assert worksheet.get(COOP_PARTNERSHIP_BUSINESS_NUMBER).value == "123456789"
    assert type(worksheet.get(COOP_PARTNERSHIP_BUSINESS_NUMBER).value) is str


def test_a_business_number_is_carried_with_its_leading_zero() -> None:
    # "enter 9 digits": nine digits as typed, so a number that starts with 0 keeps it.
    worksheet = return_ak(coop_partnership_business_number="012345678")

    assert worksheet.get(COOP_PARTNERSHIP_BUSINESS_NUMBER).value == "012345678"


def test_a_claim_that_is_not_as_a_partnership_member_carries_0_and_a_blank_number() -> None:
    # "If yes, enter your nine-digit business number": for a no the box is blank, the empty
    # text, and line 63265 is 0.
    worksheet = return_ak(coop_claimed_as_partnership_member=0, coop_partnership_business_number="")

    assert worksheet.get(COOP_CLAIMED_AS_PARTNERSHIP_MEMBER).value == 0
    assert worksheet.get(COOP_PARTNERSHIP_BUSINESS_NUMBER).value == ""


def test_a_return_that_does_not_claim_as_a_partnership_member_carries_0_and_a_blank_number() -> (
    None
):
    worksheet = return_r()

    assert worksheet.get(COOP_CLAIMED_AS_PARTNERSHIP_MEMBER).value == 0
    assert worksheet.get(COOP_PARTNERSHIP_BUSINESS_NUMBER).value == ""


def test_the_partnership_lines_change_no_computed_line() -> None:
    # Nothing is computed from lines 63265 and 63270: Return AK has Return R's credit, 5200.00,
    # Ontario credits, 13430.00, total credits, 21430.00, and refund, -17189.31, whatever they say.
    member = return_ak()
    not_member = return_ak(
        coop_claimed_as_partnership_member=0, coop_partnership_business_number=""
    )

    for worksheet in (member, not_member, return_r()):
        assert worksheet.get(COOP_EDUCATION_CREDIT).value == D("5200.00")
        assert worksheet.get(COOP_EDUCATION_PLACEMENT_COUNT).value == 2
        assert worksheet.get(ONTARIO_CREDITS).value == D("13430.00")
        assert worksheet.get(TOTAL_CREDITS).value == D("21430.00")
        assert worksheet.get(REFUND_OR_BALANCE_OWING).value == D("-17189.31")


@pytest.mark.parametrize(
    "text",
    ["12345678", "1234567890", "12345678a", "123 456 789", "123-456-789", "١٢٣٤٥٦٧٨٩"],
)
def test_a_business_number_that_is_not_nine_digits_is_refused_naming_the_kind(text: str) -> None:
    with pytest.raises(InvalidTextError, match="ca-on/coop_partnership_business_number"):
        return_ak(coop_partnership_business_number=text)
