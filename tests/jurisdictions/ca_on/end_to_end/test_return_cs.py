"""CA-ON 2025 end to end: return cs."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import pytest

from tax_calculator.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_calculator.domain.errors import InvalidRecordError
from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.catalog import (
    BUSINESS_CCA_CLAIM,
    BUSINESS_CCA_TABLE_CLAIM,
    BUSINESS_CLOSING_UCC,
    BUSINESS_RECAPTURED_CCA,
    BUSINESS_TERMINAL_LOSS,
    CCA_CLASS_NUMBER,
    CCA_UCC_AT_END,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, run

# Return CE's T2125: gross sales of 39052.05 (a chosen figure, so that line 9369 is 30000.00, as is
# Return BB's line 9946) and the three expense lines 1500 + 1200 + 4300 = 7000, with no motor
# vehicle (no Charts A to C) and no business-use-of-home expenses. The business started on June 1,
# 2025, so its first fiscal period, June 1 to December 31, 2025, is 214 days (Guide T4002, "You
# were asking?").
BUSINESS = {
    "gross_sales": "39052.05",
    "advertising": "1500",
    "insurance": "1200",
    "rent": "4300",
    "vehicle_sales_tax_rate": "13",
}
FROM = 20250601
TO = 20251231


def class_row(
    personal_part: str = "5000.00", claim: str = "2052.05"
) -> tuple[str, str, str, str, str, str, str, int, str, str, str, int, str]:
    """Area A row as (column 1, column 2, column 3, column 5, column 11, column 12, the claim, no
    property left, column 4, column 6, column 9, the half-year rule flag (0), endnote 9's remaining
    personal part): Return CE's Class 8 bought in the year (column 3 35000, nothing at the start),
    so column 7 is 35000.00, with the given remaining personal part of the property's cost."""
    return ("8", "0", "35000", "0", "0", "0", claim, 0, "0", "0", "0", 0, personal_part)


def run_cs(
    changes: Mapping[str, Any] | None = None, personal_part: str = "5000.00", **overrides: Any
) -> dict[str, tuple[Worksheet, ...]]:
    """Return CS's inputs, as in `returns/2025_return_cs.yaml`: Return CE's T2125 with a
    remaining personal part of 5000.00 on its one class (endnote 9)."""
    statement: dict[str, Any] = {
        "business": BUSINESS,
        "business_cca_classes_rows": (class_row(personal_part),),
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


def statement_cs(
    changes: Mapping[str, Any] | None = None, personal_part: str = "5000.00"
) -> Worksheet:
    """The worksheet of Return CS's one T2125 statement: its lines, as the form computes them."""
    return run_cs(changes, personal_part)["ca/t2125"][0]


def closing(statement: Worksheet) -> list[tuple[Any, Any]]:
    records = statement.get(BUSINESS_CLOSING_UCC).value.records
    return [(record[CCA_CLASS_NUMBER], record[CCA_UCC_AT_END]) for record in records]


def test_return_css_class_8_closes_at_27947_95_after_the_remaining_personal_part() -> None:
    # Column 22 is column 7 less column 21 (35000.00 - 2052.05 = 32947.95), less the remaining
    # personal part of the property's cost (endnote 9): 32947.95 - 5000.00 = 27947.95.
    statement = statement_cs()

    assert closing(statement) == [(D("8"), D("27947.95"))]


def test_return_css_trace_names_the_remaining_personal_part() -> None:
    rendered = EnglishTraceRenderer().render_all(statement_cs().trace)

    assert (
        "business_closing_ucc: item 1 class 8: column 7 35000 less claim 2052.05 "
        "(prorated 214/365) less personal part 5000 = 27947.95"
    ) in rendered


def test_return_css_personal_part_does_not_change_the_claim_or_the_form_lines() -> None:
    # Endnote 9 changes only column 22: the claim (column 21), the recapture, the terminal loss
    # and the income lines are Return CE's.
    with_part = statement_cs()
    without = statement_cs(personal_part="0")

    assert with_part.get(BUSINESS_CCA_TABLE_CLAIM).value == D("2052.05")
    assert with_part.get(BUSINESS_CCA_CLAIM).value == without.get(BUSINESS_CCA_CLAIM).value
    assert with_part.get(BUSINESS_RECAPTURED_CCA).value == D("0")
    assert with_part.get(BUSINESS_TERMINAL_LOSS).value == D("0")
    assert closing(without) == [(D("8"), D("32947.95"))]


def test_a_remaining_personal_part_above_column_7_less_the_claim_is_refused() -> None:
    # 32947.95 is column 7 less the claim, so a part of 32947.96 is refused.
    with pytest.raises(InvalidRecordError, match="item 1: personal part"):
        statement_cs(personal_part="32947.96")
