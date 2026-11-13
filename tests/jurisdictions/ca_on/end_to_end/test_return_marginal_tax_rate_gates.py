"""The marginal tax rate counts each bracket-rate part only where its own tax is above zero (#820),
through the real engine.

The marginal tax rate is the income tax on the next dollar, including the Ontario surtax and health
premium; CPP and EI are not counted. Before the fix every part read the bracket rate of the taxable
income row, so the rate was 19.55% at a salary of 100 and at every salary below 18,820.27. Each
part now reads a gate: 0 where its tax is 0.00 and 1 where it is a cent or more.

- Federal: T1 line 42000 "Net federal tax" (`ca/net_federal_tax`, read into
  `ca/net_federal_tax_return`) gives `ca/federal_rate_gate`; the federal marginal rate
  (`ca/federal_marginal_rate`) is that gate times the T1 line 73 "Line 73: Rate"
  (`ca/federal_bracket_rate_return`).
- Ontario: ON428 line 88 "Ontario tax after the farmers' food donation credit"
  (`ca-on/on428_tax_after_farmers_food_donation_credit_line_88`, read into
  `ca-on/ontario_tax_before_premium_return`), the Ontario tax before the health premium, gives
  `ca-on/ontario_rate_gate`; the Ontario marginal rate (`ca-on/ontario_marginal_rate`) is that gate
  times the bracket rate times the surtax factor (`ca-on/ontario_bracket_marginal_rate`). Not line
  90: line 90 adds the health premium (line 89), so it is positive from 20,166.76 while the Ontario
  tax reduction (line 80) and the LIFT credit (line 85) still cancel the bracket tax.
- The health premium slope is unchanged: the rate of the ON428 line 89 chart row of the taxable
  income (6% from 20,000 to 25,000, 0 in a flat row).

No new form text is quoted (the printed rates are those pinned in the marginal rate test file;
the thresholds are measured). Thresholds, salary only, 2025: net federal tax is first positive at
18,820.27 (at 18,820.26 the tax before credits equals the credits, 2,706.72) and
ON428 line 88 at 32,318.59.

Taxable income (T1 line 26000) is the salary less the enhanced CPP deduction, 1% of the salary over
3,500 rounded to the cent (19,835.00 at 20,000): 24,785.00 at 25,000 (6% row), 29,735.00 at 30,000
(flat 300 row) and 32,030.39 / 32,030.40 at 32,318.58 / 32,318.59 (flat 300 row, slope 0). The
surtax base is under 5,710 there, so the surtax factor is 1.

Known limit: the rate stays the bracket rate, so it ignores the phase-out slopes of the Ontario tax
reduction and the LIFT credit and the effect of CPP and EI on income tax.
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

NET_FEDERAL_TAX = "ca/net_federal_tax_return"
TAX_BEFORE_PREMIUM = "ca-on/ontario_tax_before_premium_return"
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
    # Net federal tax is 0.00 (and so ON428 line 88): both parts are 0 although the bracket rates
    # are 14.5% and 5.05%.
    ("100", "0", "0", "0", "0"),
    ("18820.26", "0", "0", "0", "0"),
    # Net federal tax is first positive: the federal part only, taxable income under 20,000.
    ("18820.27", "0.145", "0", "0", "0.145"),
    ("20000", "0.145", "0", "0", "0.145"),
    # The band where ON428 line 90 is positive from the premium alone but line 88 is 0.00: the
    # slope shows (6% in the 20,000 to 25,000 row, 0 in the flat row), the Ontario part does not.
    ("22000", "0.145", "0", "0.06", "0.205"),
    ("25000", "0.145", "0", "0.06", "0.205"),
    ("30000", "0.145", "0", "0", "0.145"),
    # ON428 line 88 is first positive at 32,318.59: the Ontario part, 5.05% times the factor 1.
    ("32318.58", "0.145", "0", "0", "0.145"),
    ("32318.59", "0.145", "0.0505", "0", "0.1955"),
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
    # Tax payable is 0.00 and the next dollar adds no tax; the rate was 0.1955 before #820.
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
        ("20000", True, False),
        ("30000", True, False),
        ("32318.58", True, False),
        ("32318.59", True, True),
        ("70000", True, True),
    ],
)
def test_the_gates_open_with_the_taxes_they_read(
    salary: str, federal_tax_is_positive: bool, ontario_tax_is_positive: bool
) -> None:
    summary = _summary(salary)

    assert (_value(summary, NET_FEDERAL_TAX) > 0) is federal_tax_is_positive
    assert (_value(summary, TAX_BEFORE_PREMIUM) > 0) is ontario_tax_is_positive
    assert _value(summary, FEDERAL_GATE) == D(int(federal_tax_is_positive))
    assert _value(summary, ONTARIO_GATE) == D(int(ontario_tax_is_positive))


@pytest.mark.parametrize("salary", ["100", "18820.26", "18820.27", "32318.58", "32318.59"])
def test_the_bracket_rates_read_by_the_gates_are_ungated(salary: str) -> None:
    # The gate changes the part, not the bracket rate it multiplies: 14.5% and 5.05% x 1 at every
    # one of these salaries.
    summary = _summary(salary)

    assert _value(summary, FEDERAL_BRACKET) == D("0.145")
    assert _value(summary, ONTARIO_BRACKET) == D("0.0505")


def test_the_tax_before_the_premium_is_line_88_and_not_line_90() -> None:
    # At 25,000 ON428 line 90 is positive (the health premium, 300.00 less the cancelled bracket
    # tax) while line 88 is 0.00, and the gate follows line 88.
    summary = _summary("25000")
    kinds = bundled_kinds()
    (on428,) = build_tax_computation().compute(
        ONTARIO, 2025, Artifact(EMPLOYMENT_INCOME, D("25000"))
    )["ca-on/on428"]

    assert on428.get(kinds.kind("ca-on/on428_ontario_tax_line_90")).value > 0
    assert _value(summary, TAX_BEFORE_PREMIUM) == D("0")
    assert _value(summary, ONTARIO_GATE) == D("0")
