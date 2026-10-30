"""CA-ON 2025 end to end: return ka, a rental partner who received no T5013 slip, whose amount 7 is
the share of amount 6 given by the percentage of the partnership."""

from __future__ import annotations

from typing import Any

import pytest

from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.domain.errors import InputAboveBoundError, InputOutOfRangeError
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog import (
    NET_RENTAL_INCOME,
    RENTAL_NET_INCOME_AFTER_CCA,
    RENTAL_PARTNER_AMOUNT_7,
    RENTAL_PARTNER_SHARE_OF_AMOUNT_6,
    RENTAL_PARTNERSHIP_NET_INCOME,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, compute, run

# Guide T4036: "If you are in a partnership and you do not receive a T5013 slip, or if you are a
# co-owner, fill in all of the parts in Form T776 that apply to you." and "Amount 7 - Partnerships:
# If you are a member of a partnership, enter your share of amount 6 or the amount from box 107 or
# 110 from your T5013 slip." Form T776 Part 1: "Your percentage of the partnership %".
#
# The statement: other income (line 8230) of 2,000, advertising (line 8521) of 500 and a CCA claim
# (line 9936) of 400, so amount 5 is 1,500 and amount 6 is 1,100, as in
# `returns/2025_return_ka.yaml`.


def class_row(
    class_number: str, ucc_at_start: str, claim: str = "0"
) -> tuple[str, str, str, str, str, str, str, int, str, str, str, str]:
    """An Area A row: the class, its UCC at the start (column 2, a chosen figure), no additions,
    no proceeds, the CCA claimed (column 23), property left in the class, no DIEP, no immediate
    expensing and no remaining personal part of the property's cost."""
    return (class_number, ucc_at_start, "0", "0", "0", "0", claim, 0, "0", "0", "0", "0")


def partner_statement(**changes: Any) -> dict[str, Any]:
    statement: dict[str, Any] = {
        "rental_other_income": "2000",
        "rental_expenses": {"advertising": ("500", "0", "0")},
        "rental_cca_classes_rows": (class_row("1", "100000.00", "400"),),
        "rental_partner": 1,
        "rental_partner_t5013_slip": 0,
        "rental_partner_percentage": "50",
    }
    return {**statement, **changes}


def ka_inputs(statement: dict[str, Any]) -> dict[str, Any]:
    """Return KA's inputs, as in `returns/2025_return_ka.yaml`: a landlord with the T776 `statement`
    given, no employment income, no RRSP, no union dues, no business, no farm, no fishing and no
    other income."""
    return {
        "employment_income": "0",
        "share_dispositions": (),
        "unused_rrsp_contributions": "0",
        "rrsp_contributions": "0",
        "rrsp_deduction_limit": "0",
        "rrsp_amount_deducted": "0",
        "union_dues": "0",
        "rental_statements": (statement,),
        "business_statements": (),
        "farm_statements": (),
        "fish_statements": (),
    }


def return_ka(statement: dict[str, Any]) -> Worksheet:
    """The worksheet of return KA's form `ca-on/return` with the T776 `statement`."""
    return compute(**ka_inputs(statement))


def statement_ka(statement: dict[str, Any]) -> Worksheet:
    """The worksheet of return KA's one Form T776 with the `statement`."""
    return run(**ka_inputs(statement))["ca/t776"][0]


def test_amount_7_is_the_percentage_of_amount_6() -> None:
    # Amount 6 is 1,500 - 400 = 1,100; 50% of it is 550.
    worksheet = statement_ka(partner_statement())

    assert worksheet.get(RENTAL_NET_INCOME_AFTER_CCA).value == D("1100")
    assert worksheet.get(RENTAL_PARTNER_SHARE_OF_AMOUNT_6).value == D("550.00")
    assert worksheet.get(RENTAL_PARTNER_AMOUNT_7).value == D("550.00")


def test_line_9946_is_amount_7_plus_line_9974_minus_line_9943() -> None:
    worksheet = statement_ka(
        partner_statement(rental_partner_gst_hst_rebate="20", rental_partner_other_expenses="5")
    )

    assert worksheet.get(RENTAL_PARTNERSHIP_NET_INCOME).value == D("565.00")
    assert worksheet.get(NET_RENTAL_INCOME).value == D("565.00")


def test_t1_line_12600_is_line_9946() -> None:
    worksheet = return_ka(
        partner_statement(rental_partner_gst_hst_rebate="20", rental_partner_other_expenses="5")
    )

    assert worksheet.get(NET_RENTAL_INCOME).value == D("565.00")


def test_the_share_rounds_half_up_to_the_cent() -> None:
    # 1,100 x 33.335% = 366.685, half up 366.69.
    worksheet = statement_ka(partner_statement(rental_partner_percentage="33.335"))

    assert worksheet.get(RENTAL_PARTNER_AMOUNT_7).value == D("366.69")


def test_a_loss_is_shared_as_a_loss() -> None:
    # Advertising of 3,000 makes amount 5 -1,000; no CCA is claimed, so amount 6 is -1,000 and 25%
    # of it is -250.
    worksheet = statement_ka(
        partner_statement(
            rental_expenses={"advertising": ("3000", "0", "0")},
            rental_cca_classes_rows=(),
            rental_partner_percentage="25",
        )
    )

    assert worksheet.get(RENTAL_NET_INCOME_AFTER_CCA).value == D("-1000")
    assert worksheet.get(RENTAL_PARTNER_AMOUNT_7).value == D("-250.00")


def test_the_trace_shows_amount_6_times_the_percentage() -> None:
    worksheet = statement_ka(partner_statement())

    rendered = EnglishTraceRenderer().render_all(worksheet.trace)

    assert (
        "rental_partner_share_of_amount_6: rental_partner_percentage_checked 50% of "
        "rental_net_income_after_cca 1100 = 550 (half-up to 0.01)"
    ) in rendered
    assert (
        "rental_partner_amount_7: rental_partner_share_of_amount_6 550, "
        "chosen as rental_partner_t5013_slip_checked is 0"
    ) in rendered


def test_a_partner_with_a_slip_keeps_the_typed_amount_7_and_ignores_the_percentage() -> None:
    # A slip partner fills in "only" the business number, the percentage and amount 7, so the
    # percentage is entered but amount 7 is the slip's 600.
    worksheet = statement_ka(
        {
            "rental_partner": 1,
            "rental_partner_t5013_slip": 1,
            "rental_partner_share": "600",
            "rental_partner_percentage": "50",
        }
    )

    assert worksheet.get(RENTAL_PARTNER_AMOUNT_7).value == D("600")
    assert worksheet.get(NET_RENTAL_INCOME).value == D("600")


def test_a_percentage_of_100_is_accepted_and_above_100_is_refused() -> None:
    # A share of the partnership is at most the whole, as the form prints a percentage (100).
    worksheet = statement_ka(partner_statement(rental_partner_percentage="100"))

    assert worksheet.get(RENTAL_PARTNER_AMOUNT_7).value == D("1100.00")
    with pytest.raises(InputAboveBoundError, match=r"rental_partner_percentage 100\.01"):
        return_ka(partner_statement(rental_partner_percentage="100.01"))


def test_a_typed_amount_7_from_a_partner_with_no_slip_is_refused() -> None:
    with pytest.raises(InputOutOfRangeError, match=r"rental_partner_amount_7_conflict"):
        return_ka(partner_statement(rental_partner_share="550"))


def test_a_percentage_from_a_filer_who_is_not_a_partner_is_not_read() -> None:
    # A co-owner enters the percentage too (Guide T4036): line 9946 is amount 6, 1,100.00.
    worksheet = statement_ka(partner_statement(rental_partner=0))

    assert worksheet.get(NET_RENTAL_INCOME).value == D("1100.00")
