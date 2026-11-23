"""The Saskatchewan return summary carries the average and the marginal income tax rate (2025),
through the registered engine (`build_tax_computation`, which lists Saskatchewan; salary the only
input).

Calculated the same way as British Columbia's, without a tax reduction (Saskatchewan has none: Form
SK428 line 9 prints a flat "Claim $19,491", and the payroll formulas have the one constant K1P):

- The average rate is T1 line 43500 "Total payable" over the salary (T1 line 10100), rounded once
  half-up to 0.0001 (`ca-sk/rate_rounding`).
- The marginal rate (`ca-sk/marginal_tax_rate`) is the exact sum of two gated parts: the federal
  marginal rate (`ca/federal_marginal_rate`, the T1 line 73 bracket rate, counted only where T1
  line 42900 "Basic federal tax" is above 0) and the Saskatchewan marginal rate
  (`ca-sk/saskatchewan_marginal_rate`, the SK428 line 5 rate, counted only where SK428 line 67 is
  above 0). CPP and EI are not counted.

Form text (Form SK428, CRA 5008-C): "Column 1: Line 1 is $53,463 or less", "Column 2: Line 1 is more
than $53,463 but not more than $152,750", "Column 3: Line 1 is more than $152,750"; "Line 5: Rate
10.5%", "Line 5: Rate 12.5%", "Line 5: Rate 14.5%"; "Line 9 and line 58040: Basic personal amount
Claim $19,491"; "Line 52: Saskatchewan non-refundable tax credit rate 10.5%"; "Line 67: Line 62
minus line 66 (if negative, enter "0")". Federal rates (T1 General, 5000-R): 14.5% to 57,375, 20.5%
to 114,750, 26% to 177,882, 29% to 253,414, 33% above.

Every expected figure is derived by hand from the printed form lines and the federal and
Saskatchewan datasets (exact Decimal), never read from the engine. Taxable income is the salary
less the CPP enhanced contributions (1% of the salary less 3,500, to the cent, plus 4% of the
salary between 71,300 and 81,200 at the top; at 200,000 the sum is 678.00 + 396.00 = 1,074.00).

Worked at 70,000 (taxable income 69,335.00):

- federal: 8,319.38 + 20.5% of (69,335.00 - 57,375) = 8,319.38 + 2,451.80 = 10,771.18; credits
  at 14.5% of (16,129.00 + CPP 3,291.75 + EI 1,077.48 + Canada employment amount 1,471.00) =
  3,185.54; tax 7,585.64.
- Saskatchewan: column 2, 5,613.62 + 12.5% of (69,335.00 - 53,463) = 5,613.62 + 1,984.00 =
  7,597.62 (line 8); credits at 10.5% of (19,491.00 + 3,291.75 + 1,077.48) = 2,505.32 (line 53);
  line 67 = 5,092.30.
- total payable 7,585.64 + 5,092.30 = 12,677.94; average 12,677.94 / 70,000 = 0.181113 -> 0.1811.

The gates open at the zero-tax boundaries, found cent by cent from the same derivation (the part
is 0 one cent below and counts at the cent pinned):

- federal: T1 line 42900 is 0.00 at 18,820.26 and 0.01 at 18,820.27;
- Saskatchewan: SK428 line 67 is 0.00 at 20,866.57 (line 8 and line 53 are both 2,172.75) and
  0.01 at 20,866.58 (line 8 is 2,172.76), the salary at which Saskatchewan tax first exceeds zero;
  it stays above 0.00 for every cent from there on.

The column boundaries: line 1 (taxable income) is exactly 53,463.00 at a salary of 53,967.68 and
exactly 152,750.00 at a salary of 153,824.00; a line 1 exactly at a column's upper bound is in the
lower column, so the next cent of salary reads the next column's rate.
"""

from __future__ import annotations

import re
from decimal import ROUND_HALF_UP, Decimal

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
from tests.kinds import non_negative

D = Decimal
SASKATCHEWAN = JurisdictionCode("CA-SK")
RETURN = "ca-sk/return"
SK428 = "ca-sk/sk428"
FEDERAL = "ca/federal_marginal_rate"
SK_RATE = "ca-sk/saskatchewan_marginal_rate"
MARGINAL = "ca-sk/marginal_tax_rate"
AVERAGE = "ca-sk/average_income_tax_rate"
TOTAL_PAYABLE = "ca/total_payable"
BRACKET = "ca-sk/saskatchewan_bracket_rate_return"
LINE_67_RETURN = "ca-sk/saskatchewan_tax_after_credits_return"
RATE_GATE = "ca-sk/saskatchewan_rate_gate"
LINE_67 = "ca-sk/sk428_tax_after_credits_line_67"
LINE_82 = "ca-sk/sk428_saskatchewan_tax_line_82"
NEW_KINDS = [
    AVERAGE,
    MARGINAL,
    SK_RATE,
    BRACKET,
    LINE_67_RETURN,
    RATE_GATE,
]

# Salary, federal tax (T1 line 42900), Saskatchewan tax (SK428 line 67), federal part,
# Saskatchewan part, marginal rate, T1 line 43500 total payable, average.
FIGURES = [
    # 100 (taxable income 100.00): no tax at all, both gates closed.
    ("100", "0.00", "0.00", "0", "0", "0", "0.00", "0"),
    # Federal boundary: closed at 18,820.26, open (14.5%) at 18,820.27; Saskatchewan closed.
    ("18820.26", "0.00", "0.00", "0", "0", "0", "0.00", "0"),
    ("18820.27", "0.01", "0.00", "0.145", "0", "0.145", "0.01", "0"),
    # 20,000 (taxable income 19,835.00): line 8 2,082.68 is under the credits of 2,166.75, so line
    # 67 is 0.00. 158.09 / 20,000 = 0.0079045 -> 0.0079.
    ("20000", "158.09", "0.00", "0.145", "0", "0.145", "158.09", "0.0079"),
    # Saskatchewan boundary: closed at 20,866.57, open at 20,866.58 (14.5% + 10.5% = 25%).
    ("20866.57", "274.20", "0.00", "0.145", "0", "0.145", "274.20", "0.0131"),
    ("20866.58", "274.20", "0.01", "0.145", "0.105", "0.25", "274.21", "0.0131"),
    # 50,000 (taxable income 49,535.00, column 1): 14.5% + 10.5%. 7,004.77 / 50,000 = 0.1400954.
    ("50000", "4177.93", "2826.84", "0.145", "0.105", "0.25", "7004.77", "0.1401"),
    # Column 1 / column 2 boundary: taxable income 53,463.00 is in column 1, 53,463.01 in column 2.
    ("53967.68", "4709.57", "3211.83", "0.145", "0.105", "0.25", "7921.40", "0.1468"),
    ("53967.69", "4709.57", "3211.83", "0.145", "0.125", "0.27", "7921.40", "0.1468"),
    # 70,000 (taxable income 69,335.00, column 2): 20.5% + 12.5%. 12,677.94 / 70,000 = 0.181113.
    ("70000", "7585.64", "5092.30", "0.205", "0.125", "0.33", "12677.94", "0.1811"),
    # Column 2 / column 3 boundary: taxable income 152,750.00 is in column 2, 152,750.01 in
    # column 3.
    ("153824", "26766.38", "15512.42", "0.26", "0.125", "0.385", "42278.80", "0.2749"),
    ("153824.01", "26766.38", "15512.41", "0.26", "0.145", "0.405", "42278.79", "0.2749"),
    # 200,000 (taxable income 198,926.00, column 3, federal 29%): 14.5% Saskatchewan.
    # 61,675.67 / 200,000 = 0.30837835 -> 0.3084.
    ("200000", "39467.74", "22207.93", "0.29", "0.145", "0.435", "61675.67", "0.3084"),
]
PART_FIGURES = [(s, f, k, m) for s, _, _, f, k, m, _, _ in FIGURES]
AVERAGE_FIGURES = [(s, t, a) for s, _, _, _, _, _, t, a in FIGURES]
TAX_FIGURES = [(s, f, k, t) for s, f, k, _, _, _, t, _ in FIGURES]


def _worksheets(salary: str) -> dict[str, tuple[Worksheet, ...]]:
    return build_tax_computation().compute(
        TaxCalculationRequest(SASKATCHEWAN, 2025, (Artifact(EMPLOYMENT_INCOME, D(salary)),))
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


@pytest.mark.parametrize("name", [MARGINAL, AVERAGE, SK_RATE, BRACKET])
def test_the_rate_kinds_are_non_negative(name: str) -> None:
    assert non_negative(artifact_kinds().kind(name))


@pytest.mark.parametrize(("salary", "federal", "saskatchewan", "marginal"), PART_FIGURES)
def test_the_marginal_rate_is_the_exact_sum_of_the_federal_and_the_saskatchewan_part(
    salary: str, federal: str, saskatchewan: str, marginal: str
) -> None:
    summary = _summary(salary)

    assert _value(summary, FEDERAL) == D(federal)
    assert _value(summary, SK_RATE) == D(saskatchewan)
    assert _value(summary, MARGINAL) == D(marginal)
    assert D(federal) + D(saskatchewan) == D(marginal)


@pytest.mark.parametrize(
    ("salary", "federal_tax", "saskatchewan_tax", "total_payable"), TAX_FIGURES
)
def test_the_total_payable_is_the_federal_tax_plus_the_saskatchewan_tax(
    salary: str, federal_tax: str, saskatchewan_tax: str, total_payable: str
) -> None:
    worksheets = _worksheets(salary)
    (sk428,) = worksheets[SK428]
    summary = _summary(salary)

    assert D(federal_tax) + D(saskatchewan_tax) == D(total_payable)
    assert _value(sk428, LINE_67) == D(saskatchewan_tax)
    assert _value(sk428, LINE_82) == D(saskatchewan_tax)
    assert _value(summary, LINE_67_RETURN) == D(saskatchewan_tax)
    assert _value(summary, TOTAL_PAYABLE) == D(total_payable)


@pytest.mark.parametrize(("salary", "total_payable", "average"), AVERAGE_FIGURES)
def test_the_average_rate_is_the_total_payable_over_the_salary_half_up_to_ten_thousandths(
    salary: str, total_payable: str, average: str
) -> None:
    summary = _summary(salary)

    assert _value(summary, TOTAL_PAYABLE) == D(total_payable)
    assert _value(summary, AVERAGE) == D(average)
    assert (D(total_payable) / D(salary)).quantize(D("0.0001"), rounding=ROUND_HALF_UP) == D(
        average
    )


def test_a_salary_of_100_reads_0_for_both_rates_and_both_parts() -> None:
    summary = _summary("100")

    assert _value(summary, MARGINAL) == D("0")
    assert _value(summary, AVERAGE) == D("0")
    assert _value(summary, FEDERAL) == D("0")
    assert _value(summary, SK_RATE) == D("0")
    assert _value(summary, RATE_GATE) == D("0")


def test_saskatchewan_tax_first_exceeds_zero_at_20866_58_and_the_gate_opens_there() -> None:
    closed = _summary("20866.57")
    opened = _summary("20866.58")

    assert _value(closed, LINE_67_RETURN) == D("0.00")
    assert _value(closed, RATE_GATE) == D("0")
    assert _value(opened, LINE_67_RETURN) == D("0.01")
    assert _value(opened, RATE_GATE) == D("1")
    assert _value(opened, SK_RATE) == D("0.105")


@pytest.mark.parametrize(
    ("salary", "line_1", "bracket"),
    [
        ("20000", "19835.00", "0.105"),
        ("50000", "49535.00", "0.105"),
        ("53967.68", "53463.00", "0.105"),
        ("53967.69", "53463.01", "0.125"),
        ("70000", "69335.00", "0.125"),
        ("153824", "152750.00", "0.125"),
        ("153824.01", "152750.01", "0.145"),
        ("200000", "198926.00", "0.145"),
    ],
)
def test_the_line_5_rate_is_the_one_of_the_column_that_taxable_income_falls_in(
    salary: str, line_1: str, bracket: str
) -> None:
    (sk428_credits,) = _worksheets(salary)["ca-sk/sk428_credits"]
    summary = _summary(salary)

    assert _value(sk428_credits, "ca-sk/sk428_taxable_income_line_1") == D(line_1)
    assert _value(summary, BRACKET) == D(bracket)


def test_the_marginal_rate_is_not_rounded_to_the_cent() -> None:
    # 0.145 + 0.125 = 0.27 and 0.26 + 0.125 = 0.385 keep their places: no cent rule is applied.
    value = _value(_summary("153824"), MARGINAL)

    assert value == D("0.385")
    assert value.as_tuple().exponent == -3


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


def test_the_marginal_rate_is_traced_as_one_exact_sum_of_the_federal_then_the_sk_part() -> None:
    sheet = _summary("200000")
    kinds = artifact_kinds()

    line = _sum_line(sheet)

    assert [(kind.label, value) for kind, value in line.parts] == [
        (kinds.kind(FEDERAL).label, D("0.29")),
        (kinds.kind(SK_RATE).label, D("0.145")),
    ]
    assert line.rounding == NO_ROUNDING
    assert line.total == D("0.435")
    assert line.amount == sheet.get(kinds.kind(MARGINAL)).value


def test_the_marginal_rate_is_explained_in_english_as_percentages() -> None:
    sheet = _summary("70000")

    text = EnglishTraceRenderer().render(_sum_line(sheet), sheet)

    assert re.fullmatch(
        r".*\(20\.5(0+)?%\) plus .+ \(12\.5(0+)?%\) gives 33(\.0+)?% \(not rounded\)\.?", text
    )


def test_the_marginal_rate_comes_last_in_the_trace() -> None:
    sheet = _summary("100000")
    kinds = artifact_kinds()
    labels = [line.label for line in sheet.trace]

    marginal = labels.index(kinds.kind(MARGINAL).label)

    assert marginal == len(labels) - 1
    assert labels.count(kinds.kind(MARGINAL).label) == 1
    for part in (FEDERAL, SK_RATE):
        assert labels.index(kinds.kind(part).label) < marginal


@pytest.mark.parametrize(
    ("salary", "line_82"),
    [("20000", "0.00"), ("70000", "5092.30"), ("200000", "22207.93")],
)
def test_the_saskatchewan_tax_anchors_do_not_move(salary: str, line_82: str) -> None:
    (sk428,) = _worksheets(salary)[SK428]

    assert _value(sk428, LINE_82) == D(line_82)


@pytest.mark.parametrize(
    ("salary", "line_167"),
    [("20000", "-1474.91"), ("70000", "12677.94"), ("200000", "61675.67")],
)
def test_the_line_167_anchors_do_not_move(salary: str, line_167: str) -> None:
    assert _value(_summary(salary), "ca/refund_or_balance_owing") == D(line_167)
