"""The Manitoba marginal tax rate counts each part only where its own tax or credit is above zero,
through the real engine (2026).

The marginal tax rate is the change in the take-home deductions on the next dollar of salary: the
federal tax rate (after the credits on CPP and EI, from the federal form
`ca/take_home_marginal_rates`), the Manitoba tax rate and the CPP and EI rates. A part counts only
where its own tax is above zero, through a gate (`ca-mb/marginal_rate_gate`): 0 where the tax is
0.00 and 1 where it is a cent or more.

- Federal: T1 line 42900 "Basic federal tax" (`ca/marginal_basic_federal_tax`) gives
  `ca/marginal_federal_gate`; the federal marginal rate is the rate after the credits times it.
- Manitoba: MB428 line 65 "Line 60 minus line 64 (if negative, enter "0")" (`ca-mb/manitoba_tax_
  after_credits_return`) gives `ca-mb/manitoba_rate_gate`; the Manitoba marginal rate is the
  bracket rate with the falls of the basic personal amount and of the family tax benefit, less the
  credit on CPP and EI, times it.
- The family tax benefit (Schedule MB428-A line 12, read into `ca-mb/family_tax_benefit_return`)
  gives `ca-mb/family_tax_benefit_gate`: while it is above 0 a further dollar of net income takes
  away 9% of a dollar of it, at the 10.8% credit rate, 0.972 points before the net income rate.

The printed rates and the hand-worked figures are in `test_return_rates_2026.py`; here the
thresholds are measured. Thresholds, salary only, 2026: MB428 line 65 is first positive at
17,402.22 (0.00 a cent below), T1 line 42900 at 19,200.18, and the family tax benefit (MB428-A
line 12) is 0.00 from 23,140.80.

At 100 every part is 0; one cent below the Manitoba threshold the rate is the contribution rate
only; once line 65 is positive the Manitoba part is 10.8% x 0.99 + 9% x 10.8% x 0.99 less the
credit on CPP and EI (0.0658 x 10.8%) while the family tax benefit lasts.
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
MANITOBA = JurisdictionCode("CA-MB")
RETURN = "ca-mb/return"
YEAR = 2026

FEDERAL_FORM = "ca/take_home_marginal_rates"
BASIC_FEDERAL_TAX = "ca/marginal_basic_federal_tax"
FEDERAL_GATE = "ca/marginal_federal_gate"
LINE_65 = "ca-mb/manitoba_tax_after_credits_return"
MANITOBA_GATE = "ca-mb/manitoba_rate_gate"
FAMILY_TAX_BENEFIT = "ca-mb/family_tax_benefit_return"
FAMILY_TAX_BENEFIT_GATE = "ca-mb/family_tax_benefit_gate"
FEDERAL = "ca-mb/marginal_federal_rate"
MANITOBA_RATE = "ca-mb/manitoba_marginal_rate"
CONTRIBUTION = "ca-mb/marginal_contribution_rate"
MARGINAL = "ca-mb/marginal_tax_rate"

# Salary, then the federal marginal rate, the Manitoba marginal rate, the contribution rate and the
# marginal tax rate, worked by hand from the printed rates and the gates.
PARTS = [
    ("100", "0", "0", "0", "0"),
    ("17402.21", "0", "0", "0.0758", "0.0758"),
    ("17402.22", "0", "0.1094364", "0.0758", "0.1852364"),
    ("19200.17", "0", "0.1094364", "0.0758", "0.1852364"),
    ("19200.18", "0.129388", "0.1094364", "0.0758", "0.3146244"),
    ("20000", "0.129388", "0.1094364", "0.0758", "0.3146244"),
    ("23140.79", "0.129388", "0.1094364", "0.0758", "0.3146244"),
    ("23140.80", "0.129388", "0.0998136", "0.0758", "0.3050016"),
    ("70000", "0.19602", "0.120879", "0.0595", "0.376399"),
]


def _compute(salary: str) -> dict[str, tuple[Worksheet, ...]]:
    # No fixture: the bundled Manitoba manifest, as the calculator loads it, salary the only input.
    return build_tax_computation().compute(
        TaxCalculationRequest(MANITOBA, YEAR, (Artifact(EMPLOYMENT_INCOME, D(salary)),))
    )


def _value(sheet: Worksheet, name: str) -> Decimal:
    value = sheet.get(bundled_kinds().kind(name)).value
    assert isinstance(value, Decimal)
    return value


@pytest.mark.parametrize(("salary", "federal", "manitoba", "contribution", "marginal"), PARTS)
def test_each_part_and_the_total_of_the_marginal_tax_rate(
    salary: str, federal: str, manitoba: str, contribution: str, marginal: str
) -> None:
    (summary,) = _compute(salary)[RETURN]

    assert _value(summary, FEDERAL) == D(federal)
    assert _value(summary, MANITOBA_RATE) == D(manitoba)
    assert _value(summary, CONTRIBUTION) == D(contribution)
    assert _value(summary, MARGINAL) == D(marginal)
    assert D(federal) + D(manitoba) + D(contribution) == D(marginal)


@pytest.mark.parametrize(
    ("salary", "federal_tax_is_positive", "manitoba_tax_is_positive"),
    [
        ("100", False, False),
        ("17402.21", False, False),
        ("17402.22", False, True),
        ("19200.17", False, True),
        ("19200.18", True, True),
        ("70000", True, True),
    ],
)
def test_the_gates_open_with_the_taxes_they_read(
    salary: str, federal_tax_is_positive: bool, manitoba_tax_is_positive: bool
) -> None:
    worksheets = _compute(salary)
    (summary,) = worksheets[RETURN]
    (federal,) = worksheets[FEDERAL_FORM]

    assert (_value(federal, BASIC_FEDERAL_TAX) > 0) is federal_tax_is_positive
    assert (_value(summary, LINE_65) > 0) is manitoba_tax_is_positive
    assert _value(federal, FEDERAL_GATE) == D(int(federal_tax_is_positive))
    assert _value(summary, MANITOBA_GATE) == D(int(manitoba_tax_is_positive))


@pytest.mark.parametrize(
    ("salary", "benefit_is_positive"),
    [("20000", True), ("23140.79", True), ("23140.80", False), ("30000", False), ("70000", False)],
)
def test_the_family_tax_benefit_gate_follows_schedule_mb428_a_line_12(
    salary: str, benefit_is_positive: bool
) -> None:
    (summary,) = _compute(salary)[RETURN]

    assert (_value(summary, FAMILY_TAX_BENEFIT) > 0) is benefit_is_positive
    assert _value(summary, FAMILY_TAX_BENEFIT_GATE) == D(int(benefit_is_positive))
