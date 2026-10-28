"""CA-ON 2025 end to end: return hq."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.catalog import (
    BUSINESS_CAPITAL_CONTRIBUTIONS,
    BUSINESS_DRAWINGS,
    BUSINESS_INCOME,
    BUSINESS_LIABILITIES,
    BUSINESS_NET_INCOME_AFTER_ADJUSTMENTS,
    GROSS_BUSINESS_INCOME,
    TOTAL_INCOME,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, run

# Return HQ's T2125 statement: a sole proprietorship with chosen gross sales of 40000 and rent of
# 12000, so the net business income (line 9946) is 28000, with no capital cost allowance and no
# land. Part 9 "Details of equity" enters line 9931 "Total business liabilities" as 18400.50, line
# 9932 "Drawings in the current year" as 24000 and line 9933 "Capital contributions in the current
# year" as 5000: inputs taken as entered and carried to the printed lines.
BUSINESS_HQ: dict[str, str] = {
    "gross_sales": "40000",
    "rent": "12000",
    "liabilities": "18400.50",
    "drawings": "24000",
    "capital_contributions": "5000",
}


def run_hq(
    changes: Mapping[str, Any] | None = None, **overrides: Any
) -> dict[str, tuple[Worksheet, ...]]:
    """Return HQ's inputs, as in `returns/2025_return_hq.yaml`: a single filer whose only income is
    the net business income of one business with one T2125 statement, for a full fiscal period
    (0 days entered)."""
    statement: dict[str, Any] = {"business": BUSINESS_HQ}
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


def test_return_hqs_equity_lines_are_carried_through_unchanged() -> None:
    # Part 9 line 9931 "Total business liabilities" 18400.50, line 9932 "Drawings in the current
    # year" 24000 and line 9933 "Capital contributions in the current year" 5000 are the entered
    # amounts. Nothing earlier on the form computes them, so each is carried through as entered.
    statement = run_hq()["ca/t2125"][0]

    assert statement.get(BUSINESS_LIABILITIES).value == D("18400.50")
    assert statement.get(BUSINESS_DRAWINGS).value == D("24000")
    assert statement.get(BUSINESS_CAPITAL_CONTRIBUTIONS).value == D("5000")


def test_the_equity_lines_change_no_income_line_against_all_three_at_zero() -> None:
    # The same return with the three Part 9 amounts at 0 gives the same net business income, gross
    # business income, business income and total income: the equity lines feed none of them.
    entered = run_hq()
    zeroed = run_hq(
        {
            "business": {
                **BUSINESS_HQ,
                "liabilities": "0",
                "drawings": "0",
                "capital_contributions": "0",
            }
        }
    )
    entered_statement = entered["ca/t2125"][0]
    zeroed_statement = zeroed["ca/t2125"][0]
    entered_worksheet = entered["ca-on/return"][0]
    zeroed_worksheet = zeroed["ca-on/return"][0]

    assert entered_statement.get(BUSINESS_NET_INCOME_AFTER_ADJUSTMENTS).value == D("28000.00")
    assert zeroed_statement.get(BUSINESS_NET_INCOME_AFTER_ADJUSTMENTS).value == D("28000.00")
    assert (
        entered_worksheet.get(GROSS_BUSINESS_INCOME).value
        == zeroed_worksheet.get(GROSS_BUSINESS_INCOME).value
    )
    assert (
        entered_worksheet.get(BUSINESS_INCOME).value == zeroed_worksheet.get(BUSINESS_INCOME).value
    )
    assert entered_worksheet.get(TOTAL_INCOME).value == zeroed_worksheet.get(TOTAL_INCOME).value


def test_return_hqs_net_business_income_is_28000_on_t1_line_13500_with_gross_40000() -> None:
    # Gross sales 40000 less rent 12000 is 28000 of net business income (line 9946), which is T1
    # line 13500; the gross business income on the return is 40000.
    result = run_hq()
    statement = result["ca/t2125"][0]
    worksheet = result["ca-on/return"][0]

    assert statement.get(BUSINESS_NET_INCOME_AFTER_ADJUSTMENTS).value == D("28000.00")
    assert worksheet.get(GROSS_BUSINESS_INCOME).value == D("40000")
    assert worksheet.get(BUSINESS_INCOME).value == D("28000.00")
