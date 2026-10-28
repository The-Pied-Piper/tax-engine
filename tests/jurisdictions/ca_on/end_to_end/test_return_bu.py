"""CA-ON 2025 end to end: return bu."""

from __future__ import annotations

from typing import Any

import pytest

from tax_calculator.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_calculator.domain.errors import InputAboveBoundError
from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.catalog import REFUND_OR_BALANCE_OWING
from tax_calculator.jurisdictions.ca_on.catalog import (
    FLOW_THROUGH_SHARE_CLAIMABLE,
    FLOW_THROUGH_SHARE_CREDIT,
    FLOW_THROUGH_SHARE_EXPENSES,
    FLOW_THROUGH_SHARE_EXPENSES_CLAIMED,
    ONTARIO_CREDITS,
    ONTARIO_CREDITS_SUBTOTAL,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, compute


def return_bu(**overrides: Any) -> Worksheet:
    """Return BU's inputs, as in `returns/2025_return_bu.yaml`: Return AK's filer, not a resident.

    The filer was not a resident of Ontario on December 31, 2025 (the count is 1, a chosen input).
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
        "not_resident_of_ontario_at_year_end": 1,
    }
    return compute("60000", (), "0", "0", "10800", "0", "0", **{**inputs, **overrides})


def test_return_bus_slips_total_10000_but_the_credit_is_not_claimable() -> None:
    # T1221: "You must be a resident of Ontario on the last day of the tax year to claim this
    # credit." The filer was not, so the condition applies, the count is 0, and the 10000 total of
    # T1221 line 4 is not entered on ON479 line 17, whose 5% is then 0.00.
    worksheet = return_bu()

    assert worksheet.get(FLOW_THROUGH_SHARE_EXPENSES).value == D("10000")
    assert worksheet.get(FLOW_THROUGH_SHARE_CLAIMABLE).value == 0
    assert worksheet.get(FLOW_THROUGH_SHARE_EXPENSES_CLAIMED).value == D("0")
    assert worksheet.get(FLOW_THROUGH_SHARE_CREDIT).value == D("0.00")
    # Lines 1, 2, 13, 14 and 16 are Return AK's, 8230.00 less its 500.00 on line 17.
    assert worksheet.get(ONTARIO_CREDITS_SUBTOTAL).value == D("7730.00")
    assert worksheet.get(ONTARIO_CREDITS).value == D("12930.00")


def test_a_resident_of_ontario_on_the_last_day_claims_the_credit_as_in_return_ak() -> None:
    worksheet = return_bu(not_resident_of_ontario_at_year_end=0)

    assert worksheet.get(FLOW_THROUGH_SHARE_CLAIMABLE).value == 1
    assert worksheet.get(FLOW_THROUGH_SHARE_EXPENSES_CLAIMED).value == D("10000")
    assert worksheet.get(FLOW_THROUGH_SHARE_CREDIT).value == D("500.00")
    assert worksheet.get(ONTARIO_CREDITS_SUBTOTAL).value == D("8230.00")


def test_return_bus_refund_is_the_resident_refund_less_the_credit_and_the_tax_reduction() -> None:
    # The credit (500.00) is lost, and the same count rules out the Ontario tax reduction
    # (244.74), so the refund is 17189.31 - 500.00 - 244.74 = 16444.57.
    worksheet = return_bu()

    assert worksheet.get(REFUND_OR_BALANCE_OWING).value == D("-16444.57")


def test_the_trace_shows_the_condition_and_the_expenses_not_entered() -> None:
    rendered = EnglishTraceRenderer().render_all(return_bu().trace)

    assert (
        'flow_through_share_claimable: condition 1 "You were not a resident of Ontario on the last '
        'day of the tax year": not_resident_of_ontario_at_year_end_checked 1, applies'
    ) in rendered
    assert "flow_through_share_claimable: condition 1 applies, so 0" in rendered
    assert (
        "flow_through_share_expenses_claimed: flow_through_share_expenses 10000 "
        "for each of 0 flow_through_share_claimable = 0"
    ) in rendered
    assert (
        "flow_through_share_credit: 5% of flow_through_share_expenses_claimed 0 (half-up to 0.01)"
    ) in rendered


def test_a_resident_answer_of_2_is_refused_and_not_read_as_a_resident() -> None:
    # Form T1221 "You must be a resident of Ontario on the last day of the tax year to claim this
    # credit.": the count is a yes or no answer, so 2 is an input error, not "not a resident".
    with pytest.raises(
        InputAboveBoundError,
        match="not_resident_of_ontario_at_year_end 2 is above a yes or no answer of 1",
    ):
        return_bu(not_resident_of_ontario_at_year_end=2)
