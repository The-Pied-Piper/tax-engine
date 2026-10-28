"""CA-ON 2025 end to end: return cu."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import pytest

from tax_calculator.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_calculator.domain.errors import InvalidRecordError
from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.catalog import (
    CCA_CLASS_NUMBER,
    CCA_UCC_AT_END,
    FISH_CCA_CLAIM,
    FISH_CCA_TABLE_CLAIM,
    FISH_CLOSING_UCC,
    FISH_RECAPTURED_CCA,
    FISH_TERMINAL_LOSS,
)
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


def class_row(
    personal_part: str = "5000.00", claim: str = "958.90"
) -> tuple[str, str, str, str, str, str, str, int, str, str, str, str]:
    """Area A row as (column 1, column 2, column 3, column 5, column 11, column 12, the claim, no
    property left, column 4, column 6, column 9, endnote 9's remaining personal part): Return
    CH's Class 8 bought in the year (column 3 35000, nothing at the start), so column 7 is
    35000.00, with the given remaining personal part of the property's cost."""
    return ("8", "0", "35000", "0", "0", "0", claim, 0, "0", "0", "0", personal_part)


def run_cu(
    changes: Mapping[str, Any] | None = None, personal_part: str = "5000.00", **overrides: Any
) -> dict[str, tuple[Worksheet, ...]]:
    """Return CU's inputs, as in `returns/2025_return_cu.yaml`: Return CH's T2121 with a
    remaining personal part of 5000.00 on its one class (endnote 9)."""
    statement: dict[str, Any] = {
        "fish": FISH,
        "fish_cca_classes_rows": (class_row(personal_part),),
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


def statement_cu(
    changes: Mapping[str, Any] | None = None, personal_part: str = "5000.00"
) -> Worksheet:
    """The worksheet of Return CU's one T2121 statement: its lines, as the form computes them."""
    return run_cu(changes, personal_part)["ca/t2121"][0]


def closing(statement: Worksheet) -> list[tuple[Any, Any]]:
    records = statement.get(FISH_CLOSING_UCC).value.records
    return [(record[CCA_CLASS_NUMBER], record[CCA_UCC_AT_END]) for record in records]


def test_return_cus_class_8_closes_at_29041_10_after_the_remaining_personal_part() -> None:
    # Column 22 is column 7 less column 21 (35000.00 - 958.90 = 34041.10), less the remaining
    # personal part of the property's cost (endnote 9): 34041.10 - 5000.00 = 29041.10.
    statement = statement_cu()

    assert closing(statement) == [(D("8"), D("29041.10"))]


def test_return_cus_trace_names_the_remaining_personal_part() -> None:
    rendered = EnglishTraceRenderer().render_all(statement_cu().trace)

    assert (
        "fish_closing_ucc: item 1 class 8: column 7 35000 less claim 958.9 "
        "(prorated 100/365) less personal part 5000 = 29041.1"
    ) in rendered


def test_return_cus_personal_part_does_not_change_the_claim_or_the_form_lines() -> None:
    # Endnote 9 changes only column 22: the claim (column 21), the recapture, the terminal loss
    # and the income lines are Return CH's.
    with_part = statement_cu()
    without = statement_cu(personal_part="0")

    assert with_part.get(FISH_CCA_TABLE_CLAIM).value == D("958.90")
    assert with_part.get(FISH_CCA_CLAIM).value == without.get(FISH_CCA_CLAIM).value
    assert with_part.get(FISH_RECAPTURED_CCA).value == D("0")
    assert with_part.get(FISH_TERMINAL_LOSS).value == D("0")
    assert closing(without) == [(D("8"), D("34041.10"))]


def test_a_remaining_personal_part_above_column_7_less_the_claim_is_refused() -> None:
    # 34041.10 is column 7 less the claim, so a part of 34041.11 is refused.
    with pytest.raises(InvalidRecordError, match="item 1: personal part"):
        statement_cu(personal_part="34041.11")
