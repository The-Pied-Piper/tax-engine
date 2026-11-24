"""The Alberta return summary's rates, for 2025 and 2026, through the real engine (the bundled
Alberta manifest, salary the only input).

The values of the marginal rate, worked by hand, are in
`test_return_marginal_tax_rate_values.py`, the gates in `test_return_marginal_tax_rate_gates.py`
and `..._gates_2026.py`, and the check against a double run of the engine in
`test_return_marginal_tax_rate_extra_run.py`. This file holds what is left: the kinds, the units,
the trace and the AB428 anchors that must not move.
"""

from __future__ import annotations

import re
from decimal import Decimal

import pytest

from tax_engine import build_tax_computation
from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.parameters.rounding import NO_ROUNDING
from tax_engine.domain.trace import SumLine
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tests.kinds import bundled_kinds, non_negative

D = Decimal
ALBERTA = JurisdictionCode("CA-AB")
RETURN = "ca-ab/return"
MARGINAL = "ca-ab/marginal_tax_rate"
AVERAGE = "ca-ab/average_tax_rate"
ALBERTA_RATE = "ca-ab/alberta_marginal_rate"
LINE_75 = "ca-ab/ab428_alberta_tax_line_75"

# Year, salary, AB428 line 75 (the anchors that must not move).
LINE_75_ANCHORS = [
    (2025, "20000", "0.00"),
    (2025, "70000", "3598.12"),
    (2025, "200000", "17680.36"),
    (2026, "20000", "0.00"),
    (2026, "70000", "3534.79"),
    (2026, "200000", "17500.28"),
]


def _worksheets(year: int, salary: str) -> dict[str, tuple[Worksheet, ...]]:
    # No fixture: the bundled Alberta manifest, as the calculator loads it, salary the only input.
    return build_tax_computation().compute(
        TaxCalculationRequest(ALBERTA, year, (Artifact(EMPLOYMENT_INCOME, D(salary)),))
    )


def _summary(year: int, salary: str) -> Worksheet:
    (summary,) = _worksheets(year, salary)[RETURN]
    return summary


def _value(summary: Worksheet, name: str) -> Decimal:
    value = summary.get(bundled_kinds().kind(name)).value
    assert isinstance(value, Decimal)
    return value


@pytest.mark.parametrize("year", [2025, 2026])
def test_a_salary_of_100_reads_0_for_both_rates(year: int) -> None:
    summary = _summary(year, "100")

    assert _value(summary, MARGINAL) == D("0")
    assert _value(summary, AVERAGE) == D("0")


@pytest.mark.parametrize("year", [2025, 2026])
def test_the_alberta_part_is_the_line_5_rate_below_the_table_1_limit_and_line_12_above_it(
    year: int,
) -> None:
    # At $160,000 and $200,000 every contribution is at its maximum, so the Alberta part is the
    # printed bracket rate alone: line 5's 12% below 181,481 (185,111 in 2026), line 12's 13% above.
    assert _value(_summary(year, "160000"), ALBERTA_RATE) == D("0.12")
    assert _value(_summary(year, "200000"), ALBERTA_RATE) == D("0.13")


@pytest.mark.parametrize("name", [MARGINAL, AVERAGE, ALBERTA_RATE])
def test_the_rate_kinds_are_registered_non_negative_amounts(name: str) -> None:
    kind = bundled_kinds().kind(name)

    assert kind.identifier == name
    assert non_negative(kind)
    assert kind.value_type is Decimal


def test_the_marginal_rate_is_not_rounded_to_the_cent() -> None:
    # 0.3503125 keeps its seventh place: no dollars-and-cents rule is applied to a rate.
    value = _value(_summary(2025, "70000"), MARGINAL)

    assert value.as_tuple().exponent == -7


def test_the_return_prints_both_rates_as_percentages_in_the_core_percent_unit() -> None:
    summary = _summary(2025, "70000")
    kinds = bundled_kinds()

    for name in (MARGINAL, AVERAGE):
        unit = summary.unit(kinds.kind(name).label)
        assert unit is not None
        assert unit.identifier == "core/percent"


def test_only_line_167_of_the_return_has_a_reference() -> None:
    summary = _summary(2025, "70000")
    kinds = bundled_kinds()

    for name in (MARGINAL, AVERAGE, ALBERTA_RATE):
        label = kinds.kind(name).label
        assert summary.reference(label) is None
        assert summary.title(label) is None


@pytest.mark.parametrize(("year", "salary", "line_75"), LINE_75_ANCHORS)
def test_the_alberta_tax_anchors_do_not_move(year: int, salary: str, line_75: str) -> None:
    (ab428,) = _worksheets(year, salary)["ca-ab/ab428"]

    assert ab428.get(bundled_kinds().kind(LINE_75)).value == D(line_75)


def _sum_line(sheet: Worksheet) -> SumLine:
    """The one trace line of the marginal tax rate step, found by its output kind."""
    label = bundled_kinds().kind(MARGINAL).label
    (line,) = [
        line for line in sheet.trace if isinstance(line, SumLine) and line.output.label == label
    ]
    return line


@pytest.mark.parametrize("year", [2025, 2026])
def test_the_marginal_rate_is_traced_as_one_exact_sum_of_the_three_parts(year: int) -> None:
    sheet = _summary(year, "200000")
    kinds = bundled_kinds()

    line = _sum_line(sheet)

    assert [kind.label for kind, _value in line.parts] == [
        kinds.kind("ca-ab/marginal_federal_rate").label,
        kinds.kind(ALBERTA_RATE).label,
        kinds.kind("ca-ab/marginal_contribution_rate").label,
    ]
    assert line.rounding == NO_ROUNDING
    assert sum((value for _kind, value in line.parts), D("0")) == line.total
    assert line.amount == sheet.get(kinds.kind(MARGINAL)).value


@pytest.mark.parametrize("year", [2025, 2026])
def test_the_marginal_rate_is_explained_in_english_as_percentages(year: int) -> None:
    sheet = _summary(year, "70000")

    text = EnglishTraceRenderer().render(_sum_line(sheet), sheet)

    assert re.fullmatch(r".*\(\d+(\.\d+)?%\) plus .+ gives \d+(\.\d+)?% \(not rounded\)\.?", text)


@pytest.mark.parametrize("year", [2025, 2026])
def test_the_marginal_rate_is_the_last_line_of_the_trace(year: int) -> None:
    sheet = _summary(year, "100000")
    kinds = bundled_kinds()
    labels = [line.label for line in sheet.trace]

    assert labels.index(kinds.kind(MARGINAL).label) == len(labels) - 1
    assert labels.count(kinds.kind(MARGINAL).label) == 1
    for part in ("ca-ab/marginal_federal_rate", ALBERTA_RATE, "ca-ab/marginal_contribution_rate"):
        assert labels.index(kinds.kind(part).label) < len(labels) - 1
