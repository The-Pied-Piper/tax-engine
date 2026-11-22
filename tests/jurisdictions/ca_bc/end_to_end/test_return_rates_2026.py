"""The British Columbia return summary carries the average and the marginal income tax rate (2026),
through the registered engine (`build_tax_computation`, which lists British Columbia; salary the
only input).

The British Columbia 2026 datasets are PROVISIONAL: the 2026 forms (Form BC428, CRA 5010-c; Form
BC479, CRA 5010-tc) are not yet published, and the figures come from T4127 (July 2026) or are
carried forward or derived from 2025. Every figure pinned here follows those provisional datasets
and was derived by hand; it must be re-checked when CRA publishes the 2026 forms.

The rates are calculated the same way as for 2025 (see `test_return_rates.py`), with the 2026
British Columbia figures:

- The average rate is T1 line 43500 "Total payable" over the salary (T1 line 10100), rounded once
  half-up to 0.0001 (`ca-bc/rate_rounding`).
- The marginal rate (`ca-bc/marginal_tax_rate`) is the exact sum of two gated parts: the federal
  marginal rate (`ca/federal_marginal_rate`, the T1 line 73 bracket rate, counted only where T1
  line 42900 "Basic federal tax" is above 0) and the British Columbia marginal rate
  (`ca-bc/british_columbia_marginal_rate`): the BC428 line 5 rate, or the line 12 rate when line 5
  is blank, plus the slope of the tax reduction, counted only where BC428 line 80 is above 0. CPP
  and EI are not counted.

The 2026 figures: the lowest British Columbia rate is 5.60% (up from 5.06%), the other rates are
unchanged (7.7%, 10.5%, 12.29% to 140,430 in table 1; 14.7%, 16.8%, 20.5% above it in table 2),
with the brackets at 50,363, 100,728, 115,648, 140,430, 190,405 and 265,545; the basic reduction
is 690 (up from 562) and the base amount 25,570 (up from 25,020), at the unchanged rate of 3.56%.
Inside the reduction's range a further dollar of income is taxed at 3.56 points more, so the
British Columbia part there is 5.60% + 3.56% = 9.16%. The federal rates are the 2026 ones
(14%, 20.5%, 26%, 29%, 33% from taxable income of 58,523, 117,045, 181,440 and 258,482).

Every expected figure is derived by hand from the form lines and the datasets (exact Decimal),
never read from the engine, and agrees with the pinned anchors (BC428 line 91 of 0.00, 282.49,
1,152.48, 3,293.84 and 19,079.61 at 20,000, 30,000, 40,000, 70,000 and 200,000 for 2026, and of
364.81, 3,162.39 and 19,230.76 at 30,000, 70,000 and 200,000 for 2025). The taxable income and the
net income are the salary less the CPP enhanced contribution (1% of the salary less 3,500 up to
74,600, plus 4% of the salary from 74,600 to 85,000, each to the cent). The federal tax after
credits (T1 line 42900) is the bracket tax less 14% of the basic personal amount (14,829 plus the
supplement of 1,623, reduced from a net income of 181,440 over 77,042), the CPP base contribution
(4.95% of the salary less 3,500), the EI premium (1.63% to 68,900) and the Canada employment
amount (1,501 or the salary if less); the credits are summed and multiplied by the rate once, as
the form does (rounding each credit separately would shift the 19,200.18 boundary). The British
Columbia tax (BC428 line 91, equal to line 80 here) is the bracket tax less 5.60% of the credits
of BC428 Part B, which here are the British Columbia basic personal amount of 13,216, the CPP base
contribution and the EI premium only (no Canada employment amount, no supplement), summed and
multiplied once, less the reduction of line 79. The total payable is their sum: for example
7,278.19 + 3,293.84 = 10,572.03 at 70,000.

The gates open at the zero-tax boundaries, found cent by cent from the same derivation (the part is
0 one cent below and counts at the cent pinned):

- federal: T1 line 42900 is 0.00 at 19,200.17 and 0.01 at 19,200.18;
- British Columbia: BC428 line 80 is 0.00 at 26,752.95 and 0.01 at 26,752.96, which is inside the
  tax reduction's range (the net income is 26,520.43), so the part is 5.60% + 3.56% = 9.16% where
  it opens.

The reduction's slope starts at a net income of 25,570.15 and ends at 44,951.88, not at the
printed 25,570.00 and 44,952.00: line 78 is a dollars-and-cents box (0.14 x 3.56% rounds to 0.00,
0.15 x 3.56% to 0.01), so line 78 is 0.00 up to a net income of 25,570.14 (a salary of 25,793.07);
and line 79 is 0.00 from a net income of 44,951.89 (a salary of 45,370.60, line 78 is then 690.00),
which is where the printed form already reads 0.
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
from tax_engine.registrations import artifact_kinds
from tests.kinds import bundled_kinds, non_negative

D = Decimal
BRITISH_COLUMBIA = JurisdictionCode("CA-BC")
RETURN = "ca-bc/return"
FEDERAL = "ca/federal_marginal_rate"
BC_RATE = "ca-bc/british_columbia_marginal_rate"
MARGINAL = "ca-bc/marginal_tax_rate"
AVERAGE = "ca-bc/average_income_tax_rate"
TOTAL_PAYABLE = "ca/total_payable"
LINE_5_RETURN = "ca-bc/british_columbia_bracket_rate_line_5_return"
LINE_12_RETURN = "ca-bc/british_columbia_bracket_rate_line_12_return"
BRACKET = "ca-bc/british_columbia_bracket_rate_return"
RATE_GATE = "ca-bc/british_columbia_rate_gate"
REDUCTION_GATE = "ca-bc/british_columbia_reduction_gate"
SLOPE = "ca-bc/british_columbia_reduction_slope"
PHASE_OUT = "ca-bc/british_columbia_reduction_phase_out_rate"
WITH_REDUCTION = "ca-bc/british_columbia_bracket_rate_with_reduction"
LINE_91 = "ca-bc/bc428_british_columbia_tax_line_91"
NEW_KINDS = [
    AVERAGE,
    MARGINAL,
    BC_RATE,
    LINE_5_RETURN,
    LINE_12_RETURN,
    BRACKET,
    "ca-bc/british_columbia_tax_after_reduction_return",
    RATE_GATE,
    "ca-bc/british_columbia_tax_reduction_return",
    REDUCTION_GATE,
    "ca-bc/british_columbia_reduction_clawback_return",
    SLOPE,
    PHASE_OUT,
    WITH_REDUCTION,
]

# Salary, federal part, British Columbia part, marginal rate, T1 line 43500 total payable, average.
FIGURES = [
    # Salaries of 0 and 100: no tax at all, both gates closed, and no division by zero.
    ("0", "0", "0", "0", "0.00", "0"),
    ("100", "0", "0", "0", "0.00", "0"),
    # Federal boundary: closed at 19,200.17, open (14%) at 19,200.18; British Columbia closed.
    ("19200.17", "0", "0", "0", "0.00", "0"),
    ("19200.18", "0.14", "0", "0.14", "0.01", "0"),
    # 20,000 (taxable income 19,835.00): the reduction of 690.00 takes the British Columbia tax of
    # 306.67 to 0.00, so the British Columbia part is 0. 103.49 / 20,000 = 0.005175 -> 0.0052.
    ("20000", "0.14", "0", "0.14", "103.49", "0.0052"),
    # British Columbia boundary: closed at 26,752.95, open at 26,752.96 (5.60% + 3.56% = 9.16%).
    ("26752.95", "0.14", "0", "0.14", "977.25", "0.0365"),
    ("26752.96", "0.14", "0.0916", "0.2316", "977.26", "0.0365"),
    # 30,000 (net income 29,735.00): inside the reduction range, 14% + 9.16% = 23.16%.
    # (1,397.37 + 282.49) / 30,000 = 0.055995 -> 0.0560.
    ("30000", "0.14", "0.0916", "0.2316", "1679.86", "0.0560"),
    # 40,000 (net income 39,635.00): inside the reduction range, 23.16%.
    # (2,691.25 + 1,152.48) / 40,000 = 0.096093 -> 0.0961.
    ("40000", "0.14", "0.0916", "0.2316", "3843.73", "0.0961"),
    # 45,000 (net income 44,585.00): still inside the range, which ends at 44,951.89.
    ("45000", "0.14", "0.0916", "0.2316", "4925.67", "0.1095"),
    # 46,000 (net income 45,575.00): past the end of the reduction, 5.60% only.
    ("46000", "0.14", "0.056", "0.196", "5119.89", "0.1113"),
    # 70,000 (taxable income 69,335.00): 20.5% federal, 7.7% (50,363 to 100,728). 10,572.03 /
    # 70,000 = 0.151029 -> 0.1510.
    ("70000", "0.205", "0.077", "0.282", "10572.03", "0.1510"),
    # 120,000 (taxable income 118,873.00): 26% federal, 12.29% (115,648 to 140,430).
    ("120000", "0.26", "0.1229", "0.3829", "25163.44", "0.2097"),
    # 150,000 (taxable income 148,873.00, above the table 1 limit of 140,430): the line 12 rate of
    # 14.7% is read.
    ("150000", "0.26", "0.147", "0.407", "36853.92", "0.2457"),
    # 200,000 (taxable income 198,873.00): 29% federal (above 181,440), line 12 rate of 16.8%
    # (190,405 to 265,545). 57,956.15 / 200,000 = 0.289781 -> 0.2898.
    ("200000", "0.29", "0.168", "0.458", "57956.15", "0.2898"),
]
PART_FIGURES = [(s, f, b, m) for s, f, b, m, _, _ in FIGURES]
AVERAGE_FIGURES = [(s, t, a) for s, _, _, _, t, a in FIGURES]
# Salary, BC428 line 5 and line 12 rates read (a blank is 0): taxable income 140,430.00 at 141,557
# is up to 140,430, and 140,430.01 at 141,557.01 is above it.
BRACKET_FIGURES = [
    ("70000", "0.077", "0"),
    ("120000", "0.1229", "0"),
    ("141557", "0.1229", "0"),
    ("141557.01", "0", "0.147"),
    ("200000", "0", "0.168"),
]
# Salary, net income, slope, reduction gate, phase-out rate, bracket rate with the reduction,
# British Columbia marginal rate. The slope is 3.56% where line 78 is above 0.00, the gate is 1
# where line 79 is above 0.00, and the British Columbia part is 0 below the line 80 boundary of
# 26,752.96 although the reduction is already in the bracket rate.
REDUCTION_FIGURES = [
    ("20000", "19835.00", "0", "1", "0", "0.056", "0"),
    ("25000", "24785.00", "0", "1", "0", "0.056", "0"),
    ("25793.07", "25570.14", "0", "1", "0", "0.056", "0"),
    ("25793.08", "25570.15", "0.0356", "1", "0.0356", "0.0916", "0"),
    ("30000", "29735.00", "0.0356", "1", "0.0356", "0.0916", "0.0916"),
    ("45370.59", "44951.88", "0.0356", "1", "0.0356", "0.0916", "0.0916"),
    ("45370.60", "44951.89", "0.0356", "0", "0", "0.056", "0.056"),
    ("46000", "45575.00", "0.0356", "0", "0", "0.056", "0.056"),
]


def _worksheets(salary: str, year: int = 2026) -> dict[str, tuple[Worksheet, ...]]:
    return build_tax_computation().compute(
        TaxCalculationRequest(BRITISH_COLUMBIA, year, (Artifact(EMPLOYMENT_INCOME, D(salary)),))
    )


def _summary(salary: str) -> Worksheet:
    (summary,) = _worksheets(salary)[RETURN]
    return summary


def _value(summary: Worksheet, name: str) -> Decimal:
    value = summary.get(artifact_kinds().kind(name)).value
    assert isinstance(value, Decimal)
    return value


def _sum_line(sheet: Worksheet) -> SumLine:
    """The one trace line of the marginal tax rate step, found by its output kind."""
    label = artifact_kinds().kind(MARGINAL).label
    (line,) = [
        line for line in sheet.trace if isinstance(line, SumLine) and line.output.label == label
    ]
    return line


@pytest.mark.parametrize("name", NEW_KINDS)
def test_the_new_kinds_are_registered_decimal_amounts(name: str) -> None:
    kind = artifact_kinds().kind(name)

    assert kind.identifier == name
    assert kind.value_type is Decimal


@pytest.mark.parametrize(
    "name", [MARGINAL, AVERAGE, BC_RATE, BRACKET, SLOPE, PHASE_OUT, WITH_REDUCTION]
)
def test_the_rate_kinds_are_non_negative(name: str) -> None:
    assert non_negative(artifact_kinds().kind(name))


@pytest.mark.parametrize(("salary", "federal", "british_columbia", "marginal"), PART_FIGURES)
def test_the_marginal_rate_is_the_exact_sum_of_the_federal_and_the_british_columbia_part(
    salary: str, federal: str, british_columbia: str, marginal: str
) -> None:
    summary = _summary(salary)

    assert _value(summary, FEDERAL) == D(federal)
    assert _value(summary, BC_RATE) == D(british_columbia)
    assert _value(summary, MARGINAL) == D(marginal)
    assert D(federal) + D(british_columbia) == D(marginal)


@pytest.mark.parametrize(("salary", "total_payable", "average"), AVERAGE_FIGURES)
def test_the_average_rate_is_the_total_payable_over_the_salary_half_up_to_ten_thousandths(
    salary: str, total_payable: str, average: str
) -> None:
    summary = _summary(salary)

    assert _value(summary, TOTAL_PAYABLE) == D(total_payable)
    assert _value(summary, AVERAGE) == D(average)
    if D(salary) > 0:
        assert (D(total_payable) / D(salary)).quantize(D("0.0001"), rounding="ROUND_HALF_UP") == D(
            average
        )


@pytest.mark.parametrize("salary", ["0", "100"])
def test_a_salary_of_0_or_100_reads_0_for_both_rates(salary: str) -> None:
    summary = _summary(salary)

    assert _value(summary, MARGINAL) == D("0")
    assert _value(summary, AVERAGE) == D("0")
    assert _value(summary, FEDERAL) == D("0")
    assert _value(summary, BC_RATE) == D("0")


def test_the_2026_average_at_70000_is_15_10_percent_and_the_marginal_28_2_percent() -> None:
    summary = _summary("70000")

    assert _value(summary, TOTAL_PAYABLE) == D("10572.03")
    assert _value(summary, AVERAGE) == D("0.1510")
    assert _value(summary, MARGINAL) == D("0.282")


@pytest.mark.parametrize(("salary", "line_5", "line_12"), BRACKET_FIGURES)
def test_line_12_supplies_the_rate_above_the_table_1_limit_and_line_5_below_it(
    salary: str, line_5: str, line_12: str
) -> None:
    summary = _summary(salary)

    assert _value(summary, LINE_5_RETURN) == D(line_5)
    assert _value(summary, LINE_12_RETURN) == D(line_12)
    assert _value(summary, BRACKET) == D(line_5) + D(line_12)


@pytest.mark.parametrize(
    ("salary", "net_income", "slope", "gate", "phase_out", "with_reduction", "british_columbia"),
    REDUCTION_FIGURES,
)
def test_the_reduction_slope_runs_from_a_net_income_over_25570_to_just_under_44952(
    salary: str,
    net_income: str,
    slope: str,
    gate: str,
    phase_out: str,
    with_reduction: str,
    british_columbia: str,
) -> None:
    (bc428,) = _worksheets(salary)["ca-bc/bc428"]
    summary = _summary(salary)

    assert _value(bc428, "ca-bc/bc428_net_income_line_74") == D(net_income)
    assert _value(summary, SLOPE) == D(slope)
    assert _value(summary, REDUCTION_GATE) == D(gate)
    assert _value(summary, PHASE_OUT) == D(phase_out)
    assert _value(summary, WITH_REDUCTION) == D(with_reduction)
    assert _value(summary, BC_RATE) == D(british_columbia)


@pytest.mark.parametrize("salary", ["30000", "40000"])
def test_inside_the_reduction_range_the_provincial_part_is_the_bracket_rate_plus_3_56_points(
    salary: str,
) -> None:
    summary = _summary(salary)

    assert _value(summary, BRACKET) == D("0.056")
    assert _value(summary, PHASE_OUT) == D("0.0356")
    assert _value(summary, BC_RATE) == D("0.0916")
    assert _value(summary, MARGINAL) == D("0.14") + D("0.0916")


def test_the_british_columbia_gate_closes_the_part_while_the_reduction_is_still_in_the_rate() -> (
    None
):
    summary = _summary("26752.95")

    assert _value(summary, WITH_REDUCTION) == D("0.0916")
    assert _value(summary, RATE_GATE) == D("0")
    assert _value(summary, BC_RATE) == D("0")
    assert _value(summary, MARGINAL) == D("0.14")


def test_the_marginal_rate_is_not_rounded_to_the_cent() -> None:
    # 0.14 + 0.0916 = 0.2316 keeps its fourth place: no cent rule is applied to a rate.
    value = _value(_summary("26752.96"), MARGINAL)

    assert value == D("0.2316")
    assert value.as_tuple().exponent == -4


@pytest.mark.parametrize(
    ("salary", "line_91"),
    [
        ("20000", "0.00"),
        ("30000", "282.49"),
        ("40000", "1152.48"),
        ("70000", "3293.84"),
        ("200000", "19079.61"),
    ],
)
def test_the_2026_british_columbia_tax_anchors_do_not_move(salary: str, line_91: str) -> None:
    (bc428,) = _worksheets(salary)["ca-bc/bc428"]

    assert _value(bc428, LINE_91) == D(line_91)


@pytest.mark.parametrize(
    ("salary", "line_91"),
    [("30000", "364.81"), ("70000", "3162.39"), ("200000", "19230.76")],
)
def test_the_2025_british_columbia_tax_anchors_do_not_move(salary: str, line_91: str) -> None:
    (bc428,) = _worksheets(salary, 2025)["ca-bc/bc428"]

    assert _value(bc428, LINE_91) == D(line_91)


def test_the_return_prints_both_rates_as_percentages_in_the_core_percent_unit() -> None:
    summary = _summary("70000")
    kinds = artifact_kinds()

    for name in (MARGINAL, AVERAGE):
        unit = summary.unit(kinds.kind(name).label)
        assert unit is not None
        assert unit.identifier == "core/percent"


def test_the_steps_after_line_167_have_no_reference_and_no_title() -> None:
    summary = _summary("70000")
    kinds = artifact_kinds()

    for name in NEW_KINDS:
        label = kinds.kind(name).label
        assert summary.reference(label) is None
        assert summary.title(label) is None


def test_the_marginal_rate_is_traced_as_one_exact_sum_of_the_federal_then_the_bc_part() -> None:
    sheet = _summary("200000")
    kinds = artifact_kinds()

    line = _sum_line(sheet)

    assert [(kind.label, value) for kind, value in line.parts] == [
        (kinds.kind(FEDERAL).label, D("0.29")),
        (kinds.kind(BC_RATE).label, D("0.168")),
    ]
    assert line.rounding == NO_ROUNDING
    assert line.total == D("0.458")
    assert line.amount == sheet.get(kinds.kind(MARGINAL)).value


def test_the_marginal_rate_is_explained_in_english_as_percentages() -> None:
    sheet = _summary("70000")

    text = EnglishTraceRenderer().render(_sum_line(sheet), sheet)

    assert re.fullmatch(
        r".*\(20\.5%\) plus .+ \(7\.7(0+)?%\) gives 28\.2(0+)?% \(not rounded\)\.?", text
    )


def test_the_marginal_rate_comes_last_in_the_trace() -> None:
    sheet = _summary("100000")
    kinds = artifact_kinds()
    labels = [line.label for line in sheet.trace]

    marginal = labels.index(kinds.kind(MARGINAL).label)

    assert marginal == len(labels) - 1
    assert labels.count(kinds.kind(MARGINAL).label) == 1
    for part in (FEDERAL, BC_RATE):
        assert labels.index(kinds.kind(part).label) < marginal


def test_the_ontario_and_alberta_anchors_do_not_move() -> None:
    # Ontario 2025 at 70,000: take-home is the salary less CPP, EI and T1 line 167, 53,468.68.
    # Alberta 2025 at 70,000: AB428 line 75 is 3,598.12.
    kinds = bundled_kinds()
    service = build_tax_computation()
    ontario = service.compute(
        TaxCalculationRequest(
            JurisdictionCode("CA-ON"), 2025, (Artifact(EMPLOYMENT_INCOME, D("70000")),)
        )
    )
    (schedule_8,) = ontario["ca/schedule_8"]
    (t2204,) = ontario["ca/t2204"]
    (summary,) = ontario["ca-on/return"]
    cpp = (
        schedule_8.get(kinds.kind("ca/schedule_8_cpp_base_contributions_on_return")).value
        + schedule_8.get(kinds.kind("ca/schedule_8_cpp_enhanced_contributions_on_return")).value
    )
    ei = t2204.get(kinds.kind("ca/t2204_premiums_deducted")).value
    line_167 = summary.get(kinds.kind("ca/refund_or_balance_owing")).value
    alberta = service.compute(
        TaxCalculationRequest(
            JurisdictionCode("CA-AB"), 2025, (Artifact(EMPLOYMENT_INCOME, D("70000")),)
        )
    )
    (ab428,) = alberta["ca-ab/ab428"]

    assert D("70000") - cpp - ei - line_167 == D("53468.68")
    assert ab428.get(kinds.kind("ca-ab/ab428_alberta_tax_line_75")).value == D("3598.12")
