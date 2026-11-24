"""The Alberta marginal tax rate counts each tax rate only where its own tax is above zero
(2025), through the real engine.

The marginal tax rate is the change in the take-home deductions on the next dollar of salary: the
federal and Alberta tax rates (with the credits on CPP and EI) plus the CPP and EI rates. A
tax rate counts only where its own tax is above zero, through a gate: 0 where the tax is 0.00 and 1
where it is a cent or more.

- Federal: T1 line 42900 "Basic federal tax" (`ca/federal_tax_after_credits`, read into
  `ca/marginal_basic_federal_tax` by the federal form `ca/take_home_marginal_rates`) gives
  `ca/marginal_federal_gate`; the federal marginal rate (`ca-ab/marginal_federal_rate`) is the
  federal rate after the credits times that gate.
- Alberta: AB428 line 68 "Line 66 plus line 67" (read into `ca-ab/alberta_tax_after_credits_return`)
  gives `ca-ab/alberta_rate_gate`; the Alberta marginal rate (`ca-ab/alberta_marginal_rate`) is the
  bracket rate (AB428 line 5 or line 12) after the credits times that gate. Alberta has no tax
  reduction, surtax or premium.

The printed rates and the hand-worked figures are in `test_return_marginal_tax_rate_values.py`;
here the thresholds are measured.
The engine rounds the marginal rate half-up to 0.0001 like the average rate
(`ca/take_home_average_rate_rounding`), so each expected marginal rate in the tests is the exact
figure derived in the comments rounded half-up to four decimals; the parts stay exact.
Thresholds, salary only, 2025: basic federal tax (T1 line 42900) is first positive at 18,820.27
(0.00 at 18,820.26) and AB428 line 68 at 23,931.13 (0.01; 0.00 at 23,931.12). Line 68 is not
monotone just under its boundary because of cent rounding: it is 0.01 from 23,931.13 to 23,931.21,
0.00 from 23,931.22 to 23,931.24 and 0.01 from 23,931.25 on.
"""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

import pytest

from tax_engine import build_tax_computation
from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tests.kinds import bundled_kinds

D = Decimal
ALBERTA = JurisdictionCode("CA-AB")
YEAR = 2025
RETURN = "ca-ab/return"
FEDERAL_FORM = "ca/take_home_marginal_rates"

BASIC_FEDERAL_TAX = "ca/marginal_basic_federal_tax"
FEDERAL_GATE = "ca/marginal_federal_gate"
LINE_68 = "ca-ab/alberta_tax_after_credits_return"
ALBERTA_GATE = "ca-ab/alberta_rate_gate"
FEDERAL = "ca-ab/marginal_federal_rate"
ALBERTA_RATE = "ca-ab/alberta_marginal_rate"
CONTRIBUTION = "ca-ab/marginal_contribution_rate"
MARGINAL = "ca-ab/marginal_tax_rate"

# Salary, then the federal marginal rate, the Alberta marginal rate, the contribution rate and
# the marginal tax rate, worked by hand from the printed rates and the gates.
PARTS = [
    # No tax and no contribution: every part is 0 although the bracket rates are 14.5% and 8%.
    ("100", "0", "0", "0", "0"),
    # T2204 line 16 rises 1 for 1 between 2,000 and 2,033: the EI rate is 1.
    ("2001", "0", "0", "1", "1"),
    # Contributions only: CPP 4.95% + 1% and EI 1.64%, no basic federal tax yet.
    ("18820.26", "0", "0", "0.0759", "0.0759"),
    # Basic federal tax is first positive: 14.5% x 0.99 - 14.5% x 0.0659 = 0.1339945.
    ("18820.27", "0.1339945", "0", "0.0759", "0.2099"),
    ("23931.12", "0.1339945", "0", "0.0759", "0.2099"),
    # AB428 line 68 is first positive: 8% x 0.99 - 8% x 0.0659 = 0.073928.
    ("23931.13", "0.1339945", "0.073928", "0.0759", "0.2838"),
    # Line 68 is 0.00 again for three cents (cent rounding), then positive from 23,931.25.
    ("23931.22", "0.1339945", "0", "0.0759", "0.2099"),
    ("23931.25", "0.1339945", "0.073928", "0.0759", "0.2838"),
    # Above the EI maximum: CPP 4.95% + 1% only.
    ("70000", "0.1957725", "0.09504", "0.0595", "0.3503"),
    # AB428 line 12 (table 2, taxable income over 181,481): 13%, with no contributions.
    ("200000", "0.2930542655", "0.13", "0", "0.4231"),
]


def _summary(salary: str) -> Worksheet:
    # No fixture: the bundled Alberta manifest, as the calculator loads it, salary the only
    # input.
    worksheets = build_tax_computation().compute(
        TaxCalculationRequest(ALBERTA, YEAR, (Artifact(EMPLOYMENT_INCOME, D(salary)),))
    )
    (summary,) = worksheets[RETURN]
    return summary


def _federal(salary: str) -> Worksheet:
    # The federal form's sheet, which holds the federal gate.
    worksheets = build_tax_computation().compute(
        TaxCalculationRequest(ALBERTA, YEAR, (Artifact(EMPLOYMENT_INCOME, D(salary)),))
    )
    (federal,) = worksheets[FEDERAL_FORM]
    return federal


def _value(sheet: Worksheet, name: str) -> Decimal:
    value = sheet.get(bundled_kinds().kind(name)).value
    assert isinstance(value, Decimal)
    return value


@pytest.mark.parametrize(("salary", "federal", "alberta", "contribution", "marginal"), PARTS)
def test_each_part_and_the_total_of_the_marginal_tax_rate(
    salary: str, federal: str, alberta: str, contribution: str, marginal: str
) -> None:
    summary = _summary(salary)

    assert _value(summary, FEDERAL) == D(federal)
    assert _value(summary, ALBERTA_RATE) == D(alberta)
    assert _value(summary, CONTRIBUTION) == D(contribution)
    assert _value(summary, MARGINAL) == D(marginal)
    assert D(marginal) == (D(federal) + D(alberta) + D(contribution)).quantize(
        D("0.0001"), rounding=ROUND_HALF_UP
    )


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
    ("salary", "line_68", "alberta_gate"),
    [
        ("23931.12", "0.00", "0"),
        ("23931.13", "0.01", "1"),
    ],
)
def test_the_alberta_gate_opens_where_line_68_is_first_above_zero(
    salary: str, line_68: str, alberta_gate: str
) -> None:
    summary = _summary(salary)

    assert _value(summary, LINE_68) == D(line_68)
    assert _value(summary, ALBERTA_GATE) == D(alberta_gate)
