"""The "if negative, enter 0" floors that Form T657 (2025) prints under the amounts taken "from
line 6 / line 12 of Form T2017", run on the manifest's own steps with negative amounts.

Since the amounts are read from the rows of Form T2017 (`ca/t2017_reserve_total_for_period`), an
earlier-year amount is the 2024 reserve less the 2025 reserve of dispositions whose claim cannot be
above the 2024 reserve, so no worked return can reach these floors any more. Each chart's step is
therefore applied to a worksheet that starts with the amounts it adds, the way the return would
hold them, and the line it produces is read back:

- Chart 2016 Part 1 "amount D plus amount E (if negative, enter "0")" and Charts 2017 to 2023
  Part 1 "amount F plus amount G (if negative, enter "0")";
- Charts 2024 Period 1 and Period 2 "Add amounts F to H (if negative, enter "0")";
- Chart 2025 Part 1 "Add amounts F to J (if negative, enter "0")".

Chart 2025 Part 2 is not here: its amounts are of dispositions in 2025, which a worked return can
make negative.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine import build_tax_computation
from tax_engine.domain.artifact import Artifact, ArtifactKind
from tax_engine.domain.capabilities.sum_not_below_zero import SumNotBelowZero
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca import catalog
from tests.jurisdictions.ca_on.manifest_families.t657_chart_amounts_from_t2017 import CHARTS

D = Decimal
CA_ON = JurisdictionCode("CA-ON")

# The floor step of each chart, by the dataset of the dispositions the chart takes.
FLOORS = {
    "t657_chart_2016_dispositions": "chart_2016_part_1_amounts_d_and_e",
    **{
        f"t657_chart_{year}_dispositions": f"chart_{year}_part_1_amounts_f_and_g"
        for year in range(2017, 2024)
    },
    "t657_chart_2024_period_1_dispositions": "chart_2024_period_1_amounts_f_to_h",
    "t657_chart_2024_period_2_dispositions": "chart_2024_period_2_amounts_f_to_h",
    "t657_chart_2025_part_1_dispositions": "chart_2025_part_1_amounts_f_to_j",
}
EARLIER_YEAR_CHARTS = tuple(chart for chart in CHARTS if chart[0] in FLOORS)
CHART_IDS = [chart[0] for chart in EARLIER_YEAR_CHARTS]


def floor_step(output: str) -> SumNotBelowZero:
    order = build_tax_computation().compose(CA_ON, 2025).form("ca-on/return").composition.order
    (step,) = (
        each
        for each in order
        if isinstance(each, SumNotBelowZero) and {k.identifier for k in each.produces} == {output}
    )
    return step


def amount_kinds(chart: tuple[str, str, str]) -> tuple[ArtifactKind[Decimal], ...]:
    """The kinds the chart takes from lines 6 and 12 of Form T2017."""
    return (getattr(catalog, chart[1]), getattr(catalog, chart[2]))


def floored(chart: tuple[str, str, str], amounts: tuple[str, str]) -> Decimal:
    """The floor step's output for the two T2017 `amounts`, its other parts being 0."""
    step = floor_step(f"ca/{FLOORS[chart[0]]}")
    fed = dict(zip(amount_kinds(chart), amounts, strict=True))
    worksheet = Worksheet(*(Artifact(kind, D(fed.get(kind, "0"))) for kind in step.consumes))
    worksheet.apply(step)
    (output,) = step.produces
    value = worksheet.get(output).value
    assert isinstance(value, Decimal)
    return value


def test_there_is_a_floor_for_every_chart_but_chart_2025_part_2() -> None:
    assert len(EARLIER_YEAR_CHARTS) == 11
    assert len(EARLIER_YEAR_CHARTS) == len(FLOORS)


@pytest.mark.parametrize("chart", EARLIER_YEAR_CHARTS, ids=CHART_IDS)
def test_each_floor_adds_the_two_amounts_taken_from_form_t2017(
    chart: tuple[str, str, str],
) -> None:
    step = floor_step(f"ca/{FLOORS[chart[0]]}")

    assert set(amount_kinds(chart)) <= step.consumes


@pytest.mark.parametrize("chart", EARLIER_YEAR_CHARTS, ids=CHART_IDS)
def test_a_loss_on_both_lines_gives_0(chart: tuple[str, str, str]) -> None:
    assert floored(chart, ("-50.25", "-70.00")) == D("0")


@pytest.mark.parametrize("chart", EARLIER_YEAR_CHARTS, ids=CHART_IDS)
def test_a_loss_on_one_line_larger_than_the_gain_on_the_other_gives_0(
    chart: tuple[str, str, str],
) -> None:
    assert floored(chart, ("-400.00", "150.00")) == D("0")
    assert floored(chart, ("150.00", "-400.00")) == D("0")


@pytest.mark.parametrize("chart", EARLIER_YEAR_CHARTS, ids=CHART_IDS)
def test_a_loss_on_one_line_smaller_than_the_gain_on_the_other_gives_the_difference(
    chart: tuple[str, str, str],
) -> None:
    assert floored(chart, ("-100.00", "300.25")) == D("200.25")
    assert floored(chart, ("300.25", "-100.00")) == D("200.25")


@pytest.mark.parametrize("chart", EARLIER_YEAR_CHARTS, ids=CHART_IDS)
def test_gains_on_both_lines_give_their_sum(chart: tuple[str, str, str]) -> None:
    assert floored(chart, ("100.00", "20.50")) == D("120.50")
