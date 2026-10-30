"""CA-ON 2025 end to end: return hr, two farming statements with the Part 9 equity lines.

Return HR (returns/2025_return_hr.yaml) is Return HN's two Form T2042 statements, an Ontario farm
and a Manitoba farm, with the three lines of Part 9 "Details of equity" entered on each: the
Ontario farm's total business liabilities of 250000.00, drawings in the current year of 18000.50
and capital contributions in the current year of 40000.00, and the Manitoba farm's 91000.75,
6200.00 and 12500.25. Area F and Area H are 0.00 on each statement. Each statement exports its
three lines, unread: no line of the return reads them, so the examples check the exports of each
statement and that they change no income.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog import (
    FARM_CAPITAL_CONTRIBUTIONS,
    FARM_DRAWINGS,
    FARM_LIABILITIES,
    FARM_NET_INCOME_AFTER_ADJUSTMENTS,
    TOTAL_INCOME,
)
from tests.jurisdictions.ca_on.end_to_end.support import CA_ON, D, service, starting

ONTARIO = 1
MANITOBA = 2

# The Part 9 lines of the Ontario farm (the first statement), then of the Manitoba farm.
FIRST_LINES = {
    "liabilities": "250000.00",
    "drawings": "18000.50",
    "capital_contributions": "40000.00",
}
SECOND_LINES = {
    "liabilities": "91000.75",
    "drawings": "6200.00",
    "capital_contributions": "12500.25",
}
NO_LINES = {name: "0" for name in FIRST_LINES}


def statement(province: int, wheat: str, seeds: str, lines: Mapping[str, str]) -> dict[str, Any]:
    """One Form T2042 statement, as the keywords of `t2042_statement`: the wheat income and the
    seeds and plants expense of Return HN, the Part 9 lines as given (Area F and H are 0), a fiscal
    period of 365 days of which 184 fall in 2024, and the designated province."""
    return {
        "farm": {"wheat": wheat, "seeds_and_plants": seeds, **lines},
        "farm_fiscal_period_days_entered": 365,
        "farm_designated_province": province,
        "farm_days_in_2024": 184,
    }


def run_hr(
    first: Mapping[str, str] = FIRST_LINES,
    second: Mapping[str, str] = SECOND_LINES,
) -> dict[str, tuple[Worksheet, ...]]:
    """Return HR's starting artifacts: the two farming statements, with the Part 9 lines given for
    each; everything else is 0, as in Return HN."""
    artifacts = starting(
        "0",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        farm_statements=(
            statement(ONTARIO, "96500", "36500", first),
            statement(MANITOBA, "48250", "18250", second),
        ),
    )
    return service().compute(CA_ON, 2025, *artifacts)


def test_return_hrs_ontario_farm_exports_its_part_9_equity_lines_unread() -> None:
    # Part 9 "9931 Total business liabilities" is the entered 250000.00, "9932 Drawings in the
    # current year" is 18000.50 and "9933 Capital contributions in the current year" is 40000.00.
    # Nothing earlier on the form computes them.
    first = run_hr()["ca/t2042"][0]

    assert first.get(FARM_LIABILITIES).value == D("250000.00")
    assert first.get(FARM_DRAWINGS).value == D("18000.50")
    assert first.get(FARM_CAPITAL_CONTRIBUTIONS).value == D("40000.00")


def test_return_hrs_manitoba_farm_exports_its_own_part_9_equity_lines_unread() -> None:
    # The second statement carries its own three lines: 91000.75, 6200.00 and 12500.25.
    second = run_hr()["ca/t2042"][1]

    assert second.get(FARM_LIABILITIES).value == D("91000.75")
    assert second.get(FARM_DRAWINGS).value == D("6200.00")
    assert second.get(FARM_CAPITAL_CONTRIBUTIONS).value == D("12500.25")


def test_the_part_9_equity_lines_change_no_farm_net_income_or_total_income() -> None:
    # Net farming income of each statement (line 9946) is 60000.00 and 30000.00, and the return's
    # total income 90000.00, with or without the three lines: none of them enters a line of income.
    with_lines = run_hr()
    without_lines = run_hr(NO_LINES, NO_LINES)

    assert [
        each.get(FARM_NET_INCOME_AFTER_ADJUSTMENTS).value for each in with_lines["ca/t2042"]
    ] == [D("60000.00"), D("30000.00")]
    assert [
        each.get(FARM_NET_INCOME_AFTER_ADJUSTMENTS).value for each in without_lines["ca/t2042"]
    ] == [D("60000.00"), D("30000.00")]
    assert with_lines["ca-on/return"][0].get(TOTAL_INCOME).value == D("90000.00")
    assert without_lines["ca-on/return"][0].get(TOTAL_INCOME).value == D("90000.00")
