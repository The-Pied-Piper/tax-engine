"""The Saskatchewan marginal tax rate counts each tax rate only where its own tax is above zero
(2025), through the real engine.

The marginal tax rate is the change in the take-home deductions on the next dollar of salary: the
federal and Saskatchewan tax rates (with the credits on CPP and EI) plus the CPP and EI rates. A
tax rate counts only where its own tax is above zero, through a gate: 0 where the tax is 0.00 and 1
where it is a cent or more.

- Federal: T1 line 42900 "Basic federal tax" (`ca/federal_tax_after_credits`, read into
  `ca/marginal_basic_federal_tax` by the federal form `ca/take_home_marginal_rates`) gives
  `ca/marginal_federal_gate`; the federal marginal rate (`ca-sk/marginal_federal_rate`) is the
  federal rate after the credits times that gate.
- Saskatchewan: SK428 line 67 "Line 62 minus line 66 (if negative, enter "0")" (read into
  `ca-sk/saskatchewan_tax_after_credits_return`) gives `ca-sk/saskatchewan_rate_gate`; the
  Saskatchewan marginal rate (`ca-sk/saskatchewan_marginal_rate`) is the bracket rate (SK428 line
  5) after the credits times that gate. Saskatchewan has no tax reduction, surtax or premium.

The printed rates and the hand-worked figures are in `test_return_marginal_tax_rate_values.py`;
here the thresholds are measured. Thresholds, salary only, 2025: basic federal tax (T1 line 42900)
is first positive at 18,820.27 (0.00 at 18,820.26) and SK428 line 67 at 20,866.58 (0.01; 0.00 at
20,866.57).
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
SASKATCHEWAN = JurisdictionCode("CA-SK")
YEAR = 2025
RETURN = "ca-sk/return"
FEDERAL_FORM = "ca/take_home_marginal_rates"

BASIC_FEDERAL_TAX = "ca/marginal_basic_federal_tax"
FEDERAL_GATE = "ca/marginal_federal_gate"
LINE_67 = "ca-sk/saskatchewan_tax_after_credits_return"
SASKATCHEWAN_GATE = "ca-sk/saskatchewan_rate_gate"
FEDERAL = "ca-sk/marginal_federal_rate"
SASKATCHEWAN_RATE = "ca-sk/saskatchewan_marginal_rate"
CONTRIBUTION = "ca-sk/marginal_contribution_rate"
MARGINAL = "ca-sk/marginal_tax_rate"

# Salary, then the federal marginal rate, the Saskatchewan marginal rate, the contribution rate and
# the marginal tax rate, worked by hand from the printed rates and the gates.
PARTS = [
    # No tax and no contribution: every part is 0 although the bracket rates are 14.5% and 10.5%.
    ("100", "0", "0", "0", "0"),
    # T2204 line 16 rises 1 for 1 between 2,000 and 2,033: the EI rate is 1.
    ("2001", "0", "0", "1", "1"),
    # Contributions only: CPP 4.95% + 1% and EI 1.64%, no basic federal tax yet.
    ("18820.26", "0", "0", "0.0759", "0.0759"),
    # Basic federal tax is first positive: 14.5% x 0.99 - 14.5% x 0.0659 = 0.1339945.
    ("18820.27", "0.1339945", "0", "0.0759", "0.2098945"),
    ("20866.57", "0.1339945", "0", "0.0759", "0.2098945"),
    # SK428 line 67 is first positive: 10.5% x 0.99 - 10.5% x 0.0659 = 0.0970305.
    ("20866.58", "0.1339945", "0.0970305", "0.0759", "0.306925"),
    # Above the EI maximum of 65,700: CPP 4.95% + 1% only.
    ("70000", "0.1957725", "0.1185525", "0.0595", "0.373825"),
    # SK428 line 1 is exactly 152,750.00: still column 2 (12.5%); a cent more of salary is column 3.
    ("153824", "0.26", "0.125", "0", "0.385"),
    ("153824.01", "0.26", "0.145", "0", "0.405"),
]


def _summary(salary: str) -> Worksheet:
    # No fixture: the bundled Saskatchewan manifest, as the calculator loads it, salary the only
    # input.
    worksheets = build_tax_computation().compute(
        TaxCalculationRequest(SASKATCHEWAN, YEAR, (Artifact(EMPLOYMENT_INCOME, D(salary)),))
    )
    (summary,) = worksheets[RETURN]
    return summary


def _federal(salary: str) -> Worksheet:
    # The federal form's sheet, which holds the federal gate.
    worksheets = build_tax_computation().compute(
        TaxCalculationRequest(SASKATCHEWAN, YEAR, (Artifact(EMPLOYMENT_INCOME, D(salary)),))
    )
    (federal,) = worksheets[FEDERAL_FORM]
    return federal


def _value(sheet: Worksheet, name: str) -> Decimal:
    value = sheet.get(bundled_kinds().kind(name)).value
    assert isinstance(value, Decimal)
    return value


@pytest.mark.parametrize(("salary", "federal", "saskatchewan", "contribution", "marginal"), PARTS)
def test_each_part_and_the_total_of_the_marginal_tax_rate(
    salary: str, federal: str, saskatchewan: str, contribution: str, marginal: str
) -> None:
    summary = _summary(salary)

    assert _value(summary, FEDERAL) == D(federal)
    assert _value(summary, SASKATCHEWAN_RATE) == D(saskatchewan)
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
    ("salary", "line_67", "saskatchewan_gate"),
    [
        ("20866.57", "0.00", "0"),
        ("20866.58", "0.01", "1"),
    ],
)
def test_the_saskatchewan_gate_opens_where_line_67_is_first_above_zero(
    salary: str, line_67: str, saskatchewan_gate: str
) -> None:
    summary = _summary(salary)

    assert _value(summary, LINE_67) == D(line_67)
    assert _value(summary, SASKATCHEWAN_GATE) == D(saskatchewan_gate)
