"""CA-ON 2025 end to end: line 43700 "Total income tax deducted" is taken as entered.

Tax deducted at source is not checked against the income it came from. The form prints no limit on
it (Guide 5000-G line 43700 and the line titles of Form 5006-R), so an amount above the income is
not refused: it is entered as it is on the slip and the refund shows the amount over.
"""

from __future__ import annotations

from typing import Any

from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog import (
    INCOME_TAX_DEDUCTED_AFTER_ELECTION,
    REFUND,
    TOTAL_CREDITS,
    TOTAL_INCOME,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, compute, routed_statement


def return_with_other_income(**overrides: Any) -> Worksheet:
    """The return's worksheet for a single filer whose only income is other income of 20000, so
    total income is 20000.00 and the Canada workers benefit (which needs employment income) is 0,
    unless overridden."""
    inputs: dict[str, Any] = {"other_income": "20000"}
    return compute("0", (), "0", "0", "0", "0", "0", **{**inputs, **overrides})


def return_with_wages(wages: str, **overrides: Any) -> Worksheet:
    """The return's worksheet for a single filer whose only income is employment of `wages`."""
    return compute(wages, (), "0", "0", "0", "0", "0", **overrides)


def test_tax_deducted_equal_to_total_income_is_accepted_and_counted_in_total_credits() -> None:
    # Total income 20000.00 (line 15000) and tax deducted 20000 (line 43700): the amount entered is
    # the one that is counted, and total credits (line 48200) is 20000.
    worksheet = return_with_other_income(income_tax_deducted="20000")

    assert worksheet.get(TOTAL_INCOME).value == D("20000.00")
    assert worksheet.get(TOTAL_CREDITS).value == D("20000.00")
    rendered = EnglishTraceRenderer().render_all(worksheet.trace)
    # The total credits sum reads the amount entered, as the line 43700 amount after the election.
    credits_sum = "total_credits: income_tax_deducted_after_election 20000 + cpp_overpayment 0 "
    assert any(line.startswith(credits_sum) for line in rendered)


def test_tax_deducted_one_cent_above_total_income_is_accepted_and_counted() -> None:
    # One cent more than total income is not refused or capped: the 20000.01 entered is counted.
    worksheet = return_with_other_income(income_tax_deducted="20000.01")

    assert worksheet.get(INCOME_TAX_DEDUCTED_AFTER_ELECTION).value == D("20000.01")
    assert worksheet.get(TOTAL_CREDITS).value == D("20000.01")


def test_tax_withheld_above_the_wages_is_accepted_and_the_refund_is_the_amount_over() -> None:
    # Wages of 30000 (total income 30000.00) and tax withheld of 35000: accepted, not refused or
    # capped. The refund is the total credits less the total payable, so it is the 5000 over the
    # refund of the same return with tax withheld equal to the wages of 30000.
    over = return_with_wages("30000", income_tax_deducted="35000")
    equal = return_with_wages("30000", income_tax_deducted="30000")

    assert over.get(TOTAL_INCOME).value == D("30000.00")
    assert over.get(INCOME_TAX_DEDUCTED_AFTER_ELECTION).value == D("35000")
    assert over.get(REFUND).value - equal.get(REFUND).value == D("5000")


def test_tax_deducted_above_the_income_before_losses_is_accepted_with_a_business_loss() -> None:
    # Other income of 20000 and a business loss of 50000 (a T2125 net of -50000, routed to line
    # 13500): total income is -30000.00. Tax deducted of 20000.01 is above the income before losses
    # (20000.00) and is accepted, counted in total credits as entered.
    worksheet = return_with_other_income(
        business_statements=(routed_statement("-50000", 1),),
        income_tax_deducted="20000.01",
    )

    assert worksheet.get(TOTAL_INCOME).value == D("-30000.00")
    assert worksheet.get(TOTAL_CREDITS).value == D("20000.01")


def test_no_tax_deducted_with_a_business_loss_larger_than_other_income_is_accepted() -> None:
    # The same loss with no tax deducted (line 43700 of 0): total income is -30000.00, and the
    # return is computed.
    worksheet = return_with_other_income(
        business_statements=(routed_statement("-50000", 1),),
        income_tax_deducted="0",
    )

    assert worksheet.get(TOTAL_INCOME).value == D("-30000.00")
    assert worksheet.get(TOTAL_CREDITS).value == D("0")
