"""CA-ON 2025 end to end: return kw (Guide T4002's James)."""

from __future__ import annotations

from typing import Any

from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog import (
    BUSINESS_HOME_ALLOWABLE_CLAIM,
    BUSINESS_HOME_EXPENSES,
    BUSINESS_HOME_EXPENSES_SUBTOTAL,
    BUSINESS_INCOME,
    BUSINESS_NET_INCOME_AFTER_ADJUSTMENTS,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, run


def run_kw(**overrides: Any) -> dict[str, tuple[Worksheet, ...]]:
    """Return KW's inputs, as in `returns/2025_return_kw.yaml`; `overrides` replace any of them."""
    inputs: dict[str, Any] = dict(
        cpp_part_4_completed=1,
        business_statements=(
            {
                "business": {
                    "gross_sales": "20000",
                    "home_other_expenses": "5800",
                    "home_personal_use_part": "5195.84",
                }
            },
        ),
    )
    inputs.update(overrides)
    return run("0", (), "0", "0", "0", "0", "0", **inputs)


def test_return_kws_jamess_business_use_of_home_claim_is_604_16() -> None:
    # Part 7: the 5800 of household expenses less the personal-use part 5195.84 is 604.16,
    # below the net income of 20000 before the claim, so the allowable claim (line 9945) is
    # 604.16.
    result = run_kw()
    assert result["ca/t2125"][0].get(BUSINESS_HOME_EXPENSES_SUBTOTAL).value == D("5800")
    assert result["ca/t2125"][0].get(BUSINESS_HOME_ALLOWABLE_CLAIM).value == D("604.16")
    assert result["ca/t2125"][0].get(BUSINESS_HOME_EXPENSES).value == D("604.16")


def test_return_kws_jamess_net_business_income_is_20000_less_604_16() -> None:
    # Net income before the claim 20000 (chosen sales, no other expense) less 604.16 is
    # 19395.84, T1 line 13500.
    result = run_kw()
    assert result["ca/t2125"][0].get(BUSINESS_NET_INCOME_AFTER_ADJUSTMENTS).value == D("20000")
    assert result["ca-on/return"][0].get(BUSINESS_INCOME).value == D("19395.84")
