"""CA-ON 2025 end to end: return ch."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import pytest

from tax_calculator.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_calculator.domain.errors import InputAboveBoundError
from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.catalog import (
    CCA_CLASS_NUMBER,
    CCA_UCC_AT_END,
    FEDERAL_BASIC_TAX,
    FISH_CCA_CLAIM,
    FISH_CCA_TABLE_CLAIM,
    FISH_CLOSING_UCC,
    FISH_FISCAL_PERIOD_DAYS,
    FISH_GROSS_INCOME,
    FISH_GROSS_INCOME_BEFORE_EXPENSES,
    FISH_IMMEDIATE_EXPENSING_CLAIM,
    FISH_NET_INCOME_BEFORE_ADJUSTMENTS,
    FISH_RECAPTURED_CCA,
    FISH_TERMINAL_LOSS,
    FISH_TOTAL_EXPENSES,
    FISHING_INCOME,
    NET_INCOME,
    NET_SELF_EMPLOYMENT_INCOME,
    REFUND_OR_BALANCE_OWING,
    TAXABLE_INCOME,
    TOTAL_INCOME,
    TOTAL_PAYABLE,
)
from tax_calculator.jurisdictions.ca_on.catalog import ONTARIO_BASIC_TAX
from tests.jurisdictions.ca_on.end_to_end.support import D, run

# Return CH's T2121, Return BY's with the fish products lowered to 40958.90 (a chosen figure, so
# that line 9946 stays Return BY's 15000) and no DIEP or Area G: income of 40958.90, expenses of
# 25000 (salt, bait and ice 10000 on line 9138, fishing gear 15000 on line 9136), with no partner.
# The business started on September 23, 2025, so its first fiscal period, September 23 to
# December 31, 2025, is 8 + 31 + 30 + 31 = 100 days (Guide T4002, "You were asking?", which has
# 214 days for a start on June 1).
FISH = {
    "fish_products": "40958.90",
    "salt_bait_and_ice": "10000",
    "fishing_gear": "15000",
    "vehicle_sales_tax_rate": "13",
}
DAYS = 100
# Charts A to C for one leased passenger vehicle used for no fishing, as in Return BY.
VEHICLE = {
    "business_kilometres": "0",
    "total_kilometres": "10000",
    "fuel_and_oil": "1000",
    "insurance": "600",
    "maintenance_and_repairs": "200",
    "other_expenses_10": "653",
    "interest_payable": "400",
    "interest_days": "100",
    "lease_charges": "2550",
    "lease_days": "183",
    "list_price": "60000",
}


def new_class_8(
    claim: str, additions: str = "35000"
) -> tuple[str, str, str, str, str, str, str, int, str, str, str]:
    """Area A row as (column 1, column 2, column 3, column 5, column 11, column 12, the claim, no
    property left, column 4, column 6, column 9): Return CH's Class 8 bought in the year (column 3
    35000, nothing at the start), so column 7 is 35000.00."""
    return ("8", "0", additions, "0", "0", "0", claim, 0, "0", "0", "0")


def run_ch(
    changes: Mapping[str, Any] | None = None, **overrides: Any
) -> dict[str, tuple[Worksheet, ...]]:
    """Return CH's inputs, as in `returns/2025_return_ch.yaml`: Return BY's sole proprietor whose
    first fiscal period is 100 days.

    One T2121 statement for the fishing business: income of 40958.90 (line 8299 and T1 line
    14299), expenses of 25000 (4Q) and 958.90 of capital cost allowance (Class 8, additions 35000,
    a fiscal period of 100 days, claim 958.90), 25958.90 in all (line 9368), so line 9369 is
    15000.00, which is line 9946 and T1 line 14300, Return BY's.
    """
    statement: dict[str, Any] = {
        "fish": FISH,
        "fish_cca_classes_rows": (new_class_8("958.90"),),
        "fish_vehicles_rows": (VEHICLE,),
        "fish_fiscal_period_days_entered": DAYS,
    }
    return run(
        "0",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        fish_statements=({**statement, **(changes or {})},),
        **overrides,
    )


def statement_ch(changes: Mapping[str, Any] | None = None) -> Worksheet:
    """The worksheet of Return CH's one T2121 statement: its lines, as the form computes them."""
    return run_ch(changes)["ca/t2121"][0]


def closing(statement: Worksheet) -> list[tuple[Any, Any]]:
    records = statement.get(FISH_CLOSING_UCC).value.records
    return [(record[CCA_CLASS_NUMBER], record[CCA_UCC_AT_END]) for record in records]


def test_return_chs_fiscal_period_is_the_100_days_entered() -> None:
    # September 23 to December 31, 2025: 8 + 31 + 30 + 31 = 100 days; the caller enters them.
    statement = statement_ch()
    rendered = EnglishTraceRenderer().render_all(statement.trace)

    assert statement.get(FISH_FISCAL_PERIOD_DAYS).value == 100
    assert "fish_fiscal_period_days: entered 100, fiscal period 100 days" in rendered


def test_return_chs_class_8_maximum_is_prorated_to_958_90() -> None:
    # Area A, Class 8 (20%): column 7 is 0 + 35000.00 - 0 = 35000.00, column 13 is 35000.00, the
    # half-year rule makes column 18 50% of 35000.00, 17500.00, and column 19 is 35000.00 -
    # 17500.00 = 17500.00. The maximum of a full year is 17500.00 x 20% = 3500.00; for 100 days it
    # is 3500.00 x 100 / 365 = 350000 / 365 = 958.9041..., rounded half-up to the cent, 958.90.
    statement = statement_ch()
    rendered = EnglishTraceRenderer().render_all(statement.trace)

    assert (
        "fish_cca_table_claim: item 1 class 8: column 7 35000, column 14 0, "
        "column 15 0, column 16 0, column 17 0, column 18 17500, column 19 17500, "
        "maximum 20% of column 19 = 3500 (half-up to 0.01), prorated 100/365 = 958.9, "
        "claim 958.9"
    ) in rendered
    assert statement.get(FISH_CCA_TABLE_CLAIM).value == D("958.90")


def test_return_chs_closing_ucc_is_34041_10() -> None:
    # Column 22 is column 7 less column 21: 35000.00 - 958.90 = 34041.10, next year's column 2.
    statement = statement_ch()

    assert closing(statement) == [(D("8"), D("34041.10"))]
    rendered = EnglishTraceRenderer().render_all(statement.trace)
    assert (
        "fish_closing_ucc: item 1 class 8: column 7 35000 less claim 958.9 "
        "(prorated 100/365) = 34041.1"
    ) in rendered


def test_return_chs_class_has_no_recapture_and_no_terminal_loss() -> None:
    statement = statement_ch()

    assert statement.get(FISH_RECAPTURED_CCA).value == D("0")
    assert statement.get(FISH_TERMINAL_LOSS).value == D("0")
    assert statement.get(FISH_IMMEDIATE_EXPENSING_CLAIM).value == D("0")


def test_return_chs_line_9936_is_958_90_and_line_9369_is_15000() -> None:
    # Line ii, the total of column 21, is 958.90, so is line 9936 (no personal part of CCA, no CCA
    # for business-use-of-home expenses). Line 9368 is 25000 + 958.90 = 25958.90 and line 9369 is
    # 40958.90 - 25958.90 = 15000.00.
    statement = statement_ch()

    assert statement.get(FISH_GROSS_INCOME).value == D("40958.90")
    assert statement.get(FISH_GROSS_INCOME_BEFORE_EXPENSES).value == D("40958.90")
    assert statement.get(FISH_CCA_CLAIM).value == D("958.90")
    assert statement.get(FISH_TOTAL_EXPENSES).value == D("25958.90")
    assert statement.get(FISH_NET_INCOME_BEFORE_ADJUSTMENTS).value == D("15000.00")


def test_return_chs_net_fishing_income_is_15000_on_line_9946_and_t1_line_14300() -> None:
    result = run_ch()
    worksheet = result["ca-on/return"][0]

    assert result["ca/t2121"][0].get(FISHING_INCOME).value == D("15000.00")
    assert worksheet.get(FISHING_INCOME).value == D("15000.00")
    assert worksheet.get(NET_SELF_EMPLOYMENT_INCOME).value == D("15000.00")


def test_return_chs_figures_that_depend_on_income_are_return_bys() -> None:
    # Line 9946 is Return BY's 15000.00: the federal tax 15000.00 x 14.5% = 2175.00, the Ontario
    # tax 15000.00 x 5.05% = 757.50, and nothing payable after the credits.
    worksheet = run_ch()["ca-on/return"][0]

    assert worksheet.get(TOTAL_INCOME).value == D("15000.00")
    assert worksheet.get(NET_INCOME).value == D("15000.00")
    assert worksheet.get(TAXABLE_INCOME).value == D("15000.00")
    assert worksheet.get(FEDERAL_BASIC_TAX).value == D("2175.00")
    assert worksheet.get(ONTARIO_BASIC_TAX).value == D("757.50")
    assert worksheet.get(TOTAL_PAYABLE).value == D("0.00")
    # The Canada workers benefit of 1633.00 (27% of the working income over 3000.00 is capped
    # at 1633.00, and the adjusted family net income is under 26855.00) is a refund: the
    # total payable of 0.00 less 1633.00 is -1633.00.
    assert worksheet.get(REFUND_OR_BALANCE_OWING).value == D("-1633.00")


def test_a_claim_above_958_90_is_refused() -> None:
    with pytest.raises(InputAboveBoundError) as raised:
        run_ch({"fish_cca_classes_rows": (new_class_8("958.91"),)})

    assert str(raised.value) == (
        "ca/t2121, instance 1: item 1: ca/cca_claimed 958.91 is above the maximum 958.90"
    )


def test_no_days_entered_is_a_full_year_and_is_not_prorated() -> None:
    # The maximum is 3500.00 and column 22 is 35000.00 - 3500.00 = 31500.00.
    changes = {
        "fish_fiscal_period_days_entered": 0,
        "fish_cca_classes_rows": (new_class_8("3500.00"),),
    }
    statement = statement_ch(changes)
    rendered = EnglishTraceRenderer().render_all(statement.trace)

    assert statement.get(FISH_FISCAL_PERIOD_DAYS).value == 365
    assert "fish_fiscal_period_days: entered 0, a full year of 365 days" in rendered
    assert statement.get(FISH_CCA_TABLE_CLAIM).value == D("3500.00")
    assert closing(statement) == [(D("8"), D("31500.00"))]
    assert "prorated" not in rendered
    with pytest.raises(InputAboveBoundError) as raised:
        run_ch({**changes, "fish_cca_classes_rows": (new_class_8("3500.01"),)})
    assert str(raised.value) == (
        "ca/t2121, instance 1: item 1: ca/cca_claimed 3500.01 is above the maximum 3500.00"
    )


@pytest.mark.parametrize("entered", [367, 400])
def test_more_days_than_the_longest_fiscal_period_are_refused(entered: int) -> None:
    with pytest.raises(InputAboveBoundError) as raised:
        run_ch({"fish_fiscal_period_days_entered": entered})

    assert str(raised.value) == (
        f"ca/t2121, instance 1: ca/fish_fiscal_period_days_entered {entered} "
        "is above the maximum 366"
    )
