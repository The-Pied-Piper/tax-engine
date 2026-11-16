"""The British Columbia return summary carries the average and the marginal income tax rate (2025),
through the real engine (the real British Columbia manifest over the British Columbia package list,
which stands in for `registrations.JURISDICTIONS` until British Columbia is listed; salary the only
input).

Calculated the same way as Alberta's and Ontario's, with the British Columbia tax reduction:

- The average rate is T1 line 43500 "Total payable" over the salary (T1 line 10100), rounded once
  half-up to 0.0001 (`ca-bc/rate_rounding`).
- The marginal rate (`ca-bc/marginal_tax_rate`) is the exact sum of two gated parts: the federal
  marginal rate (`ca/federal_marginal_rate`, the T1 line 73 bracket rate, counted only where T1
  line 42900 "Basic federal tax" is above 0) and the British Columbia marginal rate
  (`ca-bc/british_columbia_marginal_rate`): the BC428 line 5 rate, or the line 12 rate when line 5
  is blank, plus the slope of the tax reduction, counted only where BC428 line 80 is above 0. CPP
  and EI are not counted.

Form text (Form BC428, CRA 5010-c-25e.txt): "Line 5: Rate 5.06%", "Rate 7.7%", "Rate 10.5%", "Rate
12.29%" (table 1, "Line 1 is $49,279 or less" to "more than $113,158 but not more than $137,407");
"Line 12: Rate 14.7%", "Rate 16.8%", "Rate 20.5%" (table 2, above $137,407); "Line 73: Basic
reduction Claim $562", "Line 75: Base amount 25,020.00", "Line 77: Applicable rate 3.56%", "Line 78:
Line 76 multiplied by the percentage from line 77", "Line 79: Line 73 minus line 78 (if negative,
enter "0") British Columbia tax reduction", "Line 80: Line 72 minus line 79 (if negative, enter
"0")". T4127 (January 2025), British Columbia: "S = Where $25,020 < A <= $40,807, S is equal to the
lesser of ... $562 - [(A - $25,020) x 3.56%]". S falls as income rises, so inside that range a
further dollar of income is taxed at 3.56 points more: the British Columbia part is 5.06% + 3.56% =
8.62% at a net income between 25,020 and 40,807 (while line 80 is above zero), not 5.06%.

Every expected figure is derived by hand from the printed form lines and the federal and British
Columbia datasets (exact Decimal), never read from the engine, and agrees with the existing pinned
anchors (BC428 line 91 of 364.81, 3,162.39 and 19,230.76 at 30,000, 70,000 and 200,000). The
taxable income and the net income are the salary less the CPP enhanced contribution (1% of the
salary less 3,500, to the cent; there is no second additional contribution below 71,300). The
total payable is the federal tax after credits (T1 line 42900) plus the British Columbia tax (BC428
line 91, equal to line 80 here): for example 7,585.64 + 3,162.39 = 10,748.03 at 70,000.

The gates open at the zero-tax boundaries, found cent by cent from the same derivation (the part is
0 one cent below and counts at the cent pinned):

- federal: T1 line 42900 is 0.00 at 18,820.26 and 0.01 at 18,820.27;
- British Columbia: BC428 line 80 is 0.00 at 25,551.24 and 0.01 at 25,551.25, which is inside the
  tax reduction's range (the net income is 25,330.74), so the part is 5.06% + 3.56% = 8.62% where it
  opens.

The reduction's slope starts at a net income of 25,020.15 and ends at 40,806.38, not at the printed
25,020.00 and 40,807.00: line 78 is a dollars-and-cents box (0.14 x 3.56% rounds to 0.00, 0.15 x
3.56% to 0.01), so line 78 is 0.00 up to a net income of 25,020.14; and line 79 is 0.00 from a net
income of 40,806.38 (line 78 is then 562.00), which is where the printed form already reads 0.
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
from tests.jurisdictions.ca_bc.support import british_columbia_kinds, british_columbia_service
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
    # Federal boundary: closed at 18,820.26, open (14.5%) at 18,820.27; British Columbia closed.
    ("18820.26", "0", "0", "0", "0.00", "0"),
    ("18820.27", "0.145", "0", "0.145", "0.01", "0"),
    # 20,000 (taxable income 19,835.00): the reduction of 562.00 takes the British Columbia tax of
    # 291.37 to 0.00, so the British Columbia part is 0.
    ("20000", "0.145", "0", "0.145", "158.09", "0.0079"),
    # British Columbia boundary: closed at 25,551.24, open at 25,551.25 (5.06% + 3.56% = 8.62%).
    ("25551.24", "0.145", "0", "0.145", "901.93", "0.0353"),
    ("25551.25", "0.145", "0.0862", "0.2312", "901.94", "0.0353"),
    # 30,000 (net income 29,735.00): inside the reduction range, 14.5% + 8.62% = 23.12%.
    # (1,498.04 + 364.81) / 30,000 = 0.062095 -> 0.0621.
    ("30000", "0.145", "0.0862", "0.2312", "1862.85", "0.0621"),
    # 45,000 (net income 44,585.00): past the end of the reduction, 5.06% only.
    ("45000", "0.145", "0.0506", "0.1956", "4968.30", "0.1104"),
    # 70,000 (taxable income 69,335.00): 20.5% federal, 7.7% (49,279 to 98,560). 10,748.03 /
    # 70,000 = 0.153543 -> 0.1535.
    ("70000", "0.205", "0.077", "0.282", "10748.03", "0.1535"),
    # 120,000 (taxable income 118,926.00): 26% federal, 12.29% (113,158 to 137,407).
    ("120000", "0.26", "0.1229", "0.3829", "25623.27", "0.2135"),
    # 150,000 (taxable income 148,926.00, above the table 1 limit of 137,407): the line 12 rate of
    # 14.7% is read.
    ("150000", "0.26", "0.147", "0.407", "37387.88", "0.2493"),
    # 200,000 (taxable income 198,926.00): 29% federal (above 177,882), line 12 rate of 16.8%
    # (186,306 to 259,829). 58,698.50 / 200,000 = 0.293493 -> 0.2935.
    ("200000", "0.29", "0.168", "0.458", "58698.50", "0.2935"),
]
PART_FIGURES = [(s, f, b, m) for s, f, b, m, _, _ in FIGURES]
AVERAGE_FIGURES = [(s, t, a) for s, _, _, _, t, a in FIGURES]
# Salary, BC428 line 5 and line 12 rates read (a blank is 0): taxable income 137,407.00 at 138,481
# is up to 137,407, and 137,447.00 at 138,800 is above it.
BRACKET_FIGURES = [
    ("70000", "0.077", "0"),
    ("120000", "0.1229", "0"),
    ("138481", "0.1229", "0"),
    ("138800", "0", "0.147"),
    ("200000", "0", "0.168"),
]
# Salary, net income, slope, reduction gate, phase-out rate, bracket rate with the reduction,
# British Columbia marginal rate. The slope is 3.56% where line 78 is above 0.00, the gate is 1
# where line 79 is above 0.00, and the British Columbia part is 0 below the line 80 boundary of
# 25,551.25 although the reduction is already in the bracket rate.
REDUCTION_FIGURES = [
    ("20000", "19835.00", "0", "1", "0", "0.0506", "0"),
    ("25000", "24785.00", "0", "1", "0", "0.0506", "0"),
    ("25237.37", "25020.00", "0", "1", "0", "0.0506", "0"),
    ("25237.52", "25020.14", "0", "1", "0", "0.0506", "0"),
    ("25237.53", "25020.15", "0.0356", "1", "0.0356", "0.0862", "0"),
    ("30000", "29735.00", "0.0356", "1", "0.0356", "0.0862", "0.0862"),
    ("41183.20", "40806.37", "0.0356", "1", "0.0356", "0.0862", "0.0862"),
    ("41183.21", "40806.38", "0.0356", "0", "0", "0.0506", "0.0506"),
    ("45000", "44585.00", "0.0356", "0", "0", "0.0506", "0.0506"),
]


def _worksheets(salary: str) -> dict[str, tuple[Worksheet, ...]]:
    return british_columbia_service().compute(
        BRITISH_COLUMBIA, 2025, Artifact(EMPLOYMENT_INCOME, D(salary))
    )


def _summary(salary: str) -> Worksheet:
    (summary,) = _worksheets(salary)[RETURN]
    return summary


def _value(summary: Worksheet, name: str) -> Decimal:
    value = summary.get(british_columbia_kinds().kind(name)).value
    assert isinstance(value, Decimal)
    return value


def _sum_line(sheet: Worksheet) -> SumLine:
    """The one trace line of the marginal tax rate step, found by its output kind."""
    label = british_columbia_kinds().kind(MARGINAL).label
    (line,) = [
        line for line in sheet.trace if isinstance(line, SumLine) and line.output.label == label
    ]
    return line


@pytest.mark.parametrize("name", NEW_KINDS)
def test_the_new_kinds_are_registered_decimal_amounts(name: str) -> None:
    kind = british_columbia_kinds().kind(name)

    assert kind.identifier == name
    assert kind.value_type is Decimal


@pytest.mark.parametrize(
    "name", [MARGINAL, AVERAGE, BC_RATE, BRACKET, SLOPE, PHASE_OUT, WITH_REDUCTION]
)
def test_the_rate_kinds_are_non_negative(name: str) -> None:
    assert non_negative(british_columbia_kinds().kind(name))


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


def test_the_2025_average_at_70000_is_15_35_percent() -> None:
    summary = _summary("70000")

    assert _value(summary, TOTAL_PAYABLE) == D("10748.03")
    assert _value(summary, AVERAGE) == D("0.1535")


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
def test_the_reduction_slope_runs_from_a_net_income_over_25020_to_just_under_40807(
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


def test_inside_the_reduction_range_the_provincial_part_is_the_bracket_rate_plus_3_56_points() -> (
    None
):
    summary = _summary("30000")

    assert _value(summary, BRACKET) == D("0.0506")
    assert _value(summary, PHASE_OUT) == D("0.0356")
    assert _value(summary, BC_RATE) == D("0.0862")
    assert _value(summary, MARGINAL) == D("0.145") + D("0.0862")


def test_the_british_columbia_gate_closes_the_part_while_the_reduction_is_still_in_the_rate() -> (
    None
):
    summary = _summary("25237.53")

    assert _value(summary, WITH_REDUCTION) == D("0.0862")
    assert _value(summary, RATE_GATE) == D("0")
    assert _value(summary, BC_RATE) == D("0")
    assert _value(summary, MARGINAL) == D("0.145")


def test_the_marginal_rate_is_not_rounded_to_the_cent() -> None:
    # 0.145 + 0.0862 = 0.2312 keeps its fourth place: no cent rule is applied to a rate.
    value = _value(_summary("25551.25"), MARGINAL)

    assert value == D("0.2312")
    assert value.as_tuple().exponent == -4


def test_the_return_prints_both_rates_as_percentages_in_the_core_percent_unit() -> None:
    summary = _summary("70000")
    kinds = british_columbia_kinds()

    for name in (MARGINAL, AVERAGE):
        unit = summary.unit(kinds.kind(name).label)
        assert unit is not None
        assert unit.identifier == "core/percent"


def test_the_steps_after_line_167_have_no_reference_and_no_title() -> None:
    summary = _summary("70000")
    kinds = british_columbia_kinds()

    for name in NEW_KINDS:
        label = kinds.kind(name).label
        assert summary.reference(label) is None
        assert summary.title(label) is None


def test_the_marginal_rate_is_traced_as_one_exact_sum_of_the_federal_then_the_bc_part() -> None:
    sheet = _summary("200000")
    kinds = british_columbia_kinds()

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
    kinds = british_columbia_kinds()
    labels = [line.label for line in sheet.trace]

    marginal = labels.index(kinds.kind(MARGINAL).label)

    assert marginal == len(labels) - 1
    assert labels.count(kinds.kind(MARGINAL).label) == 1
    for part in (FEDERAL, BC_RATE):
        assert labels.index(kinds.kind(part).label) < marginal


@pytest.mark.parametrize(
    ("salary", "line_91"),
    [("30000", "364.81"), ("70000", "3162.39"), ("200000", "19230.76")],
)
def test_the_british_columbia_tax_anchors_do_not_move(salary: str, line_91: str) -> None:
    worksheets = british_columbia_service().compute(
        BRITISH_COLUMBIA, 2025, Artifact(EMPLOYMENT_INCOME, D(salary))
    )
    (bc428,) = worksheets["ca-bc/bc428"]

    assert bc428.get(british_columbia_kinds().kind(LINE_91)).value == D(line_91)


def test_the_ontario_and_alberta_anchors_do_not_move() -> None:
    # Ontario 2025 at 70,000: take-home is the salary less CPP, EI and T1 line 167, 53,468.68.
    # Alberta 2025 at 70,000: AB428 line 75 is 3,598.12.
    kinds = bundled_kinds()
    service = build_tax_computation()
    ontario = service.compute(
        JurisdictionCode("CA-ON"), 2025, Artifact(EMPLOYMENT_INCOME, D("70000"))
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
        JurisdictionCode("CA-AB"), 2025, Artifact(EMPLOYMENT_INCOME, D("70000"))
    )
    (ab428,) = alberta["ca-ab/ab428"]

    assert D("70000") - cpp - ei - line_167 == D("53468.68")
    assert ab428.get(kinds.kind("ca-ab/ab428_alberta_tax_line_75")).value == D("3598.12")
