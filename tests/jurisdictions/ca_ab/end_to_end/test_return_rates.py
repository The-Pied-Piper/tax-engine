"""The Alberta return summary carries the average and the marginal income tax rate, for 2025 and
2026, through the real engine (the bundled Alberta manifest, salary the only input).

Calculated the same way as Ontario's, without a surtax, a health premium or a tax reduction:

- The average rate is T1 line 43500 "Total payable" over the salary (T1 line 10100), rounded once
  half-up to 0.0001 (`ca-ab/rate_rounding`); 11,183.76 / 70,000 = 0.159768 prints 0.1598.
- The marginal rate (`ca-ab/marginal_tax_rate`) is the exact sum of two gated parts: the federal
  marginal rate (`ca/federal_marginal_rate`, the T1 line 73 bracket rate, counted only where T1
  line 42900 "Basic federal tax" is above 0) and the Alberta marginal rate
  (`ca-ab/alberta_marginal_rate`, the AB428 line 5 rate, or the line 12 rate when line 5 is blank,
  counted only where AB428 line 68 is above 0). CPP and EI are not counted.

The expected rates are written out by hand, never taken from the engine, from the printed brackets:
federal 14.5% to 57,375 and 20.5% to 114,750, 26% to 177,882, 29% above (2025; 2026 has 14% to
58,523, 20.5% to 117,045, 26% to 181,440, 29% above); Alberta 8% to 60,000 of taxable income, 10%
to 151,234, 12% to 181,481 (AB428 line 5), then 13% (AB428 line 12). Taxable income is a little
under the salary (the CPP enhanced deduction), so each salary below sits well inside its bracket.

The gates open at the zero-tax boundaries, measured by running the real return cent by cent (the
part is 0 one cent below and counts at the cent pinned). The 2025 Alberta line 68 is not monotone
just under its boundary because of cent rounding: it is 0.01 from 23,931.13 to 23,931.21, 0.00 from
23,931.22 to 23,931.24 and 0.01 from 23,931.25 on, so the pinned cents are a closed and an open
point, not the first salary with tax:

- 2025: federal at 18,820.27 (T1 line 42900 is 0.00 at 18,820.26 and 0.01 at 18,820.27); Alberta
  at 23,931.25 (AB428 line 68 is 0.00 at 23,931.24 and 0.01 at 23,931.25)
- 2026: federal at 19,200.18 (0.00 at 19,200.17); Alberta at 24,411.18 (0.00 at 24,411.17)

The total payable at each salary is the engine's own T1 line 43500 recorded from a run (only the
$70,000 figure of 2025 is a fixed anchor, 11,183.76); each average was re-checked by hand as the
quotient.
"""

from __future__ import annotations

import re
from decimal import Decimal

import pytest

from tax_engine import build_tax_computation
from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
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
FEDERAL = "ca/federal_marginal_rate"
ALBERTA_RATE = "ca-ab/alberta_marginal_rate"
MARGINAL = "ca-ab/marginal_tax_rate"
AVERAGE = "ca-ab/average_income_tax_rate"
TOTAL_PAYABLE = "ca/total_payable"
LINE_75 = "ca-ab/ab428_alberta_tax_line_75"

# Year, salary, federal part, Alberta part, marginal rate, T1 line 43500 total payable, average.
FIGURES = [
    # Salary 100: no tax at all, both gates closed.
    (2025, "100", "0", "0", "0", "0.00", "0"),
    (2026, "100", "0", "0", "0", "0.00", "0"),
    # 2025 federal boundary: closed at 18,820.26, open (14.5%) at 18,820.27; Alberta still closed.
    (2025, "18820.26", "0", "0", "0", "0.00", "0"),
    (2025, "18820.27", "0.145", "0", "0.145", "0.01", "0"),
    # 2025 Alberta boundary: closed at 23,931.24, open (8%) at 23,931.25.
    (2025, "23931.24", "0.145", "0", "0.145", "684.85", "0.0286"),
    (2025, "23931.25", "0.145", "0.08", "0.225", "684.87", "0.0286"),
    # 2026 federal boundary: closed at 19,200.17, open (14%) at 19,200.18; Alberta still closed.
    (2026, "19200.17", "0", "0", "0", "0.00", "0"),
    (2026, "19200.18", "0.14", "0", "0.14", "0.01", "0"),
    # 2026 Alberta boundary: closed at 24,411.17, open (8%) at 24,411.18.
    (2026, "24411.17", "0.14", "0", "0.14", "674.25", "0.0276"),
    (2026, "24411.18", "0.14", "0.08", "0.22", "674.26", "0.0276"),
    # Salary 20,000 (taxable income 19,835.00): federal only, 14.5% (2025) and 14% (2026).
    (2025, "20000", "0.145", "0", "0.145", "158.09", "0.0079"),
    (2026, "20000", "0.14", "0", "0.14", "103.49", "0.0052"),
    # Salary 70,000 (taxable income 69,335.00): 20.5% federal, 10% Alberta (60,000 to 151,234).
    # 11,183.76 / 70,000 = 0.159768 -> 0.1598; 10,812.98 / 70,000 = 0.154471 -> 0.1545.
    (2025, "70000", "0.205", "0.10", "0.305", "11183.76", "0.1598"),
    (2026, "70000", "0.205", "0.10", "0.305", "10812.98", "0.1545"),
    # Salary 120,000 (taxable income about 118,900): 26% federal, 10% Alberta.
    (2025, "120000", "0.26", "0.10", "0.36", "26524.21", "0.2210"),
    (2026, "120000", "0.26", "0.10", "0.36", "25972.52", "0.2164"),
    # Salary 160,000 (taxable income about 158,900): 26% federal, 12% Alberta (151,234 to 181,481).
    (2025, "160000", "0.26", "0.12", "0.38", "41078.05", "0.2567"),
    (2026, "160000", "0.26", "0.12", "0.38", "40464.80", "0.2529"),
    # Salary 200,000 (taxable income about 198,900, above the table 1 limit of 181,481): the
    # AB428 line 12 rate of 13% is read; federal 29% (above 177,882, and 181,440 in 2026).
    # 57,148.10 / 200,000 = 0.285740 -> 0.2857; 56,376.82 / 200,000 = 0.281884 -> 0.2819.
    (2025, "200000", "0.29", "0.13", "0.42", "57148.10", "0.2857"),
    (2026, "200000", "0.29", "0.13", "0.42", "56376.82", "0.2819"),
]
PART_FIGURES = [(y, s, f, a, m) for y, s, f, a, m, _, _ in FIGURES]
AVERAGE_FIGURES = [(y, s, t, r) for y, s, _, _, _, t, r in FIGURES]
# Year, salary, AB428 line 75 (the anchors that must not move).
LINE_75_ANCHORS = [
    (2025, "20000", "0.00"),
    (2025, "70000", "3598.12"),
    (2025, "200000", "17680.36"),
    (2026, "20000", "0.00"),
    (2026, "70000", "3534.79"),
    (2026, "200000", "17500.28"),
]


def _summary(year: int, salary: str) -> Worksheet:
    # No fixture: the bundled Alberta manifest, as the calculator loads it, salary the only input.
    worksheets = build_tax_computation().compute(
        ALBERTA, year, Artifact(EMPLOYMENT_INCOME, D(salary))
    )
    (summary,) = worksheets[RETURN]
    return summary


def _value(summary: Worksheet, name: str) -> Decimal:
    value = summary.get(bundled_kinds().kind(name)).value
    assert isinstance(value, Decimal)
    return value


def _sum_line(sheet: Worksheet) -> SumLine:
    """The one trace line of the marginal tax rate step, found by its output kind."""
    label = bundled_kinds().kind(MARGINAL).label
    (line,) = [
        line for line in sheet.trace if isinstance(line, SumLine) and line.output.label == label
    ]
    return line


@pytest.mark.parametrize("name", [MARGINAL, AVERAGE, ALBERTA_RATE])
def test_the_new_kinds_are_registered_non_negative_amounts(name: str) -> None:
    kind = bundled_kinds().kind(name)

    assert kind.identifier == name
    assert non_negative(kind)
    assert kind.value_type is Decimal


@pytest.mark.parametrize(("year", "salary", "federal", "alberta", "marginal"), PART_FIGURES)
def test_the_marginal_rate_is_the_exact_sum_of_the_federal_and_the_alberta_part(
    year: int, salary: str, federal: str, alberta: str, marginal: str
) -> None:
    summary = _summary(year, salary)

    assert _value(summary, FEDERAL) == D(federal)
    assert _value(summary, ALBERTA_RATE) == D(alberta)
    assert _value(summary, MARGINAL) == D(marginal)
    assert D(federal) + D(alberta) == D(marginal)


@pytest.mark.parametrize(("year", "salary", "total_payable", "average"), AVERAGE_FIGURES)
def test_the_average_rate_is_the_total_payable_over_the_salary_half_up_to_ten_thousandths(
    year: int, salary: str, total_payable: str, average: str
) -> None:
    summary = _summary(year, salary)

    assert _value(summary, TOTAL_PAYABLE) == D(total_payable)
    assert _value(summary, AVERAGE) == D(average)
    assert (D(total_payable) / D(salary)).quantize(D("0.0001"), rounding="ROUND_HALF_UP") == D(
        average
    )


@pytest.mark.parametrize("year", [2025, 2026])
def test_a_salary_of_100_reads_0_for_both_rates(year: int) -> None:
    summary = _summary(year, "100")

    assert _value(summary, MARGINAL) == D("0")
    assert _value(summary, AVERAGE) == D("0")


def test_the_2025_average_at_70000_is_15_98_percent() -> None:
    summary = _summary(2025, "70000")

    assert _value(summary, TOTAL_PAYABLE) == D("11183.76")
    assert _value(summary, AVERAGE) == D("0.1598")


@pytest.mark.parametrize(("year", "salary", "line_75"), LINE_75_ANCHORS)
def test_the_alberta_tax_anchors_do_not_move(year: int, salary: str, line_75: str) -> None:
    worksheets = build_tax_computation().compute(
        ALBERTA, year, Artifact(EMPLOYMENT_INCOME, D(salary))
    )
    (ab428,) = worksheets["ca-ab/ab428"]

    assert ab428.get(bundled_kinds().kind(LINE_75)).value == D(line_75)


@pytest.mark.parametrize("year", [2025, 2026])
def test_line_12_supplies_the_rate_above_the_table_1_limit_and_line_5_below_it(year: int) -> None:
    # 200,000 has taxable income 198,9xx, above 181,481: line 12's 13% is the Alberta part; at
    # 160,000 (taxable income 158,9xx) line 5's 12% is.
    assert _value(_summary(year, "200000"), ALBERTA_RATE) == D("0.13")
    assert _value(_summary(year, "160000"), ALBERTA_RATE) == D("0.12")


def test_the_marginal_rate_is_not_rounded_to_the_cent() -> None:
    # 0.145 + 0.08 = 0.225 keeps its third place: no dollars-and-cents rule is applied to a rate.
    value = _value(_summary(2025, "23931.25"), MARGINAL)

    assert value == D("0.225")
    assert value.as_tuple().exponent == -3


def test_the_return_prints_both_rates_as_percentages_in_the_core_percent_unit() -> None:
    summary = _summary(2025, "70000")
    kinds = bundled_kinds()

    for name in (MARGINAL, AVERAGE):
        unit = summary.unit(kinds.kind(name).label)
        assert unit is not None
        assert unit.identifier == "core/percent"


def test_the_two_rate_steps_have_no_reference_and_no_title() -> None:
    summary = _summary(2025, "70000")
    kinds = bundled_kinds()

    for name in (MARGINAL, AVERAGE):
        label = kinds.kind(name).label
        assert summary.reference(label) is None
        assert summary.title(label) is None


@pytest.mark.parametrize("year", [2025, 2026])
def test_the_marginal_rate_is_traced_as_one_exact_sum_of_the_federal_then_the_alberta_part(
    year: int,
) -> None:
    sheet = _summary(year, "200000")
    kinds = bundled_kinds()

    line = _sum_line(sheet)

    assert [(kind.label, value) for kind, value in line.parts] == [
        (kinds.kind(FEDERAL).label, D("0.29")),
        (kinds.kind(ALBERTA_RATE).label, D("0.13")),
    ]
    assert line.rounding == NO_ROUNDING
    assert line.total == D("0.42")
    assert line.amount == sheet.get(kinds.kind(MARGINAL)).value


@pytest.mark.parametrize("year", [2025, 2026])
def test_the_marginal_rate_is_explained_in_english_as_percentages(year: int) -> None:
    sheet = _summary(year, "70000")

    text = EnglishTraceRenderer().render(_sum_line(sheet), sheet)

    assert re.fullmatch(
        r".*\(20\.5%\) plus .+ \(10(\.0+)?%\) gives 30\.5% \(not rounded\)\.?", text
    )


@pytest.mark.parametrize("year", [2025, 2026])
def test_the_marginal_rate_comes_last_in_the_trace(year: int) -> None:
    sheet = _summary(year, "100000")
    kinds = bundled_kinds()
    labels = [line.label for line in sheet.trace]

    marginal = labels.index(kinds.kind(MARGINAL).label)

    assert marginal == len(labels) - 1
    assert labels.count(kinds.kind(MARGINAL).label) == 1
    for part in (FEDERAL, ALBERTA_RATE):
        assert labels.index(kinds.kind(part).label) < marginal
