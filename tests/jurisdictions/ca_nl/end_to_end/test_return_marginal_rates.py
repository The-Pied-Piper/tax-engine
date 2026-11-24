"""The Newfoundland and Labrador return summary carries the marginal income tax rate (2025), over
the real parts of the Newfoundland and Labrador manifest (salary the only input).

Newfoundland and Labrador is not yet listed in the registered engine, so the engine is built over
a temporary copy of the manifest folder (the `service` fixture of `tests/jurisdictions/ca_nl/
conftest.py`; `support.py` lists the packages).

Calculated the same way as British Columbia's, without a tax reduction term:

- The marginal rate (`ca-nl/marginal_tax_rate`) is the exact sum of two gated parts: the federal
  marginal rate (`ca/federal_marginal_rate`, the T1 line 73 bracket rate, counted only where T1
  line 42900 "Basic federal tax" is above 0) and the Newfoundland and Labrador marginal rate
  (`ca-nl/newfoundland_and_labrador_marginal_rate`): the NL428 line 5 rate, or the line 12 rate
  when line 5 is blank, counted only where NL428 line 85 is above 0. CPP and EI are not counted.
- The low-income tax reduction (NL428 lines 95 to 104) is not in the rate. Payroll (T4127, Jan 2025,
  Table 8.2) has no Newfoundland and Labrador low-income reduction factor, so the 16% phase-out
  between an adjusted family income of 23,928 and where the reduction ends adds nothing: at a
  salary of 28,000 the Newfoundland and Labrador part is 8.7%, not 8.7% + 16%. Ontario, British
  Columbia and Manitoba include their phase-outs because T4127 applies them; Manitoba leaves out
  the family tax benefit because T4127 does not.

Form text (Form NL428, CRA 5001-c-25e.txt): "Line 5: Rate 8.7%", "Rate 14.5%", "Rate 15.8%", "Rate
17.8%" (table 1, lines 2 to 8, up to $220,910); "Line 12: Rate 19.8%", "Rate 20.8%", "Rate 21.3%",
"Rate 21.8%" (table 2, above $220,910); "Line 85: Line 81 minus line 84 (if negative, enter "0")"
and "Line 105: Line 94 minus line 104 (if negative, enter "0")" (line 94 is line 87, line 85 less
line 86).

Every expected figure is derived by hand from the printed form lines and the federal and
Newfoundland and Labrador datasets (exact Decimal), never read from the engine. The net income is
the salary less the CPP enhanced contribution (1% of the salary less 3,500, to the cent; there is
no second additional contribution below 71,300). Line 85 is the tax on the net income (8.7% to the
cent) less the credits (8.7% of 11,067 plus the CPP base contribution, 4.95% of the salary less
3,500, plus the EI premium, 1.64% of the salary, each to the cent), not below 0.

The gates open at the zero-tax boundaries, found cent by cent from the same derivation (the part is
0 one cent below and counts at the cent pinned):

- federal: T1 line 42900 is 0.00 at 18,820.26 and 0.01 at 18,820.27;
- Newfoundland and Labrador: NL428 line 85 is 0.00 at 11,750.72 and 0.01 at 11,750.73.
"""

from __future__ import annotations

import re
from decimal import Decimal
from pathlib import Path

import pytest

import tax_engine.jurisdictions.ca_nl
from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.parameters.rounding import NO_ROUNDING
from tax_engine.domain.trace import SumLine
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tests.jurisdictions.ca_nl.support import (
    newfoundland_kinds,
)
from tests.kinds import non_negative

D = Decimal
NL_PARTS = Path(tax_engine.jurisdictions.ca_nl.__file__).parent / "manifests" / "2025"
NEWFOUNDLAND = JurisdictionCode("CA-NL")
RETURN = "ca-nl/return"
FEDERAL = "ca/federal_marginal_rate"
NL_RATE = "ca-nl/newfoundland_and_labrador_marginal_rate"
MARGINAL = "ca-nl/marginal_tax_rate"
LINE_5_RETURN = "ca-nl/newfoundland_and_labrador_bracket_rate_line_5_return"
LINE_12_RETURN = "ca-nl/newfoundland_and_labrador_bracket_rate_line_12_return"
BRACKET = "ca-nl/newfoundland_and_labrador_bracket_rate_return"
RATE_GATE = "ca-nl/newfoundland_and_labrador_rate_gate"
LINE_85 = "ca-nl/nl428_tax_line_85"
LINE_105 = "ca-nl/nl428_newfoundland_and_labrador_tax_line_105"
NEW_KINDS = [
    MARGINAL,
    NL_RATE,
    LINE_5_RETURN,
    LINE_12_RETURN,
    BRACKET,
    "ca-nl/newfoundland_and_labrador_tax_after_credits_return",
    RATE_GATE,
]

# Salary, federal part, Newfoundland and Labrador part, marginal rate.
FIGURES = [
    # Salaries of 0 and 100: no tax at all, both gates closed.
    ("0", "0", "0", "0"),
    ("100", "0", "0", "0"),
    # Newfoundland and Labrador boundary: closed at 11,750.72 (line 85 is 0.00), open (8.7%) at
    # 11,750.73; the federal gate is still closed.
    ("11750.72", "0", "0", "0"),
    ("11750.73", "0", "0.087", "0.087"),
    # Federal boundary: closed at 18,820.26, open (14.5%) at 18,820.27.
    ("18820.26", "0", "0.087", "0.087"),
    ("18820.27", "0.145", "0.087", "0.232"),
    # 20,000 and 28,000 (net income 27,755.00) are inside the low-income reduction range, but the
    # rate is 8.7% as payroll has no reduction term: 14.5% + 8.7% = 23.2%, not 39.2%.
    ("20000", "0.145", "0.087", "0.232"),
    ("24140.19", "0.145", "0.087", "0.232"),
    ("28000", "0.145", "0.087", "0.232"),
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


def _worksheets(service: TaxComputationService, salary: str) -> dict[str, tuple[Worksheet, ...]]:
    return service.compute(
        TaxCalculationRequest(NEWFOUNDLAND, 2025, (Artifact(EMPLOYMENT_INCOME, D(salary)),))
    )


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


@pytest.mark.parametrize("name", [MARGINAL, NL_RATE, BRACKET])
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


@pytest.mark.parametrize("salary", ["20000", "24140.19", "28000", "30428.50"])
def test_the_low_income_reduction_is_not_in_the_provincial_part(
    service: TaxComputationService, salary: str
) -> None:
    worksheets = _worksheets(service, salary)
    (nl428,) = worksheets["ca-nl/nl428"]
    (summary,) = worksheets[RETURN]

    # The form still reduces the tax up to a net income of 30,159.22 (a salary of 30,428.50), but
    # the rate is the bracket rate alone.
    assert _value(nl428, LINE_85) > _value(nl428, LINE_105)
    assert _value(summary, NL_RATE) == _value(summary, BRACKET) == D("0.087")


@pytest.mark.parametrize(
    ("salary", "line_85", "line_105", "gate"),
    [
        ("11750.72", "0.00", "0.00", "0"),
        ("11750.73", "0.01", "0.00", "1"),
        ("20000", "663.23", "0.00", "1"),
        ("28000", "1306.40", "921.72", "1"),
        ("70000", "6147.49", "6147.49", "1"),
        ("200000", "27192.33", "27192.33", "1"),
    ],
)
def test_the_gate_reads_nl428_line_85_not_line_105(
    service: TaxComputationService, salary: str, line_85: str, line_105: str, gate: str
) -> None:
    worksheets = _worksheets(service, salary)
    (nl428,) = worksheets["ca-nl/nl428"]
    (summary,) = worksheets[RETURN]

    assert _value(nl428, LINE_85) == D(line_85)
    assert _value(nl428, LINE_105) == D(line_105)
    assert _value(summary, RATE_GATE) == D(gate)


def test_the_marginal_rate_is_not_rounded_to_the_cent(service: TaxComputationService) -> None:
    # 0.145 + 0.087 = 0.232 keeps its third place: no cent rule is applied to a rate.
    value = _value(_summary(service, "28000"), MARGINAL)

    assert value == D("0.232")
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


def test_the_marginal_rate_comes_last_of_the_marginal_steps_in_the_trace(
    service: TaxComputationService,
) -> None:
    sheet = _summary(service, "100000")
    kinds = newfoundland_kinds()
    labels = [line.label for line in sheet.trace]

    marginal = labels.index(kinds.kind(MARGINAL).label)

    # Only the two steps of the average rate (the total and the quotient) come after it.
    assert labels[marginal + 1 :] == [
        kinds.kind("ca/return_total_deductions").label,
        kinds.kind("ca-nl/average_tax_rate").label,
    ]
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
