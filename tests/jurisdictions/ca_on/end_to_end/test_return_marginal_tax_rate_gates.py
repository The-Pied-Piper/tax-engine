"""The marginal tax rate counts each tax rate only where its own tax is above zero, through the
real engine.

The marginal tax rate is the change in the take-home deductions on the next dollar of salary: the
federal and Ontario tax rates (with the credits on CPP and EI, the Ontario surtax, the health
premium and the LIFT phase-out), plus the CPP and EI rates. A tax rate counts only where its own
tax is above zero, through a gate: 0 where the tax is 0.00 and 1 where it is a cent or more. At a
salary of 100 the rate was 19.55% before the gates, because every part read the bracket rate.

- Federal: T1 line 42900 "Basic federal tax" (`ca/federal_tax_after_credits`, read into
  `ca/marginal_basic_federal_tax` by the federal form `ca/take_home_marginal_rates`) gives
  `ca/marginal_federal_gate`; the federal marginal rate (`ca/marginal_federal_rate`, read into the
  return as `ca-on/marginal_federal_rate`) is the federal rate after the credits times that
  gate. Not line 42000: the lines between 42900 and 42000 (foreign tax credit, logging credit,
  political and other credits, ITC recapture, T2203 surtax) are return-only and must not move the
  gate.
- Ontario: ON428 line 86 "Ontario tax after the LIFT credit" (`ca-on/on428_tax_after_lift_credit_
  line_86`, read into `ca-on/ontario_tax_after_lift_return`) gives `ca-on/ontario_rate_gate`; the
  Ontario marginal rate (`ca-on/ontario_marginal_rate`) is the Ontario rate after the credits, the
  surtax, the tax reduction's phase-out and the LIFT phase-out times that gate. Line 86, not line
  81: where the LIFT credit takes all the Ontario tax a further dollar adds none, as at 20,000,
  where line 81 is 12.28 and the credit is 875.00. Not line 90 (adds the health premium).
- The Ontario tax reduction phase-out: ON428 line 80 "Ontario tax reduction"
  (`ca-on/on428_ontario_tax_reduction_line_80`, read into `ca-on/ontario_tax_reduction_return`)
  gives `ca-on/ontario_reduction_gate` (1 while it is above 0). While lines 80 and 81 are both above
  0, line 81 is 2 x line 73 less 588, so the Ontario rate is double
  (`ca-on/marginal_ontario_rate_with_reduction`); the doubling only shows in the Ontario marginal
  rate where line 86 is above 0, which a salary-only return does not reach (the LIFT credit is
  875.00 from 17,327 to 32,318).
- The health premium rate is the rate of the ON428 line 89 chart row of the taxable income (6% from
  20,000 to 25,000, 0 in a flat row) times the part of a dollar left in the taxable income.

The printed rates and the hand-worked figures are in `test_return_marginal_tax_rate_values.py`;
here the thresholds are measured. Thresholds, salary only, 2025: basic federal tax (line 42900) is
first positive at 18,820.27 (at 18,820.26 the tax before credits equals the credits, 2,706.72),
ON428 line 81 at 19,868.74 (0.02; 0.00 at 19,868.73), ON428 line 80 is 0.01 at 26,168.36 and 0.00
from 26,168.37, and ON428 line 86 first positive at 32,318.59 (0.01; 0.00 at 32,318.58).

At 100 and 18,820.26 the rate is the contribution rate only (0 at 100, 0.0759 at 18,820.26, CPP
4.95% + 1% and EI 1.64%); at 18,820.27 the federal tax part opens: 14.5% x 0.99 - 14.5% x 0.0659 =
0.1339945.
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
ONTARIO = JurisdictionCode("CA-ON")
RETURN = "ca-on/return"

FEDERAL_FORM = "ca/take_home_marginal_rates"
BASIC_FEDERAL_TAX = "ca/marginal_basic_federal_tax"
TAX_AFTER_LIFT = "ca-on/ontario_tax_after_lift_return"
TAX_REDUCTION = "ca-on/ontario_tax_reduction_return"
REDUCTION_GATE = "ca-on/ontario_reduction_gate"
WITH_REDUCTION = "ca-on/marginal_ontario_rate_with_reduction"
PHASE_OUT = "ca-on/ontario_reduction_phase_out_rate"
FEDERAL_GATE = "ca/marginal_federal_gate"
ONTARIO_GATE = "ca-on/ontario_rate_gate"
FEDERAL_BRACKET = "ca/marginal_federal_bracket_column_rate"
ONTARIO_BRACKET = "ca-on/ontario_bracket_rate_return"
FEDERAL = "ca-on/marginal_federal_rate"
ONTARIO_RATE = "ca-on/ontario_marginal_rate"
PREMIUM = "ca-on/marginal_health_premium_rate"
CONTRIBUTION = "ca-on/marginal_contribution_rate"
MARGINAL = "ca-on/marginal_tax_rate"

# Salary, then the federal marginal rate, the Ontario marginal rate, the health premium rate, the
# contribution rate and the marginal tax rate, worked by hand from the printed rates and the gates.
PARTS = [
    # No tax and no contribution: every part is 0 although the bracket rates are 14.5% and 5.05%.
    ("100", "0", "0", "0", "0", "0"),
    # T2204 line 16 rises 1 for 1 between 2,000 and 2,033: the EI rate is 1.
    ("2001", "0", "0", "0", "1", "1"),
    # Contributions only: CPP 4.95% + 1% and EI 1.64%, no basic federal tax yet.
    ("18820.26", "0", "0", "0", "0.0759", "0.0759"),
    # Basic federal tax is first positive: the federal part opens.
    ("18820.27", "0.1339945", "0", "0", "0.0759", "0.2098945"),
    # ON428 line 81 is positive from 19,868.74 but the LIFT credit (875.00) takes all of it: the
    # Ontario part stays 0 through the tax reduction band, up to 32,318.58.
    ("20000", "0.1339945", "0", "0", "0.0759", "0.2098945"),
    # The health premium rate shows (6% x 0.99 in the 20,000 to 25,000 row).
    ("22000", "0.1339945", "0", "0.0594", "0.0759", "0.2692945"),
    ("26168.37", "0.1339945", "0", "0", "0.0759", "0.2098945"),
    ("32318.58", "0.1339945", "0", "0", "0.0759", "0.2098945"),
    # ON428 line 86 is first positive: 5.05% x 0.99 - 5.05% x 0.0659 = 0.04666705.
    ("32318.59", "0.1339945", "0.04666705", "0", "0.0759", "0.25656155"),
    # In the 25% health premium row (25% x 0.99) and the LIFT credit falling 5% x 0.99 a dollar.
    ("48800", "0.1339945", "0.09616705", "0.2475", "0.0759", "0.55356155"),
    # Above the EI maximum of 65,700: CPP 4.95% + 1% only.
    ("70000", "0.1957725", "0.08808525", "0", "0.0595", "0.34335775"),
    ("120000", "0.26", "0.174096", "0", "0", "0.434096"),
    ("275000", "0.33", "0.205296", "0", "0", "0.535296"),
]


def _summary(salary: str) -> Worksheet:
    # No fixture: the bundled Ontario manifest, as the calculator loads it, salary the only input.
    worksheets = build_tax_computation().compute(
        TaxCalculationRequest(ONTARIO, 2025, (Artifact(EMPLOYMENT_INCOME, D(salary)),))
    )
    (summary,) = worksheets[RETURN]
    return summary


def _federal(salary: str) -> Worksheet:
    # The federal form's sheet, which holds the federal gate and the federal bracket rate.
    worksheets = build_tax_computation().compute(
        TaxCalculationRequest(ONTARIO, 2025, (Artifact(EMPLOYMENT_INCOME, D(salary)),))
    )
    (federal,) = worksheets[FEDERAL_FORM]
    return federal


def _value(summary: Worksheet, name: str) -> Decimal:
    value = summary.get(bundled_kinds().kind(name)).value
    assert isinstance(value, Decimal)
    return value


@pytest.mark.parametrize(
    ("salary", "federal", "ontario", "premium", "contribution", "marginal"), PARTS
)
def test_each_part_and_the_total_of_the_marginal_tax_rate(
    salary: str, federal: str, ontario: str, premium: str, contribution: str, marginal: str
) -> None:
    summary = _summary(salary)

    assert _value(summary, FEDERAL) == D(federal)
    assert _value(summary, ONTARIO_RATE) == D(ontario)
    assert _value(summary, PREMIUM) == D(premium)
    assert _value(summary, CONTRIBUTION) == D(contribution)
    assert _value(summary, MARGINAL) == D(marginal)
    assert D(federal) + D(ontario) + D(premium) + D(contribution) == D(marginal)


@pytest.mark.parametrize(
    ("salary", "federal_tax_is_positive", "ontario_tax_is_positive"),
    [
        ("100", False, False),
        ("18820.26", False, False),
        ("18820.27", True, False),
        ("19868.74", True, False),
        ("32318.58", True, False),
        ("32318.59", True, True),
        ("70000", True, True),
    ],
)
def test_the_gates_open_with_the_taxes_they_read(
    salary: str, federal_tax_is_positive: bool, ontario_tax_is_positive: bool
) -> None:
    summary = _summary(salary)

    assert (_value(_federal(salary), BASIC_FEDERAL_TAX) > 0) is federal_tax_is_positive
    assert (_value(summary, TAX_AFTER_LIFT) > 0) is ontario_tax_is_positive
    assert _value(_federal(salary), FEDERAL_GATE) == D(int(federal_tax_is_positive))
    assert _value(summary, ONTARIO_GATE) == D(int(ontario_tax_is_positive))


@pytest.mark.parametrize("salary", ["100", "18820.26", "18820.27", "19868.73", "19868.74"])
def test_the_bracket_rates_read_by_the_gates_are_ungated(salary: str) -> None:
    # The gate changes the part, not the bracket rate it multiplies: 14.5% and 5.05% at every
    # one of these salaries.
    summary = _summary(salary)

    assert _value(_federal(salary), FEDERAL_BRACKET) == D("0.145")
    assert _value(summary, ONTARIO_BRACKET) == D("0.0505")


def test_the_ontario_gate_follows_line_86_and_not_line_81() -> None:
    # At 20,000 ON428 line 81 is positive while line 86 (after the LIFT credit) is 0.00, and the
    # gate follows line 86, so the Ontario part is absent.
    kinds = bundled_kinds()
    summary = _summary("20000")
    (on428,) = build_tax_computation().compute(
        TaxCalculationRequest(ONTARIO, 2025, (Artifact(EMPLOYMENT_INCOME, D("20000")),))
    )["ca-on/on428"]

    assert on428.get(kinds.kind("ca-on/on428_tax_after_tax_reduction_line_81")).value > 0
    assert on428.get(kinds.kind("ca-on/on428_tax_after_lift_credit_line_86")).value == D("0")
    assert _value(summary, ONTARIO_GATE) == D("0")
    assert _value(summary, ONTARIO_RATE) == D("0")


@pytest.mark.parametrize(
    ("salary", "reduction_is_positive"),
    [
        ("19868.74", True),
        ("20000", True),
        ("25000", True),
        ("26168.36", True),
        ("26168.37", False),
        ("30000", False),
        ("70000", False),
    ],
)
def test_the_reduction_gate_follows_the_ontario_tax_reduction(
    salary: str, reduction_is_positive: bool
) -> None:
    # ON428 line 80 is 0.01 at 26,168.36 and 0.00 at 26,168.37 (not the line 81 gate: line 81 is
    # above 0 from 19,868.74 on).
    summary = _summary(salary)

    assert (_value(summary, TAX_REDUCTION) > 0) is reduction_is_positive
    assert _value(summary, REDUCTION_GATE) == D(int(reduction_is_positive))


@pytest.mark.parametrize(
    ("salary", "phase_out", "with_reduction"),
    [
        # 5.05% x 0.99 - 5.05% x 0.0659 = 0.04666705, counted twice while line 80 is positive.
        ("19868.74", "0.04666705", "0.0933341"),
        ("25000", "0.04666705", "0.0933341"),
        ("26168.36", "0.04666705", "0.0933341"),
        ("26168.37", "0", "0.04666705"),
        ("30000", "0", "0.04666705"),
        ("70000", "0", "0.08808525"),
    ],
)
def test_the_ontario_rate_doubles_while_line_80_is_positive(
    salary: str, phase_out: str, with_reduction: str
) -> None:
    summary = _summary(salary)

    assert _value(summary, PHASE_OUT) == D(phase_out)
    assert _value(summary, WITH_REDUCTION) == D(with_reduction)
