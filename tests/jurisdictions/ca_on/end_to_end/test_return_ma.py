"""CA-ON 2025 end to end: return ma (Form T1206 lines 25 to 27 when minimum tax is payable)."""

from __future__ import annotations

from typing import Any

from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog import (
    AMT_FEDERAL_TAX_PAYABLE_UNDER_MINIMUM_TAX,
    FEDERAL_TAX_LESS_CREDITS,
    FEDERAL_TAX_LINE_41700,
    NET_FEDERAL_TAX,
    REFUND_OR_BALANCE_OWING,
    SPLIT_INCOME_LINE_24,
    SPLIT_INCOME_LINE_29,
    SPLIT_INCOME_LINE_30,
    TOTAL_PAYABLE,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, compute


def return_ma(**overrides: Any) -> Worksheet:
    """Return MA's inputs, as in `returns/2025_return_ma.yaml`, over the keyword overrides given.

    Return CA's filer with 1000000 more of other income (1040000 in all, line 3 of Form T1206 still
    40000) and a security options deduction of 1000000 (T4 boxes 39 and 91), so that minimum tax
    is payable.
    """
    inputs: dict[str, Any] = {
        "other_dividends_received_without_a_slip": "10000",
        "other_income": "1040000",
        "foreign_investment_income": "10000",
        "foreign_tax_countries_rows": (("15000", "50000"),),
        "split_income_dividends": "11500",
        "split_income_dividends_other_than_eligible": "11500",
        "other_split_income": "40000",
        "split_income_from_foreign_sources": "40000",
        "total_income_from_foreign_sources": "50000",
        "split_income_non_business_from_foreign_sources": "40000",
        "total_non_business_income_from_foreign_sources": "50000",
        "t4_security_options_boxes_39_and_91": "1000000",
    }
    inputs.update(overrides)
    return compute("0", (), "0", "0", "0", "0", "0", **inputs)


def test_line_27_is_the_return_s_line_41700_which_carries_the_minimum_tax() -> None:
    worksheet = return_ma()

    # T691 Part 6 line 14 (the more of line 12 and T1206 line 24) is entered on line 41700 of the
    # return, and T1206 lines 25 to 27 are printed as the return's line 41700: 155940.57, not the
    # 2016.42 of line 40600 less line 41600.
    assert worksheet.get(AMT_FEDERAL_TAX_PAYABLE_UNDER_MINIMUM_TAX).value == D("155940.57")
    assert worksheet.get(FEDERAL_TAX_LINE_41700).value == D("155940.57")
    assert worksheet.get(FEDERAL_TAX_LESS_CREDITS).value == D("2016.42")
    assert worksheet.get(SPLIT_INCOME_LINE_29).value == D("155940.57")


def test_the_minimum_tax_is_in_the_net_federal_tax_not_dropped_by_line_30() -> None:
    worksheet = return_ma()

    # Line 30 is the more of line 24 (5330.85) and line 29 (155940.57). Read literally, line 27 is
    # 2016.42, line 29 is 2016.42, line 30 is line 24 and the net federal tax is 5330.85: 150609.72
    # of minimum tax would be dropped.
    assert worksheet.get(SPLIT_INCOME_LINE_24).value == D("5330.85")
    assert worksheet.get(SPLIT_INCOME_LINE_30).value == D("155940.57")
    assert worksheet.get(NET_FEDERAL_TAX).value == D("155940.57")
    literal_line_30 = max(
        worksheet.get(SPLIT_INCOME_LINE_24).value, worksheet.get(FEDERAL_TAX_LESS_CREDITS).value
    )
    assert literal_line_30 == D("5330.85")
    assert worksheet.get(NET_FEDERAL_TAX).value - literal_line_30 == D("150609.72")


def test_the_total_payable_and_balance_owing_carry_the_minimum_tax() -> None:
    worksheet = return_ma()

    # Net federal tax 155940.57 + Ontario tax 64481.09.
    assert worksheet.get(TOTAL_PAYABLE).value == D("220421.66")
    assert worksheet.get(REFUND_OR_BALANCE_OWING).value == D("220421.66")


def test_without_the_security_options_line_27_is_the_plain_federal_tax() -> None:
    # No minimum tax payable: line 41700 is line 40600 less line 41600, the same figure the
    # literal reading gives, so the two readings differ only when minimum tax is payable.
    worksheet = return_ma(t4_security_options_boxes_39_and_91="0")

    assert (
        worksheet.get(FEDERAL_TAX_LINE_41700).value == worksheet.get(FEDERAL_TAX_LESS_CREDITS).value
    )
    assert worksheet.get(SPLIT_INCOME_LINE_29).value == worksheet.get(FEDERAL_TAX_LINE_41700).value
