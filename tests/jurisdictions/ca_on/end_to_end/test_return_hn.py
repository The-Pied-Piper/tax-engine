"""CA-ON 2025 end to end: return hn, two farming statements with the Area F and H lines.

Return HN (returns/2025_return_hn.yaml) is Return DP's two Form T2042 statements, an Ontario farm
and a Manitoba farm, with the four lines of Area F (9923 and 9924) and Area H (9929 and 9930)
entered on each: the Ontario farm's land additions of 120000.00, land dispositions of 45000.50,
quota additions of 30000.00 and quota dispositions of 12500.25, and the Manitoba farm's 64000.75,
9100.40, 4500.00 and 2750.10. Each statement exports its four lines, unread: no line of the return
reads them, so the examples check the exports of each statement and that they change no income.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog import (
    FARM_LAND_ADDITIONS,
    FARM_LAND_DISPOSITIONS,
    FARM_NET_INCOME_AFTER_ADJUSTMENTS,
    FARM_QUOTA_ADDITIONS,
    FARM_QUOTA_DISPOSITIONS,
    TOTAL_INCOME,
)
from tests.jurisdictions.ca_on.end_to_end.support import CA_ON, D, service, starting

ONTARIO = 1
MANITOBA = 2

# The Area F and H lines of the Ontario farm (the first statement), then of the Manitoba farm.
FIRST_LINES = {
    "land_additions": "120000.00",
    "land_dispositions": "45000.50",
    "quota_additions": "30000.00",
    "quota_dispositions": "12500.25",
}
SECOND_LINES = {
    "land_additions": "64000.75",
    "land_dispositions": "9100.40",
    "quota_additions": "4500.00",
    "quota_dispositions": "2750.10",
}
NO_LINES = {name: "0" for name in FIRST_LINES}


def statement(province: int, wheat: str, seeds: str, lines: Mapping[str, str]) -> dict[str, Any]:
    """One Form T2042 statement, as the keywords of `t2042_statement`: the wheat income and the
    seeds and plants expense of Return DP, the Area F and H lines as given, a fiscal period of 365
    days of which 184 fall in 2024, and the designated province."""
    return {
        "farm": {"wheat": wheat, "seeds_and_plants": seeds, **lines},
        "farm_fiscal_period_days_entered": 365,
        "farm_designated_province": province,
        "farm_days_in_2024": 184,
    }


def run_hn(
    first: Mapping[str, str] = FIRST_LINES,
    second: Mapping[str, str] = SECOND_LINES,
) -> dict[str, tuple[Worksheet, ...]]:
    """Return HN's starting artifacts: the two farming statements, with the Area F and H lines
    given for each; everything else is 0, as in Return DP."""
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


def test_return_hns_ontario_farm_exports_its_land_and_quota_lines_unread() -> None:
    # Area F "9923 Total cost of all land additions in the year" is the entered 120000.00, and
    # "9924 Total proceeds from all land dispositions in the year" is 45000.50; Area H "9929 Total
    # cost of all quota additions in the year" is 30000.00 and "9930 Total proceeds from all quota
    # dispositions in the year" is 12500.25. Nothing earlier on the form computes them.
    first = run_hn()["ca/t2042"][0]

    assert first.get(FARM_LAND_ADDITIONS).value == D("120000.00")
    assert first.get(FARM_LAND_DISPOSITIONS).value == D("45000.50")
    assert first.get(FARM_QUOTA_ADDITIONS).value == D("30000.00")
    assert first.get(FARM_QUOTA_DISPOSITIONS).value == D("12500.25")


def test_return_hns_manitoba_farm_exports_its_own_land_and_quota_lines_unread() -> None:
    # The second statement carries its own four lines: 64000.75, 9100.40, 4500.00 and 2750.10.
    second = run_hn()["ca/t2042"][1]

    assert second.get(FARM_LAND_ADDITIONS).value == D("64000.75")
    assert second.get(FARM_LAND_DISPOSITIONS).value == D("9100.40")
    assert second.get(FARM_QUOTA_ADDITIONS).value == D("4500.00")
    assert second.get(FARM_QUOTA_DISPOSITIONS).value == D("2750.10")


def test_the_land_and_quota_lines_change_no_farm_net_income_or_total_income() -> None:
    # Net farming income of each statement (line 9946) is 60000.00 and 30000.00, and the return's
    # total income 90000.00, with or without the four lines: none of them enters a line of income.
    with_lines = run_hn()
    without_lines = run_hn(NO_LINES, NO_LINES)

    assert [
        each.get(FARM_NET_INCOME_AFTER_ADJUSTMENTS).value for each in with_lines["ca/t2042"]
    ] == [
        D("60000.00"),
        D("30000.00"),
    ]
    assert [
        each.get(FARM_NET_INCOME_AFTER_ADJUSTMENTS).value for each in without_lines["ca/t2042"]
    ] == [D("60000.00"), D("30000.00")]
    assert with_lines["ca-on/return"][0].get(TOTAL_INCOME).value == D("90000.00")
    assert without_lines["ca-on/return"][0].get(TOTAL_INCOME).value == D("90000.00")
