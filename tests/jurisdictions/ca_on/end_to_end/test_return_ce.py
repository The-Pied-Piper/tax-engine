"""CA-ON 2025 end to end: return ce."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import pytest

from tax_calculator.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_calculator.domain.errors import InputAboveBoundError
from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.catalog import (
    BUSINESS_CCA_CLAIM,
    BUSINESS_CCA_TABLE_CLAIM,
    BUSINESS_CLOSING_UCC,
    BUSINESS_FISCAL_PERIOD_DAYS,
    BUSINESS_GROSS_INCOME_BEFORE_EXPENSES,
    BUSINESS_IMMEDIATE_EXPENSING_CLAIM,
    BUSINESS_INCOME,
    BUSINESS_INCOME_BEFORE_CCA,
    BUSINESS_NET_INCOME_BEFORE_ADJUSTMENTS,
    BUSINESS_RECAPTURED_CCA,
    BUSINESS_TERMINAL_LOSS,
    BUSINESS_TOTAL_EXPENSES,
    CCA_CLASS_NUMBER,
    CCA_UCC_AT_END,
    FEDERAL_BASIC_TAX,
    NET_INCOME,
    NET_SELF_EMPLOYMENT_INCOME,
    REFUND_OR_BALANCE_OWING,
    TAXABLE_INCOME,
    TOTAL_INCOME,
    TOTAL_PAYABLE,
)
from tax_calculator.jurisdictions.ca_on.catalog import ONTARIO_BASIC_TAX
from tests.jurisdictions.ca_on.end_to_end.support import D, run

# Return CE's T2125: gross sales of 39052.05 (a chosen figure, so that line 9369 is 30000.00, as is
# Return BB's line 9946) and the three expense lines 1500 + 1200 + 4300 = 7000, with no motor
# vehicle (no Charts A to C) and no business-use-of-home expenses. The business started on June 1,
# 2025, so its first fiscal period, June 1 to December 31, 2025, is 214 days (Guide T4002, "You
# were asking?"), entered on the T2125 as its From and to dates.
BUSINESS = {
    "gross_sales": "39052.05",
    "advertising": "1500",
    "insurance": "1200",
    "rent": "4300",
    "vehicle_sales_tax_rate": "13",
}
FROM = 20250601
TO = 20251231


def new_class_8(
    claim: str, additions: str = "35000"
) -> tuple[str, str, str, str, str, str, str, int, str, str, str]:
    """Area A row as (column 1, column 2, column 3, column 5, column 11, column 12, the claim, no
    property left, column 4, column 6, column 9): Return CE's Class 8 bought in the year (column 3
    35000, nothing at the start), so column 7 is 35000.00."""
    return ("8", "0", additions, "0", "0", "0", claim, 0, "0", "0", "0")


def run_ce(
    changes: Mapping[str, Any] | None = None, **overrides: Any
) -> dict[str, tuple[Worksheet, ...]]:
    """Return CE's inputs, as in `returns/2025_return_ce.yaml`: a sole proprietor whose first
    fiscal period is 214 days, from 1 June to 31 December 2025.

    One T2125 statement for the business: gross sales of 39052.05 (amount 3A, and so line 8299 and
    T1 line 13499), expenses of 7000 on three lines and 2052.05 of capital cost allowance (Class
    8, additions 35000, a fiscal period of 214 days, claim 2052.05), 9052.05 in all (line 9368), so
    line 9369 is 30000.00; no business-use-of-home expenses, so line 9946 and T1 line 13500 are
    30000.00, Return BB's.
    """
    statement: dict[str, Any] = {
        "business": BUSINESS,
        "business_cca_classes_rows": (new_class_8("2052.05"),),
        "business_fiscal_period_from": FROM,
        "business_fiscal_period_to": TO,
    }
    return run(
        "0",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        business_statements=({**statement, **(changes or {})},),
        **overrides,
    )


def statement_ce(changes: Mapping[str, Any] | None = None) -> Worksheet:
    """The worksheet of Return CE's one T2125 statement: its lines, as the form computes them."""
    return run_ce(changes)["ca/t2125"][0]


def closing(statement: Worksheet) -> list[tuple[Any, Any]]:
    records = statement.get(BUSINESS_CLOSING_UCC).value.records
    return [(record[CCA_CLASS_NUMBER], record[CCA_UCC_AT_END]) for record in records]


def test_return_ces_fiscal_period_is_the_214_days_from_its_dates() -> None:
    # Guide T4002 "You were asking?": a first fiscal period from June 1, 2025, to December 31, 2025
    # is 214 days (30 + 31 + 31 + 30 + 31 + 30 + 31); the caller enters the two dates.
    statement = statement_ce()
    rendered = EnglishTraceRenderer().render_all(statement.trace)

    assert statement.get(BUSINESS_FISCAL_PERIOD_DAYS).value == 214
    assert (
        "business_fiscal_period_days: from 20250601 to 20251231, fiscal period 214 days" in rendered
    )


def test_return_ces_class_8_maximum_is_prorated_to_2052_05() -> None:
    # Area A, Class 8 (20%): column 7 is 0 + 35000.00 - 0 = 35000.00; columns 4, 6, 8, 9, 11, 12,
    # 14, 15, 16 and 17 are 0, column 10 is 35000.00 and column 13 is 35000.00. The half-year rule
    # makes column 18 50% of 35000.00, 17500.00, and column 19 is 35000.00 - 17500.00 = 17500.00.
    # The maximum of a full year is 17500.00 x 20% = 3500.00 (the Guide's $3,500); for 214 days it
    # is 3500.00 x 214 / 365 = 749000 / 365 = 2052.0547..., rounded half-up to the cent, 2052.05
    # (the Guide prints $2,052). Column 21 is the claim, 2052.05.
    statement = statement_ce()
    rendered = EnglishTraceRenderer().render_all(statement.trace)

    assert (
        "business_cca_table_claim: item 1 class 8: column 7 35000, column 14 0, "
        "column 15 0, column 16 0, column 17 0, column 18 17500, column 19 17500, "
        "maximum 20% of column 19 = 3500 (half-up to 0.01), prorated 214/365 = 2052.05, "
        "claim 2052.05"
    ) in rendered
    assert statement.get(BUSINESS_CCA_TABLE_CLAIM).value == D("2052.05")


def test_return_ces_closing_ucc_is_32947_95() -> None:
    # Column 22 is column 7 less column 21: 35000.00 - 2052.05 = 32947.95, next year's column 2.
    statement = statement_ce()

    assert closing(statement) == [(D("8"), D("32947.95"))]
    rendered = EnglishTraceRenderer().render_all(statement.trace)
    assert (
        "business_closing_ucc: item 1 class 8: column 7 35000 less claim 2052.05 "
        "(prorated 214/365) = 32947.95"
    ) in rendered


def test_return_ces_class_has_no_recapture_and_no_terminal_loss() -> None:
    # Column 7 is positive and property is left in the class (no property left is 0).
    statement = statement_ce()

    assert statement.get(BUSINESS_RECAPTURED_CCA).value == D("0")
    assert statement.get(BUSINESS_TERMINAL_LOSS).value == D("0")


def test_return_ces_line_9936_is_2052_05_and_line_9369_is_30000() -> None:
    # Line ii, the total of column 21, is 2052.05, so is line 9936 (no personal part of CCA, no CCA
    # for business-use-of-home expenses). Line 9368 is 7000 + 2052.05 + 0 = 9052.05 and line 9369
    # is 39052.05 - 9052.05 = 30000.00.
    statement = statement_ce()

    assert statement.get(BUSINESS_GROSS_INCOME_BEFORE_EXPENSES).value == D("39052.05")
    assert statement.get(BUSINESS_CCA_CLAIM).value == D("2052.05")
    assert statement.get(BUSINESS_TOTAL_EXPENSES).value == D("9052.05")
    assert statement.get(BUSINESS_NET_INCOME_BEFORE_ADJUSTMENTS).value == D("30000.00")
    assert statement.get(BUSINESS_IMMEDIATE_EXPENSING_CLAIM).value == D("0")
    assert statement.get(BUSINESS_INCOME_BEFORE_CCA).value == D("32052.05")


def test_return_ces_net_business_income_is_30000_on_line_9946_and_t1_line_13500() -> None:
    # Part 7: no business-use-of-home expenses (0), so line 9946 is 30000.00 - 0 = 30000.00, T1
    # line 22 and line 13500; the net self-employment income (line 27) is 30000.00 + 0 + 0 + 0 +
    # 0.
    result = run_ce()
    worksheet = result["ca-on/return"][0]

    assert result["ca/t2125"][0].get(BUSINESS_INCOME).value == D("30000.00")
    assert worksheet.get(BUSINESS_INCOME).value == D("30000.00")
    assert worksheet.get(NET_SELF_EMPLOYMENT_INCOME).value == D("30000.00")


def test_return_ces_figures_that_depend_on_income_are_return_bbs() -> None:
    # Line 9946 is Return BB's 30000.00, so total income, net income and taxable income are
    # 30000.00 and the tax lines are Return BB's: the federal tax 30000.00 x 14.5% = 4350.00, the
    # Ontario tax 30000.00 x 5.05% = 1515.00 and the total payable 3182.57.
    worksheet = run_ce()["ca-on/return"][0]

    assert worksheet.get(TOTAL_INCOME).value == D("30000.00")
    assert worksheet.get(NET_INCOME).value == D("30000.00")
    assert worksheet.get(TAXABLE_INCOME).value == D("30000.00")
    assert worksheet.get(FEDERAL_BASIC_TAX).value == D("4350.00")
    assert worksheet.get(ONTARIO_BASIC_TAX).value == D("1515.00")
    assert worksheet.get(TOTAL_PAYABLE).value == D("3182.57")
    # The Canada workers benefit of 1161.25 (1633.00 less 471.75, which is 15% of 30000.00
    # over 26855.00) is a refund against the total payable of 3182.57: 2021.32 owing.
    assert worksheet.get(REFUND_OR_BALANCE_OWING).value == D("2021.32")


def test_a_claim_below_the_prorated_maximum_leaves_the_rest_in_the_closing_ucc() -> None:
    # A claim of 2000.00: line 9936 is 2000.00, line 9368 is 7000 + 2000.00 = 9000.00, line 9369
    # is 39052.05 - 9000.00 = 30052.05; column 22 is 35000.00 - 2000.00 = 33000.00.
    statement = statement_ce({"business_cca_classes_rows": (new_class_8("2000.00"),)})

    assert statement.get(BUSINESS_NET_INCOME_BEFORE_ADJUSTMENTS).value == D("30052.05")
    assert closing(statement) == [(D("8"), D("33000.00"))]


def test_a_claim_above_2052_05_is_refused() -> None:
    # The prorated maximum is 2052.05; a claim of 2052.06 is one cent more.
    with pytest.raises(InputAboveBoundError) as raised:
        run_ce({"business_cca_classes_rows": (new_class_8("2052.06"),)})

    assert str(raised.value) == (
        "ca/t2125, instance 1: item 1: ca/cca_claimed 2052.06 is above the maximum 2052.05"
    )


def test_a_claim_of_the_unprorated_3500_is_refused_for_a_short_fiscal_period() -> None:
    # Without the proration the maximum would be 3500.00 (column 19 x 20%).
    with pytest.raises(InputAboveBoundError) as raised:
        run_ce({"business_cca_classes_rows": (new_class_8("3500.00"),)})

    assert str(raised.value) == (
        "ca/t2125, instance 1: item 1: ca/cca_claimed 3500.00 is above the maximum 2052.05"
    )


def test_no_days_entered_is_a_full_year_and_is_not_prorated() -> None:
    # No dates entered (0 and 0): a full fiscal period of 365 days, so the maximum is 3500.00 and
    # column 22 is 35000.00 - 3500.00 = 31500.00; line 9368 is 7000 + 3500.00 = 10500.00 and line
    # 9369 is 39052.05 - 10500.00 = 28552.05.
    changes = {
        "business_fiscal_period_from": 0,
        "business_fiscal_period_to": 0,
        "business_cca_classes_rows": (new_class_8("3500.00"),),
    }
    statement = statement_ce(changes)
    rendered = EnglishTraceRenderer().render_all(statement.trace)

    assert statement.get(BUSINESS_FISCAL_PERIOD_DAYS).value == 365
    assert "business_fiscal_period_days: no dates entered, a full year of 365 days" in rendered
    assert statement.get(BUSINESS_CCA_TABLE_CLAIM).value == D("3500.00")
    assert statement.get(BUSINESS_NET_INCOME_BEFORE_ADJUSTMENTS).value == D("28552.05")
    assert closing(statement) == [(D("8"), D("31500.00"))]
    assert "prorated" not in rendered
    with pytest.raises(InputAboveBoundError) as raised:
        run_ce({**changes, "business_cca_classes_rows": (new_class_8("3500.01"),)})
    assert str(raised.value) == (
        "ca/t2125, instance 1: item 1: ca/cca_claimed 3500.01 is above the maximum 3500.00"
    )


def test_365_days_from_its_dates_are_the_same_as_none_entered() -> None:
    changes = {"business_cca_classes_rows": (new_class_8("3500.00"),)}

    entered = statement_ce(
        {
            **changes,
            "business_fiscal_period_from": 20250101,
            "business_fiscal_period_to": 20251231,
        }
    )
    blank = statement_ce(
        {**changes, "business_fiscal_period_from": 0, "business_fiscal_period_to": 0}
    )

    assert entered.get(BUSINESS_CCA_TABLE_CLAIM).value == blank.get(BUSINESS_CCA_TABLE_CLAIM).value
    assert closing(entered) == closing(blank) == [(D("8"), D("31500.00"))]
    rendered = EnglishTraceRenderer().render_all(entered.trace)
    assert (
        "business_fiscal_period_days: from 20250101 to 20251231, fiscal period 365 days" in rendered
    )
    assert "prorated" not in rendered


def test_one_day_gives_one_365th_of_the_maximum() -> None:
    # 3500.00 / 365 = 9.5890..., rounded half-up to the cent, 9.59; column 22 is 35000.00 - 9.59 =
    # 34990.41.
    changes = {"business_fiscal_period_from": 20250101, "business_fiscal_period_to": 20250101}
    statement = statement_ce({**changes, "business_cca_classes_rows": (new_class_8("9.59"),)})

    assert statement.get(BUSINESS_CCA_TABLE_CLAIM).value == D("9.59")
    assert closing(statement) == [(D("8"), D("34990.41"))]
    with pytest.raises(InputAboveBoundError) as raised:
        statement_ce({**changes, "business_cca_classes_rows": (new_class_8("9.60"),)})
    assert str(raised.value) == (
        "ca/t2125, instance 1: item 1: ca/cca_claimed 9.60 is above the maximum 9.59"
    )


@pytest.mark.parametrize("to", [20260102, 20260204])
def test_more_days_than_12_months_are_refused(to: int) -> None:
    # A fiscal period is at most 12 months: from 1 January 2025 it must end by 31 December 2025, so
    # the 367 days to 2 January 2026 and the 400 days to 4 February 2026 are refused, naming the end
    # date.
    with pytest.raises(InputAboveBoundError, match=rf"business_fiscal_period_to.*{to}") as raised:
        run_ce({"business_fiscal_period_from": 20250101, "business_fiscal_period_to": to})

    assert str(raised.value).startswith("ca/t2125, instance 1: ")
