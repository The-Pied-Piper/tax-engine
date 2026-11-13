"""The marginal tax rate counts each bracket-rate part only where its own tax is above zero,
through the real engine.

The marginal tax rate is the income tax on the next dollar, including the Ontario surtax and health
premium; CPP and EI are not counted. Before the fix every part read the bracket rate of the taxable
income row, so the rate was 19.55% at a salary of 100 and at every salary below 18,820.27. Each
part now reads a gate: 0 where its tax is 0.00 and 1 where it is a cent or more.

- Federal: T1 line 42900 "Basic federal tax" (`ca/federal_tax_after_credits`, read into
  `ca/federal_tax_after_credits_return`) gives `ca/federal_rate_gate`; the federal marginal rate
  (`ca/federal_marginal_rate`) is that gate times the T1 line 73 "Line 73: Rate"
  (`ca/federal_bracket_rate_return`). Not line 42000: the lines between 42900 and 42000 (foreign
  tax credit, logging credit, political and other credits, ITC recapture, T2203 surtax) are
  return-only and must not move the gate.
- Ontario: ON428 line 81 "Ontario tax after the Ontario tax reduction"
  (`ca-on/on428_tax_after_tax_reduction_line_81`, read into
  `ca-on/ontario_tax_after_reduction_return`), the tax after the personal credits and the tax
  reduction, before the LIFT credit and the health premium, gives `ca-on/ontario_rate_gate`; the
  Ontario marginal rate (`ca-on/ontario_marginal_rate`) is that gate times the bracket rate with
  the tax reduction phase-out (`ca-on/ontario_bracket_rate_with_reduction`). Not line 88 (after
  the LIFT credit and the farmers' food donation credit) and not line 90 (adds the health
  premium).
- The Ontario tax reduction phase-out: ON428 line 80 "Ontario tax reduction"
  (`ca-on/on428_ontario_tax_reduction_line_80`, read into `ca-on/ontario_tax_reduction_return`)
  gives `ca-on/ontario_reduction_gate` (1 while it is above 0). While lines 80 and 81 are both above
  0, line 81 is 2 x line 73 less 588, so a further dollar of income adds the bracket tax and takes
  the same amount of tax reduction away: `ca-on/ontario_reduction_phase_out_rate` is that gate times
  the bracket rate times the surtax factor (`ca-on/ontario_bracket_marginal_rate`), and
  `ca-on/ontario_bracket_rate_with_reduction` is the bracket product plus it, so the Ontario part
  is double (10.1%) in that band.
- The health premium slope is unchanged: the rate of the ON428 line 89 chart row of the taxable
  income (6% from 20,000 to 25,000, 0 in a flat row).

No new form text is quoted (the printed rates are those pinned in the marginal rate test file;
the thresholds are measured). Thresholds, salary only, 2025: basic federal tax (line 42900) is first
positive at 18,820.27 (at 18,820.26 the tax before credits equals the credits, 2,706.72), ON428
line 81 at 19,868.74 (0.02; 0.00 at 19,868.73) and ON428 line 80 is 0.01 at 26,168.36 and 0.00 from
26,168.37.

Taxable income (T1 line 26000) is the salary less the enhanced CPP deduction, 1% of the salary over
3,500 rounded to the cent (19,835.00 at 20,000): 19,705.04 at 19,868.73 (slope 0), 24,785.00 at
25,000 (6% row), 29,735.00 at 30,000 and 32,030.39 at 32,318.58 (flat 300 row, slope 0) and
25,941.68 at 26,168.36 (flat row). The surtax base is under 5,710 there, so the surtax factor is 1.

Known limit: the rate ignores the LIFT credit phase-out and the effect of CPP and EI on income tax.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine import build_tax_computation
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tests.kinds import bundled_kinds

D = Decimal
ONTARIO = JurisdictionCode("CA-ON")
RETURN = "ca-on/return"

BASIC_FEDERAL_TAX = "ca/federal_tax_after_credits_return"
TAX_AFTER_REDUCTION = "ca-on/ontario_tax_after_reduction_return"
TAX_REDUCTION = "ca-on/ontario_tax_reduction_return"
REDUCTION_GATE = "ca-on/ontario_reduction_gate"
WITH_REDUCTION = "ca-on/ontario_bracket_rate_with_reduction"
FEDERAL_GATE = "ca/federal_rate_gate"
ONTARIO_GATE = "ca-on/ontario_rate_gate"
FEDERAL_BRACKET = "ca/federal_bracket_rate_return"
ONTARIO_BRACKET = "ca-on/ontario_bracket_marginal_rate"
FEDERAL = "ca/federal_marginal_rate"
ONTARIO_RATE = "ca-on/ontario_marginal_rate"
SLOPE = "ca-on/return_health_premium_slope"
MARGINAL = "ca-on/marginal_tax_rate"

# Salary, then the federal marginal rate, the Ontario marginal rate, the health premium slope and
# the marginal tax rate, worked by hand from the printed rates and the gates.
PARTS = [
    # Basic federal tax is 0.00 (and so ON428 line 81): both parts are 0 although the bracket rates
    # are 14.5% and 5.05%.
    ("100", "0", "0", "0", "0"),
    ("18820.26", "0", "0", "0", "0"),
    # Basic federal tax is first positive: the federal part only.
    ("18820.27", "0.145", "0", "0", "0.145"),
    ("19868.73", "0.145", "0", "0", "0.145"),
    # ON428 line 81 is first positive at 19,868.74: the Ontario part, 5.05% times the factor 1.
    # While the Ontario tax reduction (line 80) is also above 0, line 81 falls by twice the line 73
    # bracket tax, so the Ontario part is double: 2 x 5.05% = 10.1%.
    ("19868.74", "0.145", "0.101", "0", "0.246"),
    ("20000", "0.145", "0.101", "0", "0.246"),
    # The health premium slope shows (6% in the 20,000 to 25,000 row, 0 in the flat row).
    ("22000", "0.145", "0.101", "0.06", "0.306"),
    ("25000", "0.145", "0.101", "0.06", "0.306"),
    # Line 80 is 0.01 at 26,168.36 (taxable income 25,941.68, flat row) and 0.00 at 26,168.37: the
    # Ontario part is single again.
    ("26168.36", "0.145", "0.101", "0", "0.246"),
    ("26168.37", "0.145", "0.0505", "0", "0.1955"),
    ("30000", "0.145", "0.0505", "0", "0.1955"),
    ("32318.58", "0.145", "0.0505", "0", "0.1955"),
    # Unchanged by the gates (both taxes are positive).
    ("48800", "0.145", "0.0505", "0.25", "0.4455"),
    ("70000", "0.205", "0.0915", "0", "0.2965"),
    ("120000", "0.26", "0.174096", "0", "0.434096"),
    ("275000", "0.33", "0.205296", "0", "0.535296"),
]


def _summary(salary: str) -> Worksheet:
    # No fixture: the bundled Ontario manifest, as the calculator loads it, salary the only input.
    worksheets = build_tax_computation().compute(
        ONTARIO, 2025, Artifact(EMPLOYMENT_INCOME, D(salary))
    )
    (summary,) = worksheets[RETURN]
    return summary


def _value(summary: Worksheet, name: str) -> Decimal:
    value = summary.get(bundled_kinds().kind(name)).value
    assert isinstance(value, Decimal)
    return value


@pytest.mark.parametrize(("salary", "federal", "ontario", "slope", "marginal"), PARTS)
def test_each_part_and_the_total_of_the_marginal_tax_rate(
    salary: str, federal: str, ontario: str, slope: str, marginal: str
) -> None:
    summary = _summary(salary)

    assert _value(summary, FEDERAL) == D(federal)
    assert _value(summary, ONTARIO_RATE) == D(ontario)
    assert _value(summary, SLOPE) == D(slope)
    assert _value(summary, MARGINAL) == D(marginal)
    assert D(federal) + D(ontario) + D(slope) == D(marginal)


def test_the_marginal_tax_rate_at_a_salary_of_100_is_0_not_19_55_percent() -> None:
    # Tax payable is 0.00 and the next dollar adds no tax; the rate was 0.1955 before the gates.
    summary = _summary("100")

    assert _value(summary, MARGINAL) == D("0")
    assert _value(summary, FEDERAL) == D("0")
    assert _value(summary, ONTARIO_RATE) == D("0")
    assert _value(summary, SLOPE) == D("0")


@pytest.mark.parametrize(
    ("salary", "federal_tax_is_positive", "ontario_tax_is_positive"),
    [
        ("100", False, False),
        ("18820.26", False, False),
        ("18820.27", True, False),
        ("19868.73", True, False),
        ("19868.74", True, True),
        ("20000", True, True),
        ("30000", True, True),
        ("70000", True, True),
    ],
)
def test_the_gates_open_with_the_taxes_they_read(
    salary: str, federal_tax_is_positive: bool, ontario_tax_is_positive: bool
) -> None:
    summary = _summary(salary)

    assert (_value(summary, BASIC_FEDERAL_TAX) > 0) is federal_tax_is_positive
    assert (_value(summary, TAX_AFTER_REDUCTION) > 0) is ontario_tax_is_positive
    assert _value(summary, FEDERAL_GATE) == D(int(federal_tax_is_positive))
    assert _value(summary, ONTARIO_GATE) == D(int(ontario_tax_is_positive))


@pytest.mark.parametrize("salary", ["100", "18820.26", "18820.27", "19868.73", "19868.74"])
def test_the_bracket_rates_read_by_the_gates_are_ungated(salary: str) -> None:
    # The gate changes the part, not the bracket rate it multiplies: 14.5% and 5.05% x 1 at every
    # one of these salaries.
    summary = _summary(salary)

    assert _value(summary, FEDERAL_BRACKET) == D("0.145")
    assert _value(summary, ONTARIO_BRACKET) == D("0.0505")


def test_the_ontario_gate_follows_line_81_and_not_line_88() -> None:
    # At 20,000 ON428 line 81 is positive while line 88 (after the LIFT credit) is 0.00, and the
    # gate follows line 81, so the Ontario part is present.
    summary = _summary("20000")
    kinds = bundled_kinds()
    (on428,) = build_tax_computation().compute(
        ONTARIO, 2025, Artifact(EMPLOYMENT_INCOME, D("20000"))
    )["ca-on/on428"]

    assert on428.get(kinds.kind("ca-on/on428_tax_after_tax_reduction_line_81")).value > 0
    assert on428.get(
        kinds.kind("ca-on/on428_tax_after_farmers_food_donation_credit_line_88")
    ).value == D("0")
    assert _value(summary, TAX_AFTER_REDUCTION) > 0
    assert _value(summary, ONTARIO_GATE) == D("1")


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
    ("salary", "with_reduction"),
    [
        ("19868.74", "0.101"),
        ("25000", "0.101"),
        ("26168.36", "0.101"),
        ("26168.37", "0.0505"),
        ("30000", "0.0505"),
        ("70000", "0.0915"),
    ],
)
def test_the_bracket_rate_with_the_reduction_doubles_while_line_80_is_positive(
    salary: str, with_reduction: str
) -> None:
    summary = _summary(salary)

    assert _value(summary, WITH_REDUCTION) == D(with_reduction)
    assert _value(summary, WITH_REDUCTION) == _value(summary, ONTARIO_BRACKET) * (
        1 + _value(summary, REDUCTION_GATE)
    )
