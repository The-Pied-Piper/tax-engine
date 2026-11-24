"""The Manitoba return summary carries the average and the marginal income tax rate (2026), through
the registered engine (`build_tax_computation`, which lists Manitoba; salary the only input).

The Manitoba 2026 datasets are PROVISIONAL: the 2026 Form MB428 and Worksheet MB428 are not yet
published, and the figures follow the provisional 2026 datasets, which are carried forward from the
2025 forms (Form MB428, Worksheet MB428) or taken from T4127. Every figure pinned here follows those
provisional datasets and was derived by hand; every Manitoba and federal 2026 figure below is
provisional and must be re-checked when CRA publishes the 2026 forms.

The rates are calculated the same way as for 2025 (see `test_return_rates.py`):

- The average rate is the take-home deductions (T1 line 43500, CPP and EI) over the salary,
  rounded once half-up to 0.0001 (`ca/take_home_average_rate`).
- The marginal rate (`ca-mb/marginal_tax_rate`) is the exact sum of the federal marginal rate, the
  Manitoba marginal rate and the contribution rate, as in `test_return_rates.py`; the double run
  of `test_return_marginal_tax_rate_extra_run.py` checks it for 2026 too.

The provisional 2026 figures: the Manitoba rates (10.8%, 12.75%, 17.4%) and bounds (47,000 and
100,000) are carried forward unchanged from the 2025 Form MB428, and so are the basic personal
amount of 15,780 and its income threshold of 200,000 (Worksheet MB428 lines 1, 3, 5 and 7, the
printed figures, which decide here rather than the 15,969 of the T4127 formula); the provisional
federal figures are the 2026 dataset ones (14%, 20.5%, 26%, 29%, 33% from taxable income of
58,523, 117,045, 181,440 and 258,482) with a credit rate of 14%, a basic personal amount of 16,452
(14,829 from a net income of 258,482, reduced over 77,042 from 181,440) and a Canada employment
amount of 1,501. Inside the
phase-out range a further dollar of income is taxed at 15,780 / 200,000 x 10.8% = 0.0085212 more
(0.852 points), so the Manitoba part is 17.4% + 0.85212 points = 18.25212% at a net income between
200,000 and 400,000 (while line 65 is above zero).

Every expected figure is derived by hand from the form lines and the datasets (exact Decimal),
never read from the engine. The taxable income and the net income are the salary less the CPP
enhanced contribution (1% of the salary less 3,500, to the cent, up to 74,600, and 4% of the salary
between 74,600 and 85,000, to the cent; 1,127.00 from a salary of 85,000 up). The federal tax after
credits (T1 line 42900) is the bracket tax less 14% of the basic personal amount, the CPP base
contribution (4.95% of the salary less 3,500, to the cent), the EI premium (1.63% to 68,900) and
the Canada employment amount (1,501 or the salary if less), summed and multiplied once. The
Manitoba tax (MB428 line 65, equal to line 82 here) is the bracket tax less 10.8% (line 52) of the
credits (line 51; Worksheet MB428 line 9 basic personal amount, the CPP base contribution, the EI
premium and, at a low income, the family tax benefit basic amount of 2,065 less 9% of the net
income), summed and multiplied once. The total payable is their sum.

At 70,000 (taxable income and net income 69,335.00; CPP base 3,291.75 and EI 1,123.07):

- federal: 8,193.22 + 20.5% of (69,335.00 - 58,523) = 10,409.68 bracket tax, less 14% of (16,452.00
  + 3,291.75 + 1,123.07 + 1,501.00 = 22,367.82) = 3,131.49, so T1 line 42900 is 7,278.19, with the
  20.5% bracket rate as the federal part;
- Manitoba: 5,076.00 + 12.75% of (69,335.00 - 47,000) = 7,923.71 bracket tax, less 10.8% of the
  credits subtotal (line 33; line 41, the family tax benefit, is 0 here) (15,780.00 + 3,291.75 +
  1,123.07 = 20,194.82) = 2,181.04, so MB428 line 65 is 5,742.67, with the 12.75%
  bracket rate as the Manitoba part (no phase-out term);
- the marginal rate is 37.6399% (see the figures below); the total payable is 7,278.19 + 5,742.67 =
  13,020.86 and the average rate 13,020.86 / 70,000 = 0.186012, rounded to 0.1860.

The gates open at the zero-tax boundaries, found cent by cent from the same derivation (the part is
0 one cent below and counts at the cent pinned):

- Manitoba: MB428 line 65 is 0.00 at 17,402.21 and 0.01 at 17,402.22 (a net income of 17,263.20;
  the family tax benefit is already in the credits there, which this return does not count);
- federal: T1 line 42900 is 0.00 at 19,200.17 and 0.01 at 19,200.18.

The bracket columns change at a taxable income of 47,000.00 (salary 47,439.39) and 47,000.01
(47,439.40), and at 100,000.00 (salary 101,127.00) and 100,000.01 (101,127.01).

The phase-out's slope starts at a net income of 200,000.07 (salary 201,127.07) and ends at
399,999.94 (salary 401,126.94), not at the printed 200,000.00 and 400,000.00. The worksheet prints
no rounding rule for line 8 ("Line 6 multiplied by line 7"), so this follows the project's reading,
the same as for 2025 and set by the datasets' cent rounding: line 8 is a dollars-and-cents amount
(0.06 x 0.0789 rounds to 0.00, 0.07 x 0.0789 to 0.01), so it is 0.00
up to a net income of 200,000.06; and line 9 is 0.00 from a net income of 399,999.94 (line 8 is
then 15,780.00), which is where the printed form already reads 0.
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
    ("17402.21", "0", "0", "0.0758", "0.0758", "0.00", "0.0638"),
    ("17402.22", "0", "0.1094364", "0.0758", "0.1852364", "0.01", "0.0638"),
    ("19200.17", "0", "0.1094364", "0.0758", "0.1852364", "196.77", "0.0752"),
    ("19200.18", "0.129388", "0.1094364", "0.0758", "0.3146244", "196.78", "0.0752"),
    ("20000", "0.129388", "0.1094364", "0.0758", "0.3146244", "387.79", "0.0848"),
    ("70000", "0.19602", "0.120879", "0.0595", "0.376399", "13020.86", "0.2586"),
    ("150000", "0.26", "0.174", "0", "0.434", "43433.91", "0.3280"),
    ("200000", "0.292949296", "0.174", "0", "0.466949296", "65708.31", "0.3574"),
    ("201127.06", "0.292949296", "0.174", "0", "0.466949296", "66234.60", "0.3580"),
    ("201127.07", "0.292949296", "0.1825212", "0", "0.475470496", "66234.60", "0.3580"),
    ("250000", "0.292949296", "0.1825212", "0", "0.475470496", "89472.23", "0.3810"),
    ("300000", "0.33", "0.1825212", "0", "0.5125212", "114742.27", "0.4017"),
    ("401126.93", "0.33", "0.1825212", "0", "0.5125212", "166571.98", "0.4296"),
    ("401126.94", "0.33", "0.174", "0", "0.504", "166571.98", "0.4296"),
    ("410000", "0.33", "0.174", "0", "0.504", "171044.00", "0.4313"),
]
# Salary, MB428 line 5 rate read: the rate is never blank. Taxable income 47,000.00 at 47,439.39 is
# up to 47,000 (column 1) and 47,000.01 at 47,439.40 is above it; 100,000.00 at 101,127.00 is up to
# 100,000 (column 2) and 100,000.01 at 101,127.01 is above it.
BRACKET_FIGURES = [
    ("0", "0.108"),
    ("20000", "0.108"),
    ("47439.39", "0.108"),
    ("47439.40", "0.1275"),
    ("70000", "0.1275"),
    ("101127.00", "0.1275"),
    ("101127.01", "0.174"),
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
        "198873.00",
        "0.00",
        "15780.00",
        "1",
        "0",
        "0",
        "0",
    ),
    (
        "201127.06",
        "200000.06",
        "0.00",
        "15780.00",
        "1",
        "0",
        "0",
        "0",
    ),
    (
        "201127.07",
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
        "248873.00",
        "3856.08",
        "11923.92",
        "1",
        "0.108",
        "0.0085212",
        "0.0085212",
    ),
    (
        "300000",
        "298873.00",
        "7801.08",
        "7978.92",
        "1",
        "0.108",
        "0.0085212",
        "0.0085212",
    ),
    (
        "401126.93",
        "399999.93",
        "15779.99",
        "0.01",
        "1",
        "0.108",
        "0.0085212",
        "0.0085212",
    ),
    (
        "401126.94",
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
        "408873.00",
        "16480.08",
        "0.00",
        "0",
        "0.108",
        "0.0085212",
        "0",
    ),
]


def _worksheets(salary: str, year: int = 2026) -> dict[str, tuple[Worksheet, ...]]:
    return build_tax_computation().compute(
        TaxCalculationRequest(MANITOBA, year, (Artifact(EMPLOYMENT_INCOME, D(salary)),))
    )


def _summary(salary: str, year: int = 2026) -> Worksheet:
    (summary,) = _worksheets(salary, year)[RETURN]
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
    line_65 = {"70000": "5742.67", "250000": "35948.22"}[salary]

    assert _value(summary, LINE_65_RETURN) == D(line_65)
    assert _value(mb428, LINE_82) == D(line_65)


def test_inside_the_phase_out_the_provincial_part_is_the_bracket_rate_plus_0_85212_points() -> None:
    # Net income is over 200,000 and over the CPP maximum, so a further dollar is all net income:
    # 17.4% + 0.85212 points, with no contribution credit and no contribution rate left.
    summary = _summary("250000")

    assert _value(summary, BRACKET) == D("0.174")
    assert _value(summary, PHASE_OUT) == D("0.0085212")
    assert _value(summary, MB_RATE) == D("0.1825212")
    assert _value(summary, MARGINAL) == D("0.292949296") + D("0.1825212")
    assert D("15780") / D("200000") * D("0.108") == D("0.0085212")


def test_the_manitoba_gate_closes_the_part_while_the_rate_before_the_gate_is_still_above_zero() -> (
    None
):
    # Net income 99% of a further dollar: 10.8% x 0.99 less the credit on the contributions.
    summary = _summary("17402.21")

    assert _value(summary, WITH_PHASE_OUT) == D("0.1165428")
    assert _value(summary, LINE_65_RETURN) == D("0.00")
    assert _value(summary, RATE_GATE) == D("0")
    assert _value(summary, MB_RATE) == D("0")
    assert _value(summary, MARGINAL) == D("0.0758")
    assert _value(summary, MARGINAL) == _value(summary, CONTRIBUTION)


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
        (kinds.kind(FEDERAL).label, D("0.292949296")),
        (kinds.kind(MB_RATE).label, D("0.1825212")),
        (kinds.kind(CONTRIBUTION).label, D("0")),
    ]
    assert line.rounding == NO_ROUNDING
    assert line.total == D("0.475470496")
    assert line.amount == sheet.get(kinds.kind(MARGINAL)).value


def test_the_marginal_rate_is_explained_in_english_as_percentages() -> None:
    sheet = _summary("70000")

    text = EnglishTraceRenderer().render(_sum_line(sheet), sheet)

    assert (
        text
        == "Marginal federal rate (19.602%) plus manitoba marginal rate (12.0879%) plus marginal "
        "contribution rate (5.95%) gives 37.6399% (not rounded)."
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
    [("70000", "20194.82", "5742.67"), ("200000", "20422.52", "26831.77")],
)
def test_the_2026_manitoba_tax_figures_are_pinned(salary: str, line_33: str, line_82: str) -> None:
    worksheets = _worksheets(salary)
    (credits_sheet,) = worksheets["ca-mb/mb428_credits"]
    (mb428,) = worksheets["ca-mb/mb428"]

    assert _value(credits_sheet, "ca-mb/mb428_credits_subtotal_line_33") == D(line_33)
    assert _value(mb428, LINE_82) == D(line_82)


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
        TaxCalculationRequest(
            JurisdictionCode("CA-ON"), year, (Artifact(EMPLOYMENT_INCOME, D(salary)),)
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

    assert D(salary) - cpp - ei - line_167 == D(take_home)
