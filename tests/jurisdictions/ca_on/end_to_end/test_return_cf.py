"""CA-ON 2025 end to end: return cf."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import pytest

from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.domain.errors import InputAboveBoundError
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog import (
    CCA_CLASS_NUMBER,
    CCA_UCC_AT_END,
    FARM_CCA_CLAIM,
    FARM_CCA_TABLE_CLAIM,
    FARM_CLOSING_UCC,
    FARM_FISCAL_PERIOD_DAYS,
    FARM_GROSS_INCOME,
    FARM_GROSS_INCOME_BEFORE_EXPENSES,
    FARM_IMMEDIATE_EXPENSING_CLAIM,
    FARM_NET_INCOME_BEFORE_ADJUSTMENTS,
    FARM_RECAPTURED_CCA,
    FARM_TERMINAL_LOSS,
    FARM_TOTAL_EXPENSES,
    FARMING_INCOME,
    FEDERAL_BASIC_TAX,
    NET_INCOME,
    NET_SELF_EMPLOYMENT_INCOME,
    REFUND_OR_BALANCE_OWING,
    TAXABLE_INCOME,
    TOTAL_INCOME,
    TOTAL_PAYABLE,
)
from tax_engine.jurisdictions.ca_on.catalog import ONTARIO_BASIC_TAX
from tests.jurisdictions.ca_on.end_to_end.support import D, run

# Return CF's T2042, Return BC's with the wheat raised by 2200.68 to 52200.68 (a chosen figure, so
# that line 9946 stays Return BC's 30000): income lines of 82200.68 (wheat 52200.68 on line 9371,
# cattle 30000 on line 9471) and expenses of 50000 (fertilizers and lime 20000 on line 9662, seeds
# and plants 30000 on line 9664), with no inventory adjustment or partner. The farm started on
# August 1, 2025, so its first fiscal period, August 1 to December 31, 2025, is 153 days (Guide
# T4002, "You were asking?", which has 214 days for a start on June 1).
FARM = {
    "wheat": "52200.68",
    "cattle": "30000",
    "fertilizers_and_lime": "20000",
    "seeds_and_plants": "30000",
    # Charts A to C for one leased passenger vehicle that is used for no farming: business
    # kilometres 0 (amount 1), so line 9819 (amount 16 of Chart A) is 0, as in Return BC.
    "vehicle_sales_tax_rate": "13",
}
DAYS = 153
# Charts A to C for one leased passenger vehicle used for no farming, as in Return BC.
VEHICLE = {
    "business_kilometres": "0",
    "total_kilometres": "10000",
    "fuel_and_oil": "1000",
    "insurance": "600",
    "maintenance_and_repairs": "200",
    "other_expenses_10": "653",
    "interest_payable": "400",
    "interest_days": "153",
    "lease_charges": "2550",
    "lease_days": "183",
    "list_price": "60000",
}


def new_class_10(
    claim: str, additions: str = "35000"
) -> tuple[str, str, str, str, str, str, str, int, str, str, str]:
    """Area A row as (column 1, column 2, column 3, column 5, column 11, column 12, the claim, no
    property left, column 4, column 6, column 9): Return CF's Class 10 bought in the year (column 3
    35000, nothing at the start), so column 7 is 35000.00."""
    return ("10", "0", additions, "0", "0", "0", claim, 0, "0", "0", "0")


def run_cf(
    changes: Mapping[str, Any] | None = None, **overrides: Any
) -> dict[str, tuple[Worksheet, ...]]:
    """Return CF's inputs, as in `returns/2025_return_cf.yaml`: Return BC's sole proprietor whose
    first fiscal period is 153 days.

    One T2042 statement for the farm: income of 82200.68 (line 9659 and T1 line 14099), expenses of
    50000 (4B) and 2200.68 of capital cost allowance (Class 10, additions 35000, a fiscal period
    of 153 days, claim 2200.68), 52200.68 in all (line 9898), so line 9899 and amount 4C are
    30000.00, which is line 9946 and T1 line 14100, Return BC's.
    """
    statement: dict[str, Any] = {
        "farm": FARM,
        "farm_cca_classes_rows": (new_class_10("2200.68"),),
        "farm_vehicles_rows": (VEHICLE,),
        "farm_fiscal_period_days_entered": DAYS,
    }
    return run(
        "0",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        farm_statements=({**statement, **(changes or {})},),
        **overrides,
    )


def statement_cf(changes: Mapping[str, Any] | None = None) -> Worksheet:
    """The worksheet of Return CF's one T2042 statement: its lines, as the form computes them."""
    return run_cf(changes)["ca/t2042"][0]


def closing(statement: Worksheet) -> list[tuple[Any, Any]]:
    records = statement.get(FARM_CLOSING_UCC).value.records
    return [(record[CCA_CLASS_NUMBER], record[CCA_UCC_AT_END]) for record in records]


def test_return_cfs_fiscal_period_is_the_153_days_entered() -> None:
    # August 1 to December 31, 2025: 31 + 30 + 31 + 30 + 31 = 153 days; the caller enters them.
    statement = statement_cf()
    rendered = EnglishTraceRenderer().render_all(statement.trace)

    assert statement.get(FARM_FISCAL_PERIOD_DAYS).value == 153
    assert "farm_fiscal_period_days: entered 153, fiscal period 153 days" in rendered


def test_return_cfs_class_10_maximum_is_prorated_to_2200_68() -> None:
    # Area A, Class 10 (30%): column 7 is 0 + 35000.00 - 0 = 35000.00, column 13 is 35000.00, the
    # half-year rule makes column 18 50% of 35000.00, 17500.00, and column 19 is 35000.00 -
    # 17500.00 = 17500.00. The maximum of a full year is 17500.00 x 30% = 5250.00; for 153 days it
    # is 5250.00 x 153 / 365 = 803250 / 365 = 2200.6849..., rounded half-up to the cent, 2200.68.
    statement = statement_cf()
    rendered = EnglishTraceRenderer().render_all(statement.trace)

    assert (
        "farm_cca_table_claim: item 1 class 10: column 7 35000, column 14 0, "
        "column 15 0, column 16 0, column 17 0, column 18 17500, column 19 17500, "
        "maximum 30% of column 19 = 5250 (half-up to 0.01), prorated 153/365 = 2200.68, "
        "claim 2200.68"
    ) in rendered
    assert statement.get(FARM_CCA_TABLE_CLAIM).value == D("2200.68")


def test_return_cfs_closing_ucc_is_32799_32() -> None:
    # Column 22 is column 7 less column 21: 35000.00 - 2200.68 = 32799.32, next year's column 2.
    statement = statement_cf()

    assert closing(statement) == [(D("10"), D("32799.32"))]
    rendered = EnglishTraceRenderer().render_all(statement.trace)
    assert (
        "farm_closing_ucc: item 1 class 10: column 7 35000 less claim 2200.68 "
        "(prorated 153/365) = 32799.32"
    ) in rendered


def test_return_cfs_class_has_no_recapture_and_no_terminal_loss() -> None:
    statement = statement_cf()

    assert statement.get(FARM_RECAPTURED_CCA).value == D("0")
    assert statement.get(FARM_TERMINAL_LOSS).value == D("0")
    assert statement.get(FARM_IMMEDIATE_EXPENSING_CLAIM).value == D("0")


def test_return_cfs_line_9936_is_2200_68_and_line_9899_is_30000() -> None:
    # Line ii, the total of column 21, is 2200.68, so is line 9936 (no personal part of CCA, no
    # CCA for business-use-of-home expenses). Line 9898 is 50000 + 2200.68 = 52200.68 and line
    # 9899 is 82200.68 - 52200.68 = 30000.00.
    statement = statement_cf()

    assert statement.get(FARM_GROSS_INCOME).value == D("82200.68")
    assert statement.get(FARM_GROSS_INCOME_BEFORE_EXPENSES).value == D("82200.68")
    assert statement.get(FARM_CCA_CLAIM).value == D("2200.68")
    assert statement.get(FARM_TOTAL_EXPENSES).value == D("52200.68")
    assert statement.get(FARM_NET_INCOME_BEFORE_ADJUSTMENTS).value == D("30000.00")


def test_return_cfs_net_farming_income_is_30000_on_line_9946_and_t1_line_14100() -> None:
    result = run_cf()
    worksheet = result["ca-on/return"][0]

    assert result["ca/t2042"][0].get(FARMING_INCOME).value == D("30000.00")
    assert worksheet.get(FARMING_INCOME).value == D("30000.00")
    assert worksheet.get(NET_SELF_EMPLOYMENT_INCOME).value == D("30000.00")


def test_return_cfs_figures_that_depend_on_income_are_return_bcs() -> None:
    # Line 9946 is Return BC's 30000.00: the federal tax 30000.00 x 14.5% = 4350.00, the Ontario
    # tax 30000.00 x 5.05% = 1515.00 and the total payable 3182.57.
    worksheet = run_cf()["ca-on/return"][0]

    assert worksheet.get(TOTAL_INCOME).value == D("30000.00")
    assert worksheet.get(NET_INCOME).value == D("30000.00")
    assert worksheet.get(TAXABLE_INCOME).value == D("30000.00")
    assert worksheet.get(FEDERAL_BASIC_TAX).value == D("4350.00")
    assert worksheet.get(ONTARIO_BASIC_TAX).value == D("1515.00")
    assert worksheet.get(TOTAL_PAYABLE).value == D("3182.57")
    # The Canada workers benefit of 1161.25 (1633.00 less 471.75, which is 15% of 30000.00
    # over 26855.00) is a refund against the total payable of 3182.57: 2021.32 owing.
    assert worksheet.get(REFUND_OR_BALANCE_OWING).value == D("2021.32")


def test_a_claim_above_2200_68_is_refused() -> None:
    with pytest.raises(InputAboveBoundError) as raised:
        run_cf({"farm_cca_classes_rows": (new_class_10("2200.69"),)})

    assert str(raised.value) == (
        "ca/t2042, instance 1: item 1: ca/cca_claimed 2200.69 is above the maximum 2200.68"
    )


def test_no_days_entered_is_a_full_year_and_is_not_prorated() -> None:
    # The maximum is 5250.00 and column 22 is 35000.00 - 5250.00 = 29750.00.
    changes = {
        "farm_fiscal_period_days_entered": 0,
        "farm_cca_classes_rows": (new_class_10("5250.00"),),
    }
    statement = statement_cf(changes)
    rendered = EnglishTraceRenderer().render_all(statement.trace)

    assert statement.get(FARM_FISCAL_PERIOD_DAYS).value == 365
    assert "farm_fiscal_period_days: entered 0, a full year of 365 days" in rendered
    assert statement.get(FARM_CCA_TABLE_CLAIM).value == D("5250.00")
    assert closing(statement) == [(D("10"), D("29750.00"))]
    assert "prorated" not in rendered
    with pytest.raises(InputAboveBoundError) as raised:
        run_cf({**changes, "farm_cca_classes_rows": (new_class_10("5250.01"),)})
    assert str(raised.value) == (
        "ca/t2042, instance 1: item 1: ca/cca_claimed 5250.01 is above the maximum 5250.00"
    )


@pytest.mark.parametrize("entered", [367, 400])
def test_more_days_than_the_longest_fiscal_period_are_refused(entered: int) -> None:
    with pytest.raises(InputAboveBoundError) as raised:
        run_cf({"farm_fiscal_period_days_entered": entered})

    assert str(raised.value) == (
        f"ca/t2042, instance 1: ca/farm_fiscal_period_days_entered {entered} "
        "is above the maximum 366"
    )
