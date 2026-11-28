"""The gated Nova Scotia marginal tax rate, 2025, through the real engine.

The salary-only case, 2025. Nova Scotia's low-income tax reduction absorbs the provincial tax at low
salaries, so the provincial part opens late and is steepest while the reduction is phased out.

The provincial part is counted only while NS428 line 99 "Line 97 minus line 98 (if negative, enter
"0")" is above zero, and the low-income tax reduction slope (5%, NS428 line 82) only while NS428
line 81 and line 84 are both above zero. Each boundary below is found cent by cent from the engine,
and each rate is the hand-worked figure of `test_return_marginal_tax_rate_values.py`; each other
salary pins the structure: the gates are 0 or 1 and open with the amounts they read, the provincial
part is its gate times its rate, and the total is the exact sum of the three parts.

- line 99 is 0.00 at a salary of 15,775.04 and 0.01 at 15,775.05 (the reduction absorbs the tax);
- line 81 is 0.00 at 15,116.16 and 0.01 at 15,116.17 (the net income passes the base amount of
  15,000); line 84 is 0.01 at 21,176.66 and 0.00 at 21,176.67 (the reduction is used up); in
  between the provincial part is 8.79% x 0.99 - 8.79% x 0.0659 + 5% x 0.99 = 0.13072839, and after
  it 0.08122839.

The engine rounds the marginal tax rate half-up to 0.0001 like the average rate
(`ca/take_home_average_rate_rounding`), so the marginal column of PARTS is the exact sum of the
parts, kept in the comments, rounded half-up to four places (e.g. 0.29112289 is 0.2911); the parts
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
from tax_engine.jurisdictions.ca.catalog.personal_amounts import BIRTH_YEAR
from tests.kinds import bundled_kinds

D = Decimal
NOVA_SCOTIA = JurisdictionCode("CA-NS")
YEAR = 2025
RETURN = "ca-ns/return"
FEDERAL_FORM = "ca/take_home_marginal_rates"

BASIC_FEDERAL_TAX = "ca/marginal_basic_federal_tax"
FEDERAL_GATE = "ca/marginal_federal_gate"
LINE_99 = "ca-ns/nova_scotia_tax_return"
TAX_GATE = "ca-ns/nova_scotia_rate_gate"
REDUCTION_RATE = "ca-ns/marginal_nova_scotia_rate_with_reduction"
INCOME_GATE = "ca-ns/income_over_low_income_threshold_gate"
REDUCTION_GATE = "ca-ns/low_income_tax_reduction_gate"
PHASE_OUT_GATE = "ca-ns/low_income_reduction_phase_out_gate"
FEDERAL = "ca-ns/marginal_federal_rate"
PROVINCIAL = "ca-ns/nova_scotia_marginal_rate"
CONTRIBUTION = "ca-ns/marginal_contribution_rate"
MARGINAL = "ca-ns/marginal_tax_rate"

# Salary, then the federal marginal rate, the Nova Scotia marginal rate, the
# contribution rate and the marginal tax rate, worked by hand from the printed rates and the gates.
PARTS = [
    # No tax and no contribution: every part is 0 although the bracket rates are 14.5% and 8.79%.
    ("100", "0", "0", "0", "0"),
    # T2204 line 16 rises 1 for 1 between 2,000 and 2,033: the EI rate is 1.
    ("2001", "0", "0", "1", "1"),
    # Contributions only: the reduction absorbs the Nova Scotia tax and no federal tax yet.
    ("15775.04", "0", "0", "0.0759", "0.0759"),
    # NS428 line 99 is first positive: 8.79% x 0.99 - 8.79% x 0.0659 + 5% x 0.99 = 0.13072839.
    ("15775.05", "0", "0.13072839", "0.0759", "0.2066"),
    ("18820.26", "0", "0.13072839", "0.0759", "0.2066"),
    # Basic federal tax is first positive: 14.5% x 0.99 - 14.5% x 0.0659 = 0.1339945.
    ("18820.27", "0.1339945", "0.13072839", "0.0759", "0.3406"),
    ("21176.66", "0.1339945", "0.13072839", "0.0759", "0.3406"),
    # The reduction is used up (NS428 line 84 is 0.00): 8.79% x 0.99 - 8.79% x 0.0659 = 0.08122839.
    ("21176.67", "0.1339945", "0.08122839", "0.0759", "0.2911"),
    # Above the EI maximum of 65,700: CPP 4.95% + 1% only; 20.5% x 0.99 - 14.5% x 0.0495 federal and
    # 16.67% x 0.99 - 8.79% x 0.0495 Nova Scotia.
    ("70000", "0.1957725", "0.16068195", "0.0595", "0.4160"),
    # Above the CPP ceilings: the net income rate is 1 and no contribution is left.
    ("275000", "0.33", "0.21", "0", "0.5400"),
]


def _summary(salary: str) -> Worksheet:
    # No fixture: the bundled Nova Scotia manifest, as the calculator loads it,
    # salary the only input.
    worksheets = build_tax_computation().compute(
        TaxCalculationRequest(NOVA_SCOTIA, YEAR, (Artifact(EMPLOYMENT_INCOME, D(salary)),))
    )
    (summary,) = worksheets[RETURN]
    return summary


def _federal(salary: str) -> Worksheet:
    # The federal form's sheet, which holds the federal gate.
    worksheets = build_tax_computation().compute(
        TaxCalculationRequest(NOVA_SCOTIA, YEAR, (Artifact(EMPLOYMENT_INCOME, D(salary)),))
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
        ("15775.04", "0", "0"),
        ("15775.05", "1", "0.13072839"),
        ("21176.66", "1", "0.13072839"),
        ("21176.67", "1", "0.08122839"),
    ],
)
def test_2025_the_provincial_part_follows_line_99_and_the_reduction_phase_out(
    salary: str, gate: str, provincial: str
) -> None:
    summary = _summary(salary)

    assert _value(summary, TAX_GATE) == D(gate)
    assert _value(summary, PROVINCIAL) == D(provincial)


@pytest.mark.parametrize(
    ("salary", "income_gate", "reduction_gate"),
    [
        ("15116.16", "0", "1"),
        ("15116.17", "1", "1"),
        ("21176.66", "1", "1"),
        ("21176.67", "1", "0"),
    ],
)
def test_2025_the_phase_out_gates_open_where_lines_81_and_84_turn_positive_or_zero(
    salary: str, income_gate: str, reduction_gate: str
) -> None:
    summary = _summary(salary)

    assert _value(summary, INCOME_GATE) == D(income_gate)
    assert _value(summary, REDUCTION_GATE) == D(reduction_gate)


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
    ("salary", "line_99", "provincial_gate"),
    [
        ("15775.04", "0.00", "0"),
        ("15775.05", "0.01", "1"),
    ],
)
def test_the_provincial_gate_opens_where_line_99_is_first_above_zero(
    salary: str, line_99: str, provincial_gate: str
) -> None:
    summary = _summary(salary)

    assert _value(summary, LINE_99) == D(line_99)
    assert _value(summary, TAX_GATE) == D(provincial_gate)


# Salary, over the threshold (worksheet line 4), age amount claimed (before the printed maximum
# check), the two age gates and the age term, for a filer born in 1955 (the Nova Scotia part and
# the age term are the hand-worked figures of `test_return_marginal_tax_rate_values.py`).
BORN_1955_GATES = [
    # 2025: net income = salary less 1% of the salary over 3,500.
    # $0: nothing yet; the threshold gate is shut and no tax.
    ("0", "0.00", "5734.00", "0", "1", "0"),
    # Net income 30,828.00 = the threshold: line 4 is 0.00, no effect.
    ("31104.04", "0.00", "5734.00", "0", "1", "0"),
    # Net income 30,828.01: one cent over; the whole 15% starts at once.
    ("31104.05", "0.01", "5734.00", "1", "1", "0.01305315"),
    # Net income 30,829.00: $1 over; line 6 is 0.15, line 7 is 5,733.85.
    ("31105.05", "1.00", "5733.85", "1", "1", "0.01305315"),
    # Net income 39,635.00: 8,807 over; line 6 is 1,321.05, line 7 is 4,412.95.
    ("40000", "8807.00", "4412.95", "1", "1", "0.01305315"),
    # Net income 69,054.63: line 4 is 38,226.63, line 7 is 0.01, the last cent with an amount left.
    # (Line 6 reaches the maximum 5,734 at line 4 = 38,226.64: 5,733.996 rounds to 5,734.00, and
    # 38,226.63 gives 5,733.9945, which rounds to 5,733.99.)
    ("69716.80", "38226.63", "0.01", "1", "1", "0.01305315"),
    # Net income 69,054.64: line 6 rounds to 5,734.00, nothing is left, the term is off again.
    ("69716.81", "38226.64", "0.00", "1", "0", "0"),
]


def _born_1955(salary: str) -> Worksheet:
    worksheets = build_tax_computation().compute(
        TaxCalculationRequest(
            NOVA_SCOTIA,
            YEAR,
            (Artifact(EMPLOYMENT_INCOME, D(salary)), Artifact(BIRTH_YEAR, 1955)),
        )
    )
    (summary,) = worksheets[RETURN]
    return summary


@pytest.mark.parametrize(
    ("salary", "over", "claimed", "threshold_gate", "amount_gate", "term"), BORN_1955_GATES
)
def test_born_1955_the_age_amount_falls_only_over_the_threshold_and_while_some_is_left(
    salary: str,
    over: str,
    claimed: str,
    threshold_gate: str,
    amount_gate: str,
    term: str,
) -> None:
    summary = _born_1955(salary)

    assert _value(summary, "ca-ns/marginal_age_income_over_threshold") == D(over)
    assert _value(summary, "ca-ns/marginal_age_amount_claimed") == D(claimed)
    assert _value(summary, "ca-ns/marginal_age_threshold_gate") == D(threshold_gate)
    assert _value(summary, "ca-ns/marginal_age_amount_gate") == D(amount_gate)
    assert _value(summary, "ca-ns/marginal_nova_scotia_age_credit_rate") == D(term)


@pytest.mark.parametrize("salary", ["31104.05", "40000", "69716.80", "69716.81"])
def test_born_1955_the_line_99_gate_still_governs_the_age_term(salary: str) -> None:
    # The age term is inside the provincial part, which is the line 99 gate times the rate.
    summary = _born_1955(salary)

    assert _value(summary, TAX_GATE) == D("1")
    assert _value(summary, PROVINCIAL) == _value(summary, TAX_GATE) * _value(
        summary, REDUCTION_RATE
    )
