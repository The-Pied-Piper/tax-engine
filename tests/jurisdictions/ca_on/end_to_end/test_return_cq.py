"""CA-ON 2025 end to end: return cq."""

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
    NET_RENTAL_INCOME,
    REFUND_OR_BALANCE_OWING,
    RENTAL_CCA_CLAIM,
    RENTAL_CCA_LIMIT,
    RENTAL_CCA_TABLE_CLAIM,
    RENTAL_CLOSING_UCC,
    RENTAL_FISCAL_PERIOD_DAYS,
    RENTAL_NET_INCOME_AFTER_CCA,
    TOTAL_INCOME,
)
from tax_calculator.jurisdictions.ca_on.catalog import ONTARIO_BASIC_TAX
from tests.jurisdictions.ca_on.end_to_end.support import D, rental_return

# Return CQ's one Area A class: Class 1 (4%), the building bought on July 1, 2025, with additions
# (column 3) of 300000 and nothing at the start, so column 7 is 300000.00. Its claim (column 23) is
# 3024.66, the prorated maximum (see the tests). As the other rows of these tests: column 1, column
# 2, column 3, column 5, column 11, column 12, the claim, no property left, column 4, column 6,
# column 9 and the personal part remaining.
BUILDING = ("1", "0", "300000", "0", "0", "0", "3024.66", 0, "0", "0", "0", "0")

# Return CQ's fiscal period: from July 1 to December 31, 2025, 184 days (T776 Part 1, "Fiscal period
# from Date (Year/Month/Day) to (Year/12/31)"), entered by the caller.
DAYS = 184

# Return CQ's rental: one property with one unit and gross rents for all units of 12000 (line
# 8141), and two expenses, insurance (line 8690) 600 and property taxes (line 9180) 375.34, so
# amount A and line 1 are 975.34 (no personal or short-term portion), and line 9369 is
# 12000 - 975.34 = 11024.66.
RETURN_CQ_STATEMENT: dict[str, Any] = {
    "rental_properties": ((1, "0", "12000"),),
    "rental_expenses": {
        "insurance": ("600", "0", "0"),
        "property_taxes": ("375.34", "0", "0"),
    },
    "rental_cca_classes_rows": (BUILDING,),
    "rental_fiscal_period_days_entered": DAYS,
}


def run_cq(
    changes: Mapping[str, Any] | None = None, **overrides: Any
) -> dict[str, tuple[Worksheet, ...]]:
    """Return CQ's inputs, as in `returns/2025_return_cq.yaml`: a single filer whose only income is
    one rental of a building bought on July 1, 2025, reported on one Form T776 statement for a
    fiscal period of 184 days.

    Gross rents of 12000, expenses of 975.34 and the Class 1 claim of 3024.66: line 9946, and so T1
    line 12600, is 12000 - 975.34 - 3024.66 = 8000.00, Return BS's, so the return's other figures
    are Return BS's.
    """
    return rental_return(RETURN_CQ_STATEMENT, changes, **overrides)


def statement_cq(changes: Mapping[str, Any] | None = None) -> Worksheet:
    """The worksheet of Return CQ's one T776 statement: its lines, as the form computes them."""
    return run_cq(changes)["ca/t776"][0]


def closing(statement: Worksheet) -> list[tuple[Any, Any]]:
    records = statement.get(RENTAL_CLOSING_UCC).value.records
    return [(record[CCA_CLASS_NUMBER], record[CCA_UCC_AT_END]) for record in records]


def test_return_cqs_fiscal_period_is_the_184_days_entered() -> None:
    # T776 Part 1 "Fiscal period": from July 1, 2025 to December 31, 2025 is 184 days (July 31 +
    # August 31 + September 30 + October 31 + November 30 + December 31 = 184); the caller enters
    # them, and the form derives the days the CCA is prorated by.
    statement = statement_cq()
    rendered = EnglishTraceRenderer().render_all(statement.trace)

    assert statement.get(RENTAL_FISCAL_PERIOD_DAYS).value == 184
    assert "rental_fiscal_period_days: entered 184, fiscal period 184 days" in rendered


def test_the_class_1_maximum_is_prorated_to_3024_66() -> None:
    # Area A, Class 1 (4%): column 7 is 0 + 300000 - 0 = 300000.00; the half-year rule takes one
    # half of the additions, so column 18 is 150000.00 and column 19 is 300000.00 - 150000.00 =
    # 150000.00. The maximum of a full year is 150000.00 x 4% = 6000.00; for 184 days it is
    # 6000.00 x 184 / 365 = 1104000 / 365 = 3024.6575..., rounded half-up to the cent, 3024.66,
    # which is claimed in full (column 23).
    statement = statement_cq()
    rendered = EnglishTraceRenderer().render_all(statement.trace)

    assert (
        "rental_cca_table_claim: item 1 class 1: column 7 300000, column 14 0, "
        "column 15 0, column 16 0, column 17 0, column 18 150000, column 19 150000, "
        "maximum 4% of column 19 = 6000 (half-up to 0.01), prorated 184/365 = 3024.66, "
        "claim 3024.66"
    ) in rendered
    assert statement.get(RENTAL_CCA_TABLE_CLAIM).value == D("3024.66")
    assert statement.get(RENTAL_CCA_CLAIM).value == D("3024.66")


def test_the_closing_ucc_is_296975_34() -> None:
    # Column 24 is column 7 less column 23: 300000.00 - 3024.66 = 296975.34, next year's column 2.
    statement = statement_cq()

    assert closing(statement) == [(D("1"), D("296975.34"))]
    rendered = EnglishTraceRenderer().render_all(statement.trace)
    assert (
        "rental_closing_ucc: item 1 class 1: column 7 300000 less claim 3024.66 "
        "(prorated 184/365) = 296975.34"
    ) in rendered


def test_line_9946_and_t1_line_12600_are_8000_which_is_return_bss() -> None:
    # Line 9369 is 12000.00 - 975.34 = 11024.66, the CCA limit of the statement; line ii, the total
    # of column 23, is 3024.66, so amount 6 and line 9946 are 11024.66 - 3024.66 = 8000.00, which is
    # T1 line 12600 and the whole of total income (line 15000).
    result = run_cq()
    statement = result["ca/t776"][0]
    worksheet = result["ca-on/return"][0]

    assert statement.get(RENTAL_CCA_LIMIT).value == D("11024.66")
    assert statement.get(RENTAL_NET_INCOME_AFTER_CCA).value == D("8000.00")
    assert worksheet.get(NET_RENTAL_INCOME).value == D("8000.00")
    assert worksheet.get(TOTAL_INCOME).value == D("8000.00")


def test_the_tax_on_8000_is_nil_as_on_return_bs() -> None:
    # The federal tax on 8000.00 is 8000.00 x 14.5% = 1160.00, less than the non-refundable credits
    # (2338.71), and the Ontario tax is 8000.00 x 5.05% = 404.00, less than 643.72, so the tax is
    # covered by the credits and the refund or balance owing is 0, as Return BS's.
    worksheet = run_cq()["ca-on/return"][0]

    assert worksheet.get(FEDERAL_BASIC_TAX).value == D("1160.00")
    assert worksheet.get(ONTARIO_BASIC_TAX).value == D("404.00")
    assert worksheet.get(REFUND_OR_BALANCE_OWING).value == D("0")


def test_zero_days_and_365_days_give_the_same_figures() -> None:
    # Both are a full fiscal period, so nothing is prorated: the maximum of the class is 6000.00
    # (150000.00 x 4%), claimed in full, column 24 is 300000.00 - 6000.00 = 294000.00 and line 9946
    # is 12000.00 - 975.34 - 6000.00 = 5024.66.
    changes = {
        "rental_cca_classes_rows": (
            ("1", "0", "300000", "0", "0", "0", "6000.00", 0, "0", "0", "0", "0"),
        )
    }

    blank = statement_cq({**changes, "rental_fiscal_period_days_entered": 0})
    entered = statement_cq({**changes, "rental_fiscal_period_days_entered": 365})

    assert blank.get(RENTAL_FISCAL_PERIOD_DAYS).value == 365
    assert entered.get(RENTAL_FISCAL_PERIOD_DAYS).value == 365
    assert entered.get(RENTAL_CCA_TABLE_CLAIM).value == blank.get(RENTAL_CCA_TABLE_CLAIM).value
    assert blank.get(RENTAL_CCA_TABLE_CLAIM).value == D("6000.00")
    assert closing(entered) == closing(blank) == [(D("1"), D("294000.00"))]
    assert (
        entered.get(RENTAL_NET_INCOME_AFTER_CCA).value
        == blank.get(RENTAL_NET_INCOME_AFTER_CCA).value
        == D("5024.66")
    )
    rendered = EnglishTraceRenderer().render_all(entered.trace)
    assert "rental_fiscal_period_days: entered 365, fiscal period 365 days" in rendered
    assert "prorated" not in rendered


@pytest.mark.parametrize("claim", ["3024.67", "6000.00"])
def test_a_claim_above_the_prorated_maximum_is_refused(claim: str) -> None:
    # The prorated maximum for 184 days is 3024.66: one cent more is refused, and so is the full
    # year's 6000.00.
    changes = {
        "rental_cca_classes_rows": (
            ("1", "0", "300000", "0", "0", "0", claim, 0, "0", "0", "0", "0"),
        )
    }
    with pytest.raises(InputAboveBoundError) as raised:
        run_cq(changes)

    assert str(raised.value) == (
        f"ca/t776, instance 1: item 1: ca/cca_claimed {claim} is above the maximum 3024.66"
    )


@pytest.mark.parametrize("entered", [367, 400])
def test_more_days_than_the_longest_fiscal_period_are_refused(entered: int) -> None:
    # A fiscal period is at most 12 months, 366 days (the dataset's longest fiscal period).
    with pytest.raises(InputAboveBoundError) as raised:
        run_cq({"rental_fiscal_period_days_entered": entered})

    assert str(raised.value) == (
        f"ca/t776, instance 1: ca/rental_fiscal_period_days_entered {entered} "
        "is above the maximum 366"
    )
