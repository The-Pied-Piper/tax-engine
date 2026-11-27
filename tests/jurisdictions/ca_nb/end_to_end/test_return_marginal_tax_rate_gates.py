"""The gated New Brunswick marginal tax rate, 2025, through the real engine.

The salary-only case, 2025. New Brunswick's low-income tax reduction absorbs the provincial tax at
low salaries, so the provincial part opens late and is steepest while the reduction is phased out.

The provincial part is counted only while NB428 line 97 "Line 95 minus line 96 (if negative, enter
"0")" is above zero, and the low-income tax reduction slope (3%, NB428 line 84) only while NB428
line 83 and line 86 are both above zero. Each boundary below is found cent by cent from the engine
and checked against the printed form worked by hand, and each rate is the hand-worked figure of
`test_return_marginal_tax_rate_values.py`; each other salary pins the structure: the gates are 0
or 1 and open with the amounts they read, the provincial part is its gate times its rate, and the
total is the exact sum of the three parts.

- line 97 is 0.00 at a salary of 23,147.59 and 0.01 at 23,147.60 (the reduction absorbs the tax);
- line 83 is 0.00 at 22,106.06 and 0.01 at 22,106.07 (the net income passes the base amount of
  21,920); line 86 is 0.01 at 49,109.08 and 0.00 at 49,109.09 (the net income reaches the single
  income limit of 48,653, which ends the reduction); in between the provincial part is 9.4% x 0.99
  - 9.4% x 0.0659 + 3% x 0.99 = 0.1165654, and after it 0.0868654.

The engine rounds the marginal tax rate half-up to 0.0001 like the average rate
(`ca/take_home_average_rate_rounding`), so the marginal column of PARTS is the exact sum of the
parts, kept in the comments, rounded half-up to four places (e.g. 0.2098945 is 0.2099); the parts
themselves stay exact.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine import build_tax_computation
from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tests.kinds import bundled_kinds

D = Decimal
NEW_BRUNSWICK = JurisdictionCode("CA-NB")
YEAR = 2025
RETURN = "ca-nb/return"
FEDERAL_FORM = "ca/take_home_marginal_rates"

BASIC_FEDERAL_TAX = "ca/marginal_basic_federal_tax"
FEDERAL_GATE = "ca/marginal_federal_gate"
LINE_97 = "ca-nb/new_brunswick_tax_return"
TAX_GATE = "ca-nb/new_brunswick_rate_gate"
REDUCTION_RATE = "ca-nb/marginal_new_brunswick_rate_with_reduction"
INCOME_GATE = "ca-nb/income_over_base_amount_gate"
REDUCTION_GATE = "ca-nb/low_income_tax_reduction_gate"
PHASE_OUT_GATE = "ca-nb/low_income_reduction_phase_out_gate"
FEDERAL = "ca-nb/marginal_federal_rate"
PROVINCIAL = "ca-nb/new_brunswick_marginal_rate"
CONTRIBUTION = "ca-nb/marginal_contribution_rate"
MARGINAL = "ca-nb/marginal_tax_rate"

# Salary, then the federal marginal rate, the New Brunswick marginal rate, the contribution rate and
# the marginal tax rate, worked by hand from the printed rates and the gates.
PARTS = [
    # No tax and no contribution: every part is 0 although the bracket rates are 14.5% and 9.4%.
    ("100", "0", "0", "0", "0"),
    # T2204 line 16 rises 1 for 1 between 2,000 and 2,033: the EI rate is 1.
    ("2001", "0", "0", "1", "1"),
    # Contributions only: CPP 4.95% + 1% and EI 1.64%, no basic federal tax yet.
    ("18820.26", "0", "0", "0.0759", "0.0759"),
    # Basic federal tax is first positive: 14.5% x 0.99 - 14.5% x 0.0659 = 0.1339945.
    ("18820.27", "0.1339945", "0", "0.0759", "0.2099"),
    ("23147.59", "0.1339945", "0", "0.0759", "0.2099"),
    # NB428 line 97 is first positive: 9.4% x 0.99 - 9.4% x 0.0659 + 3% x 0.99 = 0.1165654.
    ("23147.60", "0.1339945", "0.1165654", "0.0759", "0.3265"),
    ("49109.08", "0.1339945", "0.1165654", "0.0759", "0.3265"),
    # The reduction ends (NB428 line 86 is 0.00): 9.4% x 0.99 - 9.4% x 0.0659 = 0.0868654.
    ("49109.09", "0.1339945", "0.0868654", "0.0759", "0.2968"),
    # Above the EI maximum of 65,700: CPP 4.95% + 1% only; the net income is in the 14% column:
    # 14% x 0.99 - 9.4% x 0.0495 = 0.133947.
    ("70000", "0.1957725", "0.133947", "0.0595", "0.3892"),
    # Above the CPP ceilings: the net income rate is 1 and no contribution is left; the net income
    # of 152,750 is in the 16% column.
    ("153824", "0.26", "0.16", "0", "0.42"),
]


def _summary(salary: str) -> Worksheet:
    # No fixture: the bundled New Brunswick manifest, as the calculator loads it,
    # salary the only input.
    worksheets = build_tax_computation().compute(
        TaxCalculationRequest(NEW_BRUNSWICK, YEAR, (Artifact(EMPLOYMENT_INCOME, D(salary)),))
    )
    (summary,) = worksheets[RETURN]
    return summary


def _federal(salary: str) -> Worksheet:
    # The federal form's sheet, which holds the federal gate.
    worksheets = build_tax_computation().compute(
        TaxCalculationRequest(NEW_BRUNSWICK, YEAR, (Artifact(EMPLOYMENT_INCOME, D(salary)),))
    )
    (federal,) = worksheets[FEDERAL_FORM]
    return federal


def _value(sheet: Worksheet, name: str) -> Decimal:
    value = sheet.get(bundled_kinds().kind(name)).value
    assert isinstance(value, Decimal)
    return value


@pytest.mark.parametrize(
    ("salary", "gate", "provincial"),
    [
        ("23147.59", "0", "0"),
        ("23147.60", "1", "0.1165654"),
        ("49109.08", "1", "0.1165654"),
        ("49109.09", "1", "0.0868654"),
    ],
)
def test_2025_the_provincial_part_follows_line_97_and_the_reduction_phase_out(
    salary: str, gate: str, provincial: str
) -> None:
    summary = _summary(salary)

    assert _value(summary, TAX_GATE) == D(gate)
    assert _value(summary, PROVINCIAL) == D(provincial)


@pytest.mark.parametrize(
    ("salary", "income_gate", "reduction_gate"),
    [
        ("22106.06", "0", "1"),
        ("22106.07", "1", "1"),
        ("49109.08", "1", "1"),
        ("49109.09", "1", "0"),
    ],
)
def test_2025_the_phase_out_gates_open_where_lines_83_and_86_turn_positive_or_zero(
    salary: str, income_gate: str, reduction_gate: str
) -> None:
    summary = _summary(salary)

    assert _value(summary, INCOME_GATE) == D(income_gate)
    assert _value(summary, REDUCTION_GATE) == D(reduction_gate)
    assert _value(summary, PHASE_OUT_GATE) == D(income_gate) * D(reduction_gate)


@pytest.mark.parametrize(("salary", "federal", "provincial", "contribution", "marginal"), PARTS)
def test_each_part_and_the_total_of_the_marginal_tax_rate(
    salary: str, federal: str, provincial: str, contribution: str, marginal: str
) -> None:
    summary = _summary(salary)

    assert _value(summary, FEDERAL) == D(federal)
    assert _value(summary, PROVINCIAL) == D(provincial)
    assert _value(summary, CONTRIBUTION) == D(contribution)
    assert _value(summary, MARGINAL) == D(marginal)


@pytest.mark.parametrize(
    ("salary", "basic_federal_tax", "federal_gate"),
    [
        ("18820.26", "0.00", "0"),
        ("18820.27", "0.01", "1"),
    ],
)
def test_the_federal_gate_opens_where_the_basic_federal_tax_is_first_above_zero(
    salary: str, basic_federal_tax: str, federal_gate: str
) -> None:
    federal = _federal(salary)

    assert _value(federal, BASIC_FEDERAL_TAX) == D(basic_federal_tax)
    assert _value(federal, FEDERAL_GATE) == D(federal_gate)


@pytest.mark.parametrize(
    ("salary", "line_97", "provincial_gate"),
    [
        ("23147.59", "0.00", "0"),
        ("23147.60", "0.01", "1"),
    ],
)
def test_the_provincial_gate_opens_where_line_97_is_first_above_zero(
    salary: str, line_97: str, provincial_gate: str
) -> None:
    summary = _summary(salary)

    assert _value(summary, LINE_97) == D(line_97)
    assert _value(summary, TAX_GATE) == D(provincial_gate)
