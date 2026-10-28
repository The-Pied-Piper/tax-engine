"""CA-ON 2025 end to end: return kx (Guide T4002's Cathy)."""

from __future__ import annotations

from typing import Any

from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.catalog import (
    BUSINESS_INCOME,
    BUSINESS_MEALS_AND_ENTERTAINMENT,
    BUSINESS_NET_INCOME_BEFORE_ADJUSTMENTS,
    BUSINESS_OTHER_EXPENSES,
    BUSINESS_TOTAL_EXPENSES,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, run


def run_kx(**overrides: Any) -> dict[str, tuple[Worksheet, ...]]:
    """Return KX's inputs, as in `returns/2025_return_kx.yaml`; `overrides` replace any of them."""
    inputs: dict[str, Any] = dict(
        cpp_part_4_completed=1,
        business_statements=(
            {
                "business": {
                    "gross_sales": "20000",
                    "meals_and_entertainment": "50",
                    "other_expenses": "500",
                }
            },
        ),
    )
    inputs.update(overrides)
    return run("0", (), "0", "0", "0", "0", "0", **inputs)


def test_return_kxs_cathys_convention_expense_and_meals_total_550() -> None:
    # Other expenses (line 9270) 600 - 2 x 50 = 500 and meals and entertainment (line 8523)
    # 50% x 2 x 50 = 50: total expenses (line 9368) 550.
    result = run_kx()
    assert result["ca/t2125"][0].get(BUSINESS_OTHER_EXPENSES).value == D("500")
    assert result["ca/t2125"][0].get(BUSINESS_MEALS_AND_ENTERTAINMENT).value == D("50")
    assert result["ca/t2125"][0].get(BUSINESS_TOTAL_EXPENSES).value == D("550")


def test_return_kxs_cathys_net_business_income_is_20000_less_550() -> None:
    # Gross sales of 20000 (chosen) less 550: line 9946 is 19450, which is T1 line 13500.
    result = run_kx()
    assert result["ca/t2125"][0].get(BUSINESS_NET_INCOME_BEFORE_ADJUSTMENTS).value == D("19450")
    assert result["ca-on/return"][0].get(BUSINESS_INCOME).value == D("19450")
