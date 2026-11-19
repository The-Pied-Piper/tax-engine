"""The Newfoundland and Labrador return summary carries the marginal income tax rate (2025), over
the real parts of the Newfoundland and Labrador manifest (salary the only input).

Newfoundland and Labrador is not yet listed in the registered engine, so the engine is built over
a temporary copy of the manifest folder (`tests/jurisdictions/ca_nl/support.py` lists the
packages). The manifest also declares the average rate as an output; while that rate has no step
in `return.yaml` the copy leaves its declaration out, so the engine can load.

Calculated the same way as British Columbia's, with the low-income tax reduction as British
Columbia's tax reduction:

- The marginal rate (`ca-nl/marginal_tax_rate`) is the exact sum of two gated parts: the federal
  marginal rate (`ca/federal_marginal_rate`, the T1 line 73 bracket rate, counted only where T1
  line 42900 "Basic federal tax" is above 0) and the Newfoundland and Labrador marginal rate
  (`ca-nl/newfoundland_and_labrador_marginal_rate`): the NL428 line 5 rate, or the line 12 rate
  when line 5 is blank, plus the slope of the low-income tax reduction, counted only where NL428
  line 105 is above 0. CPP and EI are not counted.

Form text (Form NL428, CRA 5001-c-25e.txt): "Line 5: Rate 8.7%", "Rate 14.5%", "Rate 15.8%", "Rate
17.8%" (table 1, lines 2 to 8, up to $220,910); "Line 12: Rate 19.8%", "Rate 20.8%", "Rate 21.3%",
"Rate 21.8%" (table 2, above $220,910); "Line 95 and line 61870: Basic reduction Claim $997",
"Line 100: If you claimed an amount on line 96 or line 97, enter $40,460; if not, enter $23,928",
"Line 101: Line 99 minus line 100 (if negative, enter "0")", "Line 102: Applicable rate 16%",
"Line 103: Line 101 multiplied by the percentage from line 102", "Line 104: Line 98 minus line 103
(if negative, enter "0")" and "Line 105: Line 94 minus line 104 (if negative, enter "0")".

The low-income tax reduction falls by 16% of each dollar of adjusted family income above 23,928,
so inside that range a further dollar of income is taxed at 16 points more: the Newfoundland and
Labrador part is 8.7% + 16% = 24.7% at a net income between 23,928 and where the reduction ends,
while line 105 is above zero.

Every expected figure is derived by hand from the printed form lines and the federal and
Newfoundland and Labrador datasets (exact Decimal), never read from the engine, and agrees with
the anchors of the line tests (NL428 line 105 of 0.00, 921.72, 6,147.49 and 27,192.33 at 20,000,
28,000, 70,000 and 200,000). The net income is the salary less the CPP enhanced contribution (1%
of the salary less 3,500, to the cent; there is no second additional contribution below 71,300).
Line 105 is the tax on the net income (8.7% to the cent) less the credits (8.7% of 11,067 plus the
CPP base contribution, 4.95% of the salary less 3,500, plus the EI premium, 1.64% of the salary,
each to the cent), not below 0, less line 104.

The gates open at the zero-tax boundaries, found cent by cent from the same derivation (the part is
0 one cent below and counts at the cent pinned):

- federal: T1 line 42900 is 0.00 at 18,820.26 and 0.01 at 18,820.27;
- Newfoundland and Labrador: NL428 line 105 is 0.00 at 24,140.18 and 0.01 at 24,140.19, which is
  inside the reduction's range (the net income is 23,933.79 and line 103 is 0.93), so the part is
  8.7% + 16% = 24.7% where it opens.

The reduction's slope starts at a net income of 23,928.04, not at the printed 23,928.00: line 103
is a dollars-and-cents box (0.03 x 16% rounds to 0.00, 0.04 x 16% to 0.01), so line 103 is 0.00 up
to a net income of 23,928.03; and line 104 is 0.00 from a net income of 30,159.22 (line 103 is then
997.00), which is where the printed form already reads 0.
"""

from __future__ import annotations

import re
import shutil
from collections.abc import Iterator
from decimal import Decimal
from pathlib import Path

import pytest

import tax_engine.jurisdictions.ca_nl
from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.parameters.rounding import NO_ROUNDING
from tax_engine.domain.registry import Namespace
from tax_engine.domain.trace import SumLine
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tests.jurisdictions.ca_nl.support import (
    newfoundland_capabilities,
    newfoundland_kinds,
    newfoundland_packages,
    newfoundland_parameter_parsers,
    newfoundland_units,
)
from tests.kinds import non_negative

D = Decimal
NL_PARTS = Path(tax_engine.jurisdictions.ca_nl.__file__).parent / "manifests" / "2025"
NEWFOUNDLAND = JurisdictionCode("CA-NL")
RETURN = "ca-nl/return"
FEDERAL = "ca/federal_marginal_rate"
NL_RATE = "ca-nl/newfoundland_and_labrador_marginal_rate"
MARGINAL = "ca-nl/marginal_tax_rate"
AVERAGE_OUTPUT = "  - ca-nl/average_income_tax_rate\n"
LINE_5_RETURN = "ca-nl/newfoundland_and_labrador_bracket_rate_line_5_return"
LINE_12_RETURN = "ca-nl/newfoundland_and_labrador_bracket_rate_line_12_return"
BRACKET = "ca-nl/newfoundland_and_labrador_bracket_rate_return"
RATE_GATE = "ca-nl/newfoundland_and_labrador_rate_gate"
REDUCTION_GATE = "ca-nl/newfoundland_and_labrador_reduction_gate"
SLOPE = "ca-nl/newfoundland_and_labrador_reduction_slope"
PHASE_OUT = "ca-nl/newfoundland_and_labrador_reduction_phase_out_rate"
WITH_REDUCTION = "ca-nl/newfoundland_and_labrador_bracket_rate_with_reduction"
LINE_103 = "ca-nl/nl428_line_103"
LINE_104 = "ca-nl/nl428_line_104"
LINE_105 = "ca-nl/nl428_newfoundland_and_labrador_tax_line_105"
NEW_KINDS = [
    MARGINAL,
    NL_RATE,
    LINE_5_RETURN,
    LINE_12_RETURN,
    BRACKET,
    "ca-nl/newfoundland_and_labrador_tax_after_reduction_return",
    RATE_GATE,
    "ca-nl/newfoundland_and_labrador_low_income_reduction_return",
    REDUCTION_GATE,
    "ca-nl/newfoundland_and_labrador_reduction_clawback_return",
    SLOPE,
    PHASE_OUT,
    WITH_REDUCTION,
]

# Salary, federal part, Newfoundland and Labrador part, marginal rate.
FIGURES = [
    # Salaries of 0 and 100: no tax at all, both gates closed.
    ("0", "0", "0", "0"),
    ("100", "0", "0", "0"),
    # Federal boundary: closed at 18,820.26, open (14.5%) at 18,820.27; Newfoundland and Labrador
    # closed (line 105 is 0.00, the reduction of 997.00 takes all of the tax).
    ("18820.26", "0", "0", "0"),
    ("18820.27", "0.145", "0", "0.145"),
    # 20,000 (net income 19,835.00): line 105 is 0.00, so the Newfoundland and Labrador part is 0.
    ("20000", "0.145", "0", "0.145"),
    # Newfoundland and Labrador boundary: closed at 24,140.18, open at 24,140.19 (8.7% + 16%).
    ("24140.18", "0.145", "0", "0.145"),
    ("24140.19", "0.145", "0.247", "0.392"),
    # 28,000 (net income 27,755.00): inside the reduction range, 14.5% + 24.7% = 39.2%.
    ("28000", "0.145", "0.247", "0.392"),
    # Past the end of the reduction (net income 30,159.22), 8.7% only: 14.5% + 8.7% = 23.2%.
    ("30428.50", "0.145", "0.247", "0.392"),
    ("30428.51", "0.145", "0.087", "0.232"),
    ("40000", "0.145", "0.087", "0.232"),
    # 70,000 (net income 69,335.00): 20.5% federal, 14.5% (44,192 to 88,382); 20.5% + 14.5%.
    ("70000", "0.205", "0.145", "0.35"),
    # 200,000: 29% federal, 17.8% (157,792 to 220,910).
    ("200000", "0.29", "0.178", "0.468"),
    # 250,000 (above the table 1 limit of 220,910): the line 12 rate of 19.8% is read.
    ("250000", "0.29", "0.198", "0.488"),
]
PART_FIGURES = FIGURES
# Salary, NL428 line 5 and line 12 rates read (a blank is 0).
BRACKET_FIGURES = [
    ("40000", "0.087", "0"),
    ("70000", "0.145", "0"),
    ("200000", "0.178", "0"),
    ("250000", "0", "0.198"),
]
# Salary, net income, line 103, line 104, slope, reduction gate, phase-out rate, bracket rate with
# the reduction, Newfoundland and Labrador marginal rate. The slope is 16% where line 103 is above
# 0.00, the gate is 1 where line 104 is above 0.00, and the part is 0 below the line 105 boundary
# of 24,140.19 although the reduction is already in the bracket rate.
REDUCTION_FIGURES = [
    ("20000", "19835.00", "0.00", "997.00", "0", "1", "0", "0.087", "0"),
    ("24134.37", "23928.03", "0.00", "997.00", "0", "1", "0", "0.087", "0"),
    ("24134.38", "23928.04", "0.01", "996.99", "0.16", "1", "0.16", "0.247", "0"),
    ("24140.18", "23933.78", "0.92", "996.08", "0.16", "1", "0.16", "0.247", "0"),
    ("24140.19", "23933.79", "0.93", "996.07", "0.16", "1", "0.16", "0.247", "0.247"),
    ("28000", "27755.00", "612.32", "384.68", "0.16", "1", "0.16", "0.247", "0.247"),
    ("30428.50", "30159.21", "996.99", "0.01", "0.16", "1", "0.16", "0.247", "0.247"),
    ("30428.51", "30159.22", "997.00", "0.00", "0.16", "0", "0", "0.087", "0.087"),
    ("40000", "39635.00", "2513.12", "0.00", "0.16", "0", "0", "0.087", "0.087"),
]


@pytest.fixture(scope="module")
def service(tmp_path_factory: pytest.TempPathFactory) -> Iterator[TaxComputationService]:
    """The engine over a temporary copy of the real Newfoundland and Labrador manifest folder."""
    root = tmp_path_factory.mktemp("newfoundland")
    folder = root / "manifests" / "2025"
    shutil.copytree(NL_PARTS, folder)
    manifest = folder / "manifest.yaml"
    if f"output: {AVERAGE_OUTPUT.strip()[2:]}" not in (folder / "return.yaml").read_text(
        encoding="utf-8"
    ):
        manifest.write_text(
            manifest.read_text(encoding="utf-8").replace(AVERAGE_OUTPUT, ""), encoding="utf-8"
        )
    roots = {**newfoundland_packages().roots(), Namespace("ca-nl"): root}
    yield TaxComputationService(
        YamlJurisdictionSource(roots, newfoundland_kinds(), newfoundland_units()),
        YamlParameterSource(
            newfoundland_packages().roots(), newfoundland_parameter_parsers(), newfoundland_units()
        ),
        newfoundland_capabilities(),
    )


def _worksheets(service: TaxComputationService, salary: str) -> dict[str, tuple[Worksheet, ...]]:
    return service.compute(NEWFOUNDLAND, 2025, Artifact(EMPLOYMENT_INCOME, D(salary)))


def _summary(service: TaxComputationService, salary: str) -> Worksheet:
    (summary,) = _worksheets(service, salary)[RETURN]
    return summary


def _value(summary: Worksheet, name: str) -> Decimal:
    value = summary.get(newfoundland_kinds().kind(name)).value
    assert isinstance(value, Decimal)
    return value


def _sum_line(sheet: Worksheet) -> SumLine:
    """The one trace line of the marginal tax rate step, found by its output kind."""
    label = newfoundland_kinds().kind(MARGINAL).label
    (line,) = [
        line for line in sheet.trace if isinstance(line, SumLine) and line.output.label == label
    ]
    return line


@pytest.mark.parametrize("name", NEW_KINDS)
def test_the_new_kinds_are_registered_decimal_amounts(name: str) -> None:
    kind = newfoundland_kinds().kind(name)

    assert kind.identifier == name
    assert kind.value_type is Decimal


@pytest.mark.parametrize("name", [MARGINAL, NL_RATE, BRACKET, SLOPE, PHASE_OUT, WITH_REDUCTION])
def test_the_rate_kinds_are_non_negative(name: str) -> None:
    assert non_negative(newfoundland_kinds().kind(name))


@pytest.mark.parametrize(("salary", "federal", "newfoundland", "marginal"), PART_FIGURES)
def test_the_marginal_rate_is_the_exact_sum_of_the_federal_and_the_newfoundland_part(
    service: TaxComputationService, salary: str, federal: str, newfoundland: str, marginal: str
) -> None:
    summary = _summary(service, salary)

    assert _value(summary, FEDERAL) == D(federal)
    assert _value(summary, NL_RATE) == D(newfoundland)
    assert _value(summary, MARGINAL) == D(marginal)
    assert D(federal) + D(newfoundland) == D(marginal)


@pytest.mark.parametrize("salary", ["0", "100"])
def test_a_salary_of_0_or_100_reads_0_for_the_rate(
    service: TaxComputationService, salary: str
) -> None:
    summary = _summary(service, salary)

    assert _value(summary, MARGINAL) == D("0")
    assert _value(summary, FEDERAL) == D("0")
    assert _value(summary, NL_RATE) == D("0")


@pytest.mark.parametrize(("salary", "line_5", "line_12"), BRACKET_FIGURES)
def test_line_12_supplies_the_rate_above_the_table_1_limit_and_line_5_below_it(
    service: TaxComputationService, salary: str, line_5: str, line_12: str
) -> None:
    summary = _summary(service, salary)

    assert _value(summary, LINE_5_RETURN) == D(line_5)
    assert _value(summary, LINE_12_RETURN) == D(line_12)
    assert _value(summary, BRACKET) == D(line_5) + D(line_12)


@pytest.mark.parametrize(
    (
        "salary",
        "net_income",
        "line_103",
        "line_104",
        "slope",
        "gate",
        "phase_out",
        "with_reduction",
        "newfoundland",
    ),
    REDUCTION_FIGURES,
)
def test_the_reduction_slope_runs_from_a_net_income_over_23928_to_the_end_of_the_reduction(
    service: TaxComputationService,
    salary: str,
    net_income: str,
    line_103: str,
    line_104: str,
    slope: str,
    gate: str,
    phase_out: str,
    with_reduction: str,
    newfoundland: str,
) -> None:
    worksheets = _worksheets(service, salary)
    (nl428,) = worksheets["ca-nl/nl428"]
    (summary,) = worksheets[RETURN]

    assert _value(nl428, "ca-nl/nl428_adjusted_family_income_line_93") == D(net_income)
    assert _value(nl428, LINE_103) == D(line_103)
    assert _value(nl428, LINE_104) == D(line_104)
    assert _value(summary, SLOPE) == D(slope)
    assert _value(summary, REDUCTION_GATE) == D(gate)
    assert _value(summary, PHASE_OUT) == D(phase_out)
    assert _value(summary, WITH_REDUCTION) == D(with_reduction)
    assert _value(summary, NL_RATE) == D(newfoundland)


def test_inside_the_reduction_range_the_provincial_part_is_the_bracket_rate_plus_16_points(
    service: TaxComputationService,
) -> None:
    summary = _summary(service, "28000")

    assert _value(summary, BRACKET) == D("0.087")
    assert _value(summary, PHASE_OUT) == D("0.16")
    assert _value(summary, NL_RATE) == D("0.247")
    assert _value(summary, MARGINAL) == D("0.145") + D("0.247")


def test_the_newfoundland_gate_closes_the_part_while_the_reduction_is_still_in_the_rate(
    service: TaxComputationService,
) -> None:
    summary = _summary(service, "24140.18")

    assert _value(summary, WITH_REDUCTION) == D("0.247")
    assert _value(summary, RATE_GATE) == D("0")
    assert _value(summary, NL_RATE) == D("0")
    assert _value(summary, MARGINAL) == D("0.145")


@pytest.mark.parametrize(
    ("salary", "line_105", "gate"),
    [
        ("20000", "0.00", "0"),
        ("24140.18", "0.00", "0"),
        ("24140.19", "0.01", "1"),
        ("28000", "921.72", "1"),
        ("70000", "6147.49", "1"),
        ("200000", "27192.33", "1"),
    ],
)
def test_the_gate_reads_nl428_line_105(
    service: TaxComputationService, salary: str, line_105: str, gate: str
) -> None:
    worksheets = _worksheets(service, salary)
    (nl428,) = worksheets["ca-nl/nl428"]
    (summary,) = worksheets[RETURN]

    assert _value(nl428, LINE_105) == D(line_105)
    assert _value(summary, RATE_GATE) == D(gate)


def test_the_marginal_rate_is_not_rounded_to_the_cent(service: TaxComputationService) -> None:
    # 0.145 + 0.247 = 0.392 keeps its third place: no cent rule is applied to a rate.
    value = _value(_summary(service, "28000"), MARGINAL)

    assert value == D("0.392")
    assert value.as_tuple().exponent == -3


def test_the_return_prints_the_rate_as_a_percentage_in_the_core_percent_unit(
    service: TaxComputationService,
) -> None:
    summary = _summary(service, "70000")

    unit = summary.unit(newfoundland_kinds().kind(MARGINAL).label)
    assert unit is not None
    assert unit.identifier == "core/percent"


def test_the_steps_after_line_167_have_no_reference_and_no_title(
    service: TaxComputationService,
) -> None:
    summary = _summary(service, "70000")
    kinds = newfoundland_kinds()

    for name in NEW_KINDS:
        label = kinds.kind(name).label
        assert summary.reference(label) is None
        assert summary.title(label) is None


def test_the_marginal_rate_is_traced_as_one_exact_sum_of_the_federal_then_the_nl_part(
    service: TaxComputationService,
) -> None:
    sheet = _summary(service, "200000")
    kinds = newfoundland_kinds()

    line = _sum_line(sheet)

    assert [(kind.label, value) for kind, value in line.parts] == [
        (kinds.kind(FEDERAL).label, D("0.29")),
        (kinds.kind(NL_RATE).label, D("0.178")),
    ]
    assert line.rounding == NO_ROUNDING
    assert line.total == D("0.468")
    assert line.amount == sheet.get(kinds.kind(MARGINAL)).value


def test_the_marginal_rate_is_explained_in_english_as_percentages(
    service: TaxComputationService,
) -> None:
    sheet = _summary(service, "70000")

    text = EnglishTraceRenderer().render(_sum_line(sheet), sheet)

    assert re.fullmatch(
        r".*\(20\.5%\) plus .+ \(14\.5(0+)?%\) gives 35(\.0+)?% \(not rounded\)\.?", text
    )


def test_the_marginal_rate_comes_last_in_the_trace(service: TaxComputationService) -> None:
    sheet = _summary(service, "100000")
    kinds = newfoundland_kinds()
    labels = [line.label for line in sheet.trace]

    marginal = labels.index(kinds.kind(MARGINAL).label)

    assert marginal == len(labels) - 1
    assert labels.count(kinds.kind(MARGINAL).label) == 1
    for part in (FEDERAL, NL_RATE):
        assert labels.index(kinds.kind(part).label) < marginal


@pytest.mark.parametrize(
    ("salary", "line_105"),
    [("28000", "921.72"), ("70000", "6147.49"), ("200000", "27192.33")],
)
def test_the_newfoundland_tax_anchors_do_not_move(
    service: TaxComputationService, salary: str, line_105: str
) -> None:
    (nl428,) = _worksheets(service, salary)["ca-nl/nl428"]

    assert _value(nl428, LINE_105) == D(line_105)
