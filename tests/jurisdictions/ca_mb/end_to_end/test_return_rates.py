"""The Manitoba return summary carries the average and the marginal income tax rate (2025), through
the registered engine (`build_tax_computation`, which lists Manitoba; salary the only input).

- The average rate is the take-home deductions (T1 line 43500, CPP and EI) over the salary,
  rounded once half-up to 0.0001 (`ca/take_home_average_rate`).
- The marginal rate (`ca-mb/marginal_tax_rate`) is the exact sum of three parts: the federal
  marginal rate (`ca-mb/marginal_federal_rate`, from the federal form
  `ca/take_home_marginal_rates`), the Manitoba marginal rate (`ca-mb/manitoba_marginal_rate`: the
  MB428 line 5 rate and the falls of the basic personal amount and of the family tax benefit,
  less the credit on the CPP base and EI, counted only where MB428 line 65 is above 0) and the
  contribution rate (CPP base, first and second additional, EI). `end_to_end/
  test_return_marginal_tax_rate_extra_run.py` checks it against a double run of the engine.

Form text (Form MB428, CRA 5007-c-25e.txt): "Line 5: Rate 10.8%", "Line 5: Rate 12.75%", "Line 5:
Rate 17.4%" (column 1 "Line 1 is $47,000 or less", column 2 "Line 1 is more than $47,000 but not
more than $100,000", column 3 "Line 1 is more than $100,000"); "Line 52: Manitoba non-refundable tax
credits rate 10.8%"; "Line 65: Line 60 minus line 64 (if negative, enter "0") = ^". Worksheet MB428
(CRA 5007-d-25e.txt), "Line 58040 - Basic personal amount": "Line 1: Base amount 15,780.00", "Line
3: Income threshold 200,000.00", "Line 4: Line 2 minus line 3 (if negative, enter "0") = ^", "Line
5: Income threshold 200,000.00", "Line 6: Line 4 divided by line 5 = ^", "Line 7: Base amount
15,780.00", "Line 8: Line 6 multiplied by line 7 = ^" and "Line 9: Line 1 minus line 8 (if negative,
enter "0")". T4127 (January 2025), Manitoba: "Where $200,000 < NI* < $400,000, BPAMB** = $15,969 -
(NI* - $200,000) × ($15,969 / $200,000)***". The basic personal amount falls as income rises, so
inside that range a further dollar of income is taxed at 15,780 / 200,000 x 10.8% = 0.0085212 more
(0.852 points): the Manitoba part is 17.4% + 0.85212 points = 18.25212% at a net income between
200,000 and 400,000 (while line 65 is above zero). The printed Worksheet MB428 figure of 15,780
decides, not the T4127 one.

The rates are pinned from the engine after the figures at 70,000 (2025: 19.57725% + 12.0879% +
5.95% = 37.61515%), 250,000, 300,000 and 500,000 were derived by hand from the printed rates, and
after the double run agreed at every salary of its sweep. The total payable and the average were
derived by hand from the printed form lines and the datasets (exact Decimal), and agree with the
existing pinned anchors
(MB428 line 33 of 20,149.23 and line 82 of 5,747.59 at 70,000, 26,863.55 at 200,000 and 35,980.46
at 250,000, and the federal tax of 7,585.64 at 70,000). The taxable income and the net income are
the salary less the CPP enhanced contribution (1% of the salary less 3,500, to the cent, and 4% of
the salary between 71,300 and 81,200, to the cent; 1,074.00 from a salary of 81,200 up). The total
payable is the federal tax after credits (T1 line 42900) plus the Manitoba tax (MB428 line 65, equal
to line 82 here): for example 7,585.64 + 5,747.59 = 13,333.23 at 70,000.

The gates open at the zero-tax boundaries, found cent by cent from the same derivation (the part is
0 one cent below and counts at the cent pinned):

- Manitoba: MB428 line 65 is 0.00 at 17,403.90 and 0.01 at 17,403.91 (a net income of 17,264.87;
  the family tax benefit is already in the credits there, which this return does not count);
- federal: T1 line 42900 is 0.00 at 18,820.26 and 0.01 at 18,820.27.

The phase-out's slope starts at a net income of 200,000.07 (salary 201,074.07) and ends at
399,999.93 (salary 401,073.93), not at the printed 200,000.00 and 400,000.00: Worksheet MB428 line 8
is a dollars-and-cents box (0.06 x 0.0789 rounds to 0.00, 0.07 x 0.0789 to 0.01), so it is 0.00
up to a net income of 200,000.06; and line 9 is 0.00 from a net income of 399,999.94 (line 8 is then
15,780.00), which is where the printed form already reads 0.
"""

from __future__ import annotations

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
MANITOBA = JurisdictionCode("CA-MB")
RETURN = "ca-mb/return"
FEDERAL = "ca-mb/marginal_federal_rate"
CONTRIBUTION = "ca-mb/marginal_contribution_rate"
MB_RATE = "ca-mb/manitoba_marginal_rate"
MARGINAL = "ca-mb/marginal_tax_rate"
AVERAGE = "ca-mb/average_tax_rate"
BRACKET = "ca-mb/manitoba_bracket_rate_return"
LINE_65_RETURN = "ca-mb/manitoba_tax_after_credits_return"
RATE_GATE = "ca-mb/manitoba_rate_gate"
LINE_8_RETURN = "ca-mb/manitoba_phase_out_amount_return"
LINE_9_RETURN = "ca-mb/manitoba_basic_personal_amount_return"
LINE_7_RETURN = "ca-mb/manitoba_base_amount_return"
LINE_5_RETURN = "ca-mb/manitoba_income_threshold_return"
BPA_GATE = "ca-mb/manitoba_basic_personal_amount_gate"
SLOPE = "ca-mb/manitoba_reduction_slope"
RATIO = "ca-mb/manitoba_phase_out_ratio"
CREDIT_RATE = "ca-mb/manitoba_phase_out_credit_rate"
PHASE_OUT = "ca-mb/manitoba_phase_out_rate"
WITH_PHASE_OUT = "ca-mb/manitoba_bracket_rate_with_phase_out"
WORKSHEET = "ca-mb/worksheet_mb428"
WORKSHEET_LINE_2 = "ca-mb/worksheet_mb428_line_2"
WORKSHEET_LINE_8 = "ca-mb/worksheet_mb428_line_8"
WORKSHEET_LINE_9 = "ca-mb/worksheet_mb428_basic_personal_amount_line_9"
LINE_82 = "ca-mb/mb428_manitoba_tax_line_82"
NEW_KINDS = [
    AVERAGE,
    MARGINAL,
    MB_RATE,
    BRACKET,
    LINE_65_RETURN,
    RATE_GATE,
    LINE_8_RETURN,
    LINE_9_RETURN,
    LINE_7_RETURN,
    LINE_5_RETURN,
    BPA_GATE,
    SLOPE,
    RATIO,
    CREDIT_RATE,
    PHASE_OUT,
    WITH_PHASE_OUT,
]

# Salary, federal part, Manitoba part, contribution rate, marginal rate, T1 line 43500 total
# payable, average. The marginal rate is the exact sum of the first three (checked in the test).
FIGURES = [
    ("0", "0", "0", "0", "0", "0.00", "0"),
    ("100", "0", "0", "0", "0", "0.00", "0.0000"),
    ("17403.90", "0", "0", "0.0759", "0.0759", "0.00", "0.0639"),
    ("17403.91", "0", "0.1094256", "0.0759", "0.1853256", "0.01", "0.0639"),
    ("18820.26", "0", "0.1094256", "0.0759", "0.1853256", "154.99", "0.0731"),
    ("18820.27", "0.1339945", "0.1094256", "0.0759", "0.3193201", "155.00", "0.0731"),
    ("20000", "0.1339945", "0.1094256", "0.0759", "0.3193201", "442.17", "0.0876"),
    ("50000", "0.1339945", "0.1191078", "0.0759", "0.3290023", "7535.75", "0.2225"),
    ("70000", "0.1957725", "0.120879", "0.0595", "0.3761515", "13333.23", "0.2624"),
    ("150000", "0.26", "0.174", "0", "0.434", "43935.69", "0.3296"),
    ("200000", "0.2930542655", "0.174", "0", "0.4670542655", "66331.29", "0.3592"),
    ("201074.06", "0.2930542655", "0.174", "0", "0.4670542655", "66832.93", "0.3598"),
    ("201074.07", "0.2930542655", "0.1825212", "0", "0.4755754655", "66832.93", "0.3598"),
    ("250000", "0.2930542655", "0.1825212", "0", "0.4755754655", "90100.91", "0.3824"),
    ("300000", "0.33", "0.1825212", "0", "0.5125212", "115561.16", "0.4036"),
    ("401073.93", "0.33", "0.1825212", "0", "0.5125212", "167363.70", "0.4310"),
    ("401073.94", "0.33", "0.174", "0", "0.504", "167363.70", "0.4310"),
    ("410000", "0.33", "0.174", "0", "0.504", "171862.43", "0.4326"),
]
PART_FIGURES = [(s, f, m, c, t) for s, f, m, c, t, _, _ in FIGURES]
# Salary, MB428 line 5 rate read: the rate is never blank. Taxable income 47,000.00 at 47,439.39 is
# up to 47,000 (column 1) and 47,000.01 at 47,439.40 is above it; 100,000.00 at 101,074.00 is up to
# 100,000 (column 2) and 100,000.01 at 101,074.01 is above it.
BRACKET_FIGURES = [
    ("0", "0.108"),
    ("20000", "0.108"),
    ("47439.39", "0.108"),
    ("47439.40", "0.1275"),
    ("70000", "0.1275"),
    ("101074.00", "0.1275"),
    ("101074.01", "0.174"),
    ("200000", "0.174"),
]
# Salary, net income, Worksheet MB428 line 8, line 9, basic personal amount gate, reduction slope,
# phase-out credit rate (0.0789 x slope), phase-out rate (gate x credit rate). The slope is 0.108
# where line 8 is above 0.00 and the gate is 1 where line 9 is above 0.00.
PHASE_OUT_FIGURES = [
    (
        "0",
        "0.00",
        "0.00",
        "15780.00",
        "1",
        "0",
        "0",
        "0",
    ),
    (
        "70000",
        "69335.00",
        "0.00",
        "15780.00",
        "1",
        "0",
        "0",
        "0",
    ),
    (
        "200000",
        "198926.00",
        "0.00",
        "15780.00",
        "1",
        "0",
        "0",
        "0",
    ),
    (
        "201074.06",
        "200000.06",
        "0.00",
        "15780.00",
        "1",
        "0",
        "0",
        "0",
    ),
    (
        "201074.07",
        "200000.07",
        "0.01",
        "15779.99",
        "1",
        "0.108",
        "0.0085212",
        "0.0085212",
    ),
    (
        "250000",
        "248926.00",
        "3860.26",
        "11919.74",
        "1",
        "0.108",
        "0.0085212",
        "0.0085212",
    ),
    (
        "300000",
        "298926.00",
        "7805.26",
        "7974.74",
        "1",
        "0.108",
        "0.0085212",
        "0.0085212",
    ),
    (
        "401073.93",
        "399999.93",
        "15779.99",
        "0.01",
        "1",
        "0.108",
        "0.0085212",
        "0.0085212",
    ),
    (
        "401073.94",
        "399999.94",
        "15780.00",
        "0.00",
        "0",
        "0.108",
        "0.0085212",
        "0",
    ),
    (
        "410000",
        "408926.00",
        "16484.26",
        "0.00",
        "0",
        "0.108",
        "0.0085212",
        "0",
    ),
]


def _worksheets(salary: str) -> dict[str, tuple[Worksheet, ...]]:
    return build_tax_computation().compute(
        TaxCalculationRequest(MANITOBA, 2025, (Artifact(EMPLOYMENT_INCOME, D(salary)),))
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
    "name",
    [
        MARGINAL,
        AVERAGE,
        MB_RATE,
        BRACKET,
        SLOPE,
        RATIO,
        CREDIT_RATE,
        PHASE_OUT,
        WITH_PHASE_OUT,
        BPA_GATE,
        RATE_GATE,
    ],
)
def test_the_rate_kinds_are_non_negative(name: str) -> None:
    assert non_negative(artifact_kinds().kind(name))


@pytest.mark.parametrize(
    ("salary", "federal", "manitoba", "contribution", "marginal"), PART_FIGURES
)
def test_the_marginal_rate_is_the_exact_sum_of_the_federal_manitoba_and_contribution_part(
    salary: str, federal: str, manitoba: str, contribution: str, marginal: str
) -> None:
    summary = _summary(salary)

    assert _value(summary, FEDERAL) == D(federal)
    assert _value(summary, MB_RATE) == D(manitoba)
    assert _value(summary, CONTRIBUTION) == D(contribution)
    assert _value(summary, MARGINAL) == D(marginal)
    assert D(federal) + D(manitoba) + D(contribution) == D(marginal)


@pytest.mark.parametrize("salary", ["0", "100"])
def test_a_salary_of_0_or_100_reads_0_for_both_rates(salary: str) -> None:
    summary = _summary(salary)

    assert _value(summary, MARGINAL) == D("0")
    assert _value(summary, AVERAGE) == D("0")
    assert _value(summary, FEDERAL) == D("0")
    assert _value(summary, MB_RATE) == D("0")
    assert _value(summary, CONTRIBUTION) == D("0")


@pytest.mark.parametrize(("salary", "line_5"), BRACKET_FIGURES)
def test_the_bracket_rate_is_the_line_5_rate_of_the_column_the_taxable_income_is_in(
    salary: str, line_5: str
) -> None:
    summary = _summary(salary)

    assert _value(summary, BRACKET) == D(line_5)


@pytest.mark.parametrize(
    (
        "salary",
        "net_income",
        "line_8",
        "line_9",
        "gate",
        "slope",
        "credit_rate",
        "phase_out",
    ),
    PHASE_OUT_FIGURES,
)
def test_the_phase_out_slope_runs_from_a_net_income_over_200000_to_just_under_400000(
    salary: str,
    net_income: str,
    line_8: str,
    line_9: str,
    gate: str,
    slope: str,
    credit_rate: str,
    phase_out: str,
) -> None:
    (sheet,) = _worksheets(salary)[WORKSHEET]
    summary = _summary(salary)

    assert _value(sheet, WORKSHEET_LINE_2) == D(net_income)
    assert _value(sheet, WORKSHEET_LINE_8) == D(line_8)
    assert _value(sheet, WORKSHEET_LINE_9) == D(line_9)
    assert _value(summary, LINE_8_RETURN) == D(line_8)
    assert _value(summary, LINE_9_RETURN) == D(line_9)
    assert _value(summary, LINE_7_RETURN) == D("15780.00")
    assert _value(summary, LINE_5_RETURN) == D("200000.00")
    assert _value(summary, BPA_GATE) == D(gate)
    assert _value(summary, SLOPE) == D(slope)
    assert _value(summary, RATIO) == D("0.0789")
    assert _value(summary, CREDIT_RATE) == D(credit_rate)
    assert _value(summary, PHASE_OUT) == D(phase_out)


@pytest.mark.parametrize("salary", ["70000", "250000"])
def test_the_manitoba_tax_after_credits_return_is_line_65_and_line_82_here(salary: str) -> None:
    worksheets = _worksheets(salary)
    (mb428,) = worksheets["ca-mb/mb428"]
    (summary,) = worksheets[RETURN]
    line_65 = {"70000": "5747.59", "250000": "35980.46"}[salary]

    assert _value(summary, LINE_65_RETURN) == D(line_65)
    assert _value(mb428, LINE_82) == D(line_65)


def test_inside_the_phase_out_the_provincial_part_is_the_bracket_rate_plus_0_85212_points() -> None:
    # Net income is over 200,000 and over the CPP maximum, so a further dollar is all net income:
    # 17.4% + 0.85212 points, with no contribution credit and no contribution rate left.
    summary = _summary("250000")

    assert _value(summary, BRACKET) == D("0.174")
    assert _value(summary, PHASE_OUT) == D("0.0085212")
    assert _value(summary, MB_RATE) == D("0.1825212")
    assert _value(summary, MARGINAL) == D("0.2930542655") + D("0.1825212")
    assert D("15780") / D("200000") * D("0.108") == D("0.0085212")


def test_the_manitoba_gate_closes_the_part_while_the_rate_before_the_gate_is_still_above_zero() -> (
    None
):
    # Net income 99% of a further dollar: 10.8% x 0.99 less the credit on the contributions.
    summary = _summary("17403.90")

    assert _value(summary, WITH_PHASE_OUT) == D("0.1165428")
    assert _value(summary, LINE_65_RETURN) == D("0.00")
    assert _value(summary, RATE_GATE) == D("0")
    assert _value(summary, MB_RATE) == D("0")
    assert _value(summary, MARGINAL) == D("0.0759")
    assert _value(summary, MARGINAL) == _value(summary, CONTRIBUTION)


def test_the_marginal_rate_is_not_rounded_to_the_cent_or_to_ten_thousandths() -> None:
    # 0.2930542655 + 0.1825212 = 0.4755754655 keeps its places: no rule is applied to a rate.
    value = _value(_summary("250000"), MARGINAL)

    assert value == D("0.4755754655")
    assert value != value.quantize(D("0.0001"))


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


def test_the_marginal_rate_is_traced_as_one_exact_sum_of_its_three_parts() -> None:
    sheet = _summary("250000")
    kinds = artifact_kinds()

    line = _sum_line(sheet)

    assert [(kind.label, value) for kind, value in line.parts] == [
        (kinds.kind(FEDERAL).label, D("0.2930542655")),
        (kinds.kind(MB_RATE).label, D("0.1825212")),
        (kinds.kind(CONTRIBUTION).label, D("0")),
    ]
    assert line.rounding == NO_ROUNDING
    assert line.total == D("0.4755754655")
    assert line.amount == sheet.get(kinds.kind(MARGINAL)).value


def test_the_marginal_rate_is_explained_in_english_as_percentages() -> None:
    sheet = _summary("70000")

    text = EnglishTraceRenderer().render(_sum_line(sheet), sheet)

    assert (
        text
        == "Marginal federal rate (19.57725%) plus manitoba marginal rate (12.0879%) plus marginal "
        "contribution rate (5.95%) gives 37.61515% (not rounded)."
    )


def test_the_marginal_rate_comes_last_of_the_marginal_steps_in_the_trace() -> None:
    sheet = _summary("100000")
    kinds = artifact_kinds()
    labels = [line.label for line in sheet.trace]

    marginal = labels.index(kinds.kind(MARGINAL).label)

    assert marginal == len(labels) - 1
    assert labels.count(kinds.kind(MARGINAL).label) == 1
    for part in (FEDERAL, MB_RATE, WITH_PHASE_OUT, PHASE_OUT, CREDIT_RATE, RATIO, SLOPE):
        assert labels.index(kinds.kind(part).label) < marginal


@pytest.mark.parametrize(
    ("salary", "line_33", "line_82"),
    [("70000", "20149.23", "5747.59"), ("200000", "20213.58", "26863.55")],
)
def test_the_manitoba_tax_anchors_do_not_move(salary: str, line_33: str, line_82: str) -> None:
    worksheets = _worksheets(salary)
    (credits_sheet,) = worksheets["ca-mb/mb428_credits"]
    (mb428,) = worksheets["ca-mb/mb428"]

    assert _value(credits_sheet, "ca-mb/mb428_credits_subtotal_line_33") == D(line_33)
    assert _value(mb428, LINE_82) == D(line_82)


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
