"""The Saskatchewan return summary carries the average and the marginal income tax rate (2026),
through the registered engine (`build_tax_computation`, which lists Saskatchewan; salary the only
input, every optional input blank).

The Saskatchewan 2026 datasets are PROVISIONAL: the 2026 Form SK428 (CRA 5008-C) is not yet
published, and the figures come from T4127 (January 2026) or are carried forward or derived from
2025. Every figure pinned here follows those provisional datasets and was derived by hand; it must
be re-checked when CRA publishes the 2026 forms.

The rates are calculated the same way as for 2025 (see `test_return_rates.py`), with the 2026
figures:

- The average rate is T1 line 43500 "Total payable" over the salary (T1 line 10100), rounded once
  half-up to 0.0001 (`ca-sk/rate_rounding`).
- The marginal rate (`ca-sk/marginal_tax_rate`) is the exact sum of two gated parts: the federal
  marginal rate (`ca/federal_marginal_rate`, the T1 line 73 bracket rate, counted only where T1
  line 42900 "Basic federal tax" is above 0) and the Saskatchewan marginal rate
  (`ca-sk/saskatchewan_marginal_rate`, the SK428 line 5 rate, counted only where SK428 line 67 is
  above 0). CPP and EI are not counted.

The 2026 figures: the Saskatchewan columns end at taxable income of 54,532 and 155,805 (up from
53,463 and 152,750) at the unchanged rates of 10.5%, 12.5% and 14.5%; the basic personal amount is
20,381 (up from 19,491) at the credit rate of 10.5%. The federal rates are the 2026 ones (14%,
20.5%, 26%, 29%, 33% from taxable income of 58,523, 117,045, 181,440 and 258,482), the federal basic
personal amount is 14,829 plus a supplement of 1,623 reduced from a net income of 181,440 over
77,042, the Canada employment amount is 1,501 or the salary if less, the EI premium is 1.63% to
68,900 and the CPP base contribution 4.95% of the salary less 3,500.

Every expected figure is derived by hand with plain decimal arithmetic from those datasets, never
read from the engine. Taxable income is the salary less the CPP enhanced contributions (1% of the
salary less 3,500 to 74,600, 4% of the salary from 74,600 to 85,000, each to the cent). The federal
tax after credits (T1 line 42900) is the bracket tax less 14% of the credits, summed and multiplied
once as the form does: the basic personal amount, the CPP base contribution, the EI premium and
the Canada employment amount (1,501 or the salary if less). The Saskatchewan tax after credits
(SK428 line 67; it equals line 82, the form's "Saskatchewan tax", because the lines between are
blank) is the bracket tax (rounded to the cent) less 10.5% of the credits: the Saskatchewan basic
personal amount of 20,381, the CPP base contribution and the EI premium only. The total payable is
their sum.

The cent rounding of each line, the half-up rounding of the average rate to 0.0001 and the zero-tax
gates are the project's choices: no form prints them.

Worked at 70,000 (taxable income 69,335.00):

- federal: 8,193.22 + 20.5% of (69,335.00 - 58,523) = 8,193.22 + 2,216.46 = 10,409.68; credits at
  14% of (16,452.00 + CPP 3,291.75 + EI 1,123.07 + Canada employment amount 1,501.00) = 3,131.49;
  tax 7,278.19.
- Saskatchewan: column 2, 5,725.86 + 12.5% of (69,335.00 - 54,532) = 5,725.86 + 1,850.375 =
  7,576.24 (line 8); credits at 10.5% of (20,381.00 + 3,291.75 + 1,123.07) = 2,603.56 (line 53);
  line 67 = 4,972.68.
- total payable 7,278.19 + 4,972.68 = 12,250.87; average 12,250.87 / 70,000 = 0.175012 -> 0.1750;
  marginal 20.5% + 12.5% = 33%.

The gates open at the zero-tax boundaries, found cent by cent from the same derivation (the part
is 0 one cent below and counts at the cent pinned):

- federal: T1 line 42900 is 0.00 at 19,200.17 and 0.01 at 19,200.18;
- Saskatchewan: SK428 line 67 is 0.00 at 21,827.31 (line 8 and line 53 are both 2,272.62) and
  0.01 at 21,827.32 (line 8 is 2,272.63), the salary at which Saskatchewan tax first exceeds zero.

The column boundaries: line 1 (taxable income) is exactly 54,532.00 at a salary of 55,047.47 and
exactly 155,805.00 at a salary of 156,932.00; a line 1 exactly at a column's upper bound is in the
lower column, so the next cent of salary reads the next column's rate.
"""

from __future__ import annotations

import re
from decimal import ROUND_HALF_UP, Decimal

import pytest

from tax_engine import build_tax_computation
from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.parameters.rounding import NO_ROUNDING
from tax_engine.domain.trace import SumLine
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.registrations import artifact_kinds
from tests.kinds import bundled_kinds, non_negative

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
    # 100 (taxable income 100.00): no tax at all, both gates closed, marginal 0%.
    ("100", "0.00", "0.00", "0", "0", "0", "0.00", "0"),
    # Federal boundary: closed at 19,200.17, open (14%) at 19,200.18; Saskatchewan closed.
    ("19200.17", "0.00", "0.00", "0", "0", "0", "0.00", "0"),
    ("19200.18", "0.01", "0.00", "0.14", "0", "0.14", "0.01", "0"),
    # 20,000 (taxable income 19,835.00): line 8 2,082.68 is under the credits of 2,259.99, so line
    # 67 is 0.00. 103.49 / 20,000 = 0.005175 -> 0.0052.
    ("20000", "103.49", "0.00", "0.14", "0", "0.14", "103.49", "0.0052"),
    # Saskatchewan boundary: closed at 21,827.31, open at 21,827.32 (14% + 10.5% = 24.5%).
    ("21827.31", "339.93", "0.00", "0.14", "0", "0.14", "339.93", "0.0156"),
    ("21827.32", "339.93", "0.01", "0.14", "0.105", "0.245", "339.94", "0.0156"),
    # 50,000 (taxable income 49,535.00, column 1): 14% + 10.5%. 6,719.05 / 50,000 = 0.134381.
    ("50000", "3985.13", "2733.92", "0.14", "0.105", "0.245", "6719.05", "0.1344"),
    # Column 1 / column 2 boundary: taxable income 54,532.00 is in column 1, 54,532.01 in column 2.
    ("55047.47", "4638.22", "3223.72", "0.14", "0.105", "0.245", "7861.94", "0.1428"),
    ("55047.48", "4638.22", "3223.72", "0.14", "0.125", "0.265", "7861.94", "0.1428"),
    # 70,000 (taxable income 69,335.00, column 2): 20.5% + 12.5%. 12,250.87 / 70,000 = 0.175012.
    ("70000", "7278.19", "4972.68", "0.205", "0.125", "0.33", "12250.87", "0.1750"),
    # 120,000 (taxable income 118,873.00, federal bracket 3, Saskatchewan column 2): 26% + 12.5%.
    ("120000", "17502.14", "11141.02", "0.26", "0.125", "0.385", "28643.16", "0.2387"),
    # Column 2 / column 3 boundary: taxable income 155,805.00 is in column 2, 155,805.01 in
    # column 3.
    ("156932", "27104.46", "15757.52", "0.26", "0.125", "0.385", "42861.98", "0.2731"),
    ("156932.01", "27104.46", "15757.52", "0.26", "0.145", "0.405", "42861.98", "0.2731"),
    # 200,000 (taxable income 198,873.00, column 3, federal 29%): 14.5% Saskatchewan.
    # 60,878.92 / 200,000 = 0.3043946 -> 0.3044.
    ("200000", "38876.54", "22002.38", "0.29", "0.145", "0.435", "60878.92", "0.3044"),
    # 300,000 (taxable income 298,873.00, federal 33%, federal supplement fully reduced):
    # 106,170.37 / 300,000 = 0.3539012 -> 0.3539.
    ("300000", "69667.99", "36502.38", "0.33", "0.145", "0.475", "106170.37", "0.3539"),
]
PART_FIGURES = [(s, f, k, m) for s, _, _, f, k, m, _, _ in FIGURES]
AVERAGE_FIGURES = [(s, t, a) for s, _, _, _, _, _, t, a in FIGURES]
TAX_FIGURES = [(s, f, k, t) for s, f, k, _, _, _, t, _ in FIGURES]


def _worksheets(salary: str, year: int = 2026) -> dict[str, tuple[Worksheet, ...]]:
    return build_tax_computation().compute(
        SASKATCHEWAN, year, Artifact(EMPLOYMENT_INCOME, D(salary))
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


def test_the_2026_average_at_70000_is_17_50_percent_and_the_marginal_33_percent() -> None:
    summary = _summary("70000")

    assert _value(summary, TOTAL_PAYABLE) == D("12250.87")
    assert _value(summary, AVERAGE) == D("0.1750")
    assert _value(summary, MARGINAL) == D("0.33")


def test_a_salary_of_100_reads_0_for_both_rates_and_both_parts() -> None:
    summary = _summary("100")

    assert _value(summary, MARGINAL) == D("0")
    assert _value(summary, AVERAGE) == D("0")
    assert _value(summary, FEDERAL) == D("0")
    assert _value(summary, SK_RATE) == D("0")
    assert _value(summary, RATE_GATE) == D("0")


def test_saskatchewan_tax_first_exceeds_zero_at_21827_32_and_the_gate_opens_there() -> None:
    closed = _summary("21827.31")
    opened = _summary("21827.32")

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
        ("55047.47", "54532.00", "0.105"),
        ("55047.48", "54532.01", "0.125"),
        ("70000", "69335.00", "0.125"),
        ("156932", "155805.00", "0.125"),
        ("156932.01", "155805.01", "0.145"),
        ("200000", "198873.00", "0.145"),
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
    # 0.14 + 0.105 = 0.245 and 0.26 + 0.125 = 0.385 keep their places: no cent rule is applied.
    value = _value(_summary("21827.32"), MARGINAL)

    assert value == D("0.245")
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
    [("20000", "0.00"), ("70000", "4972.68"), ("200000", "22002.38")],
)
def test_the_2026_saskatchewan_tax_anchors_do_not_move(salary: str, line_82: str) -> None:
    (sk428,) = _worksheets(salary)[SK428]

    assert _value(sk428, LINE_82) == D(line_82)


@pytest.mark.parametrize(
    ("salary", "line_82"),
    [("20000", "0.00"), ("70000", "5092.30"), ("200000", "22207.93")],
)
def test_the_2025_saskatchewan_tax_anchors_do_not_move(salary: str, line_82: str) -> None:
    (sk428,) = _worksheets(salary, 2025)[SK428]

    assert _value(sk428, LINE_82) == D(line_82)


@pytest.mark.parametrize(
    ("salary", "line_167"),
    [("20000", "-1474.91"), ("70000", "12677.94"), ("200000", "61675.67")],
)
def test_the_2025_line_167_anchors_do_not_move(salary: str, line_167: str) -> None:
    (summary,) = _worksheets(salary, 2025)[RETURN]

    assert _value(summary, "ca/refund_or_balance_owing") == D(line_167)


@pytest.mark.parametrize(
    ("year", "salary", "take_home"),
    [
        (2025, "70000", "53468.68"),
        (2025, "20000", "20165.16"),
        (2025, "275000", "167749.14"),
        (2026, "70000", "53786.25"),
        (2026, "20000", "20253.76"),
        (2026, "275000", "168519.20"),
    ],
)
def test_the_ontario_take_home_anchors_do_not_move(year: int, salary: str, take_home: str) -> None:
    # Take-home is the salary less CPP, EI and T1 line 167.
    kinds = bundled_kinds()
    ontario = build_tax_computation().compute(
        JurisdictionCode("CA-ON"), year, Artifact(EMPLOYMENT_INCOME, D(salary))
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

    assert D(salary) - cpp - ei - line_167 == D(take_home)
