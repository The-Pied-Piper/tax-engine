"""The Alberta return summary carries the marginal tax rate on the take-home basis, for 2025 and
2026, through the real engine (the bundled Alberta manifest, salary the only input).

The marginal rate (`ca-ab/marginal_tax_rate`) is the change in T1 line 43500, CPP, CPP2 and EI
(T2204 line 16) per further dollar of salary, with no paid credits. It is the sum of the federal
marginal rate, the Alberta marginal rate and the contribution rate. The independent check against
a double run of the engine is `test_return_marginal_tax_rate_extra_run.py`; this file pins values
worked out by hand from the printed rates, and the invariants of the kinds.

Worked by hand for 2025 at a salary of $70,000 (taxable income a little under it, inside the
federal 20.5% and the Alberta 10% brackets; CPP base 4.95% and first additional 1% still charged,
CPP2 and EI at their maximum; the credits are earned on the CPP base only):
- net income rate 1 - 0.01 = 0.99;
- federal 0.205 x 0.99 - 0.145 x 0.0495 = 0.1957725 (federal credit rate 14.5%);
- Alberta 0.10 x 0.99 - 0.08 x 0.0495 = 0.09504 (Alberta credit rate 8%);
- contributions 0.0495 + 0.01 = 0.0595;
- total 0.1957725 + 0.09504 + 0.0595 = 0.3503125.
At $120,000 and $160,000 every contribution is at its maximum, so the rate is the two bracket rates
alone: 26% + 10% and 26% + 12%. At $200,000 the federal basic personal amount is phased down
(0.145 x (16,129 - 14,538) / (253,414 - 177,882) of further federal credit lost; the shared
federal form rounds the quotient to 7 places, 0.0210639, so the figure is 0.145 x 0.0210639 =
0.0030542655), and the AB428 line 12 rate of 13% applies: 0.29 + 0.13 + 0.0030542655.
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

# Year, salary, marginal rate. The first rows are the cases worked out by hand above.
FIGURES = [
    (2025, "100", "0"),
    (2026, "100", "0"),
    (2025, "20000", "0.2098945"),
    (2026, "20000", "0.205188"),
    (2025, "70000", "0.3503125"),
    (2026, "70000", "0.35056"),
    (2025, "120000", "0.36"),
    (2026, "120000", "0.36"),
    (2025, "160000", "0.38"),
    (2026, "160000", "0.38"),
    (2025, "200000", "0.4230542655"),
    (2026, "200000", "0.422949296"),
]
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


@pytest.mark.parametrize(("year", "salary", "marginal"), FIGURES)
def test_the_marginal_rate_at_each_salary(year: int, salary: str, marginal: str) -> None:
    assert _value(_summary(year, salary), MARGINAL) == D(marginal)


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
