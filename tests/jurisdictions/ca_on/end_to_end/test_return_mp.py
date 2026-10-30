"""CA-ON 2025 end to end: return mp."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import pytest

from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.domain.errors import InputAboveBoundError
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog import (
    BUSINESS_CCA_CLAIM,
    BUSINESS_CLOSING_UCC,
    BUSINESS_FISCAL_PERIOD_DAYS,
    BUSINESS_IMMEDIATE_EXPENSING_LIMIT,
    BUSINESS_NET_INCOME_BEFORE_ADJUSTMENTS,
    CCA_CLASS_NUMBER,
    CCA_UCC_AT_END,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, run

# Return MP: Return CE's sole proprietor with a fiscal period of 12 months that has 366 days
# (1 Feb 2024 to 31 Jan 2025). Guide T4002: "A fiscal period cannot be longer than 12 months"; a
# period "less than 365 days" is prorated, so 366 days is a full year: the Class 8 maximum is
# 3500.00, not 3500.00 x 366 / 365. Gross sales of 40500.00 less 7000 of expenses and the 3500.00
# claim leave 30000.00, as in Return BB.
BUSINESS = {
    "gross_sales": "40500.00",
    "advertising": "1500",
    "insurance": "1200",
    "rent": "4300",
    "vehicle_sales_tax_rate": "13",
}
FROM = 20240201
TO = 20250131


def class_8(
    claim: str,
) -> tuple[str, str, str, str, str, str, str, int, str, str, str]:
    """Area A row as (column 1, column 2, column 3, column 5, column 11, column 12, the claim, no
    property left, column 4, column 6, column 9): Class 8 bought in the year (column 3 35000)."""
    return ("8", "0", "35000", "0", "0", "0", claim, 0, "0", "0", "0")


def run_mp(
    changes: Mapping[str, Any] | None = None, **overrides: Any
) -> dict[str, tuple[Worksheet, ...]]:
    """Return MP's inputs, as in `returns/2025_return_mp.yaml`: one T2125 statement with a fiscal
    period of 366 days and a Class 8 claim of 3500.00."""
    statement: dict[str, Any] = {
        "business": BUSINESS,
        "business_cca_classes_rows": (class_8("3500.00"),),
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


def statement_mp(changes: Mapping[str, Any] | None = None) -> Worksheet:
    """The worksheet of Return MP's one T2125 statement."""
    return run_mp(changes)["ca/t2125"][0]


def test_a_fiscal_period_of_366_days_is_accepted_from_its_dates() -> None:
    statement = statement_mp()
    rendered = EnglishTraceRenderer().render_all(statement.trace)

    assert statement.get(BUSINESS_FISCAL_PERIOD_DAYS).value == 366
    assert (
        "business_fiscal_period_days: from 20240201 to 20250131, fiscal period 366 days" in rendered
    )


def test_a_period_from_29_february_2024_to_28_february_2025_is_366_days_and_accepted() -> None:
    # 29 February 2024 is in the period, and its anniversary, 1 March 2025, is not a day of it: the
    # period ends on 28 February 2025, which is 12 months, so 366 days are accepted as a full year.
    statement = run_mp(
        {"business_fiscal_period_from": 20240229, "business_fiscal_period_to": 20250228}
    )["ca/t2125"][0]
    rendered = EnglishTraceRenderer().render_all(statement.trace)

    assert statement.get(BUSINESS_FISCAL_PERIOD_DAYS).value == 366
    assert statement.get(BUSINESS_CCA_CLAIM).value == D("3500.00")
    assert (
        "business_fiscal_period_days: from 20240229 to 20250228, fiscal period 366 days" in rendered
    )


def test_a_period_from_1_march_2025_to_1_march_2026_is_refused() -> None:
    # 366 days with no 29 February: 1 March 2025 to 1 March 2026 is 12 months and a day, longer
    # than a fiscal period may be (Guide T4002: "A fiscal period cannot be longer than 12 months").
    # The period must end by 28 February 2026.
    with pytest.raises(InputAboveBoundError, match=r"business_fiscal_period_to.*20260301"):
        run_mp({"business_fiscal_period_from": 20250301, "business_fiscal_period_to": 20260301})


def test_a_fiscal_period_of_366_days_is_not_prorated() -> None:
    statement = statement_mp()
    records = statement.get(BUSINESS_CLOSING_UCC).value.records

    assert statement.get(BUSINESS_CCA_CLAIM).value == D("3500.00")
    assert [(r[CCA_CLASS_NUMBER], r[CCA_UCC_AT_END]) for r in records] == [(D("8"), D("31500.00"))]
    assert statement.get(BUSINESS_NET_INCOME_BEFORE_ADJUSTMENTS).value == D("30000.00")
    assert statement.get(BUSINESS_IMMEDIATE_EXPENSING_LIMIT).value == D("1500000")


def test_a_claim_above_the_unprorated_maximum_is_refused() -> None:
    with pytest.raises(InputAboveBoundError):
        statement_mp({"business_cca_classes_rows": (class_8("3500.01"),)})


def test_more_than_12_months_is_refused() -> None:
    # 1 February 2024 to 1 February 2025 is 367 days (the 29 February of 2024 included): the period
    # must end by 31 January 2025.
    with pytest.raises(InputAboveBoundError, match=r"business_fiscal_period_to.*20250201"):
        run_mp({"business_fiscal_period_from": 20240201, "business_fiscal_period_to": 20250201})
