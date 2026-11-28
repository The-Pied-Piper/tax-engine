"""The Manitoba marginal tax rate counts each part only where its own tax or credit is above zero,
through the real engine (2025).

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

The printed rates and the hand-worked figures are in
`test_return_marginal_tax_rate_values.py`; here the thresholds are
measured. Thresholds, salary only, 2025: MB428 line 65 is first positive at 17,403.91 (0.00 a cent
below), T1 line 42900 at 18,820.27, and the family tax benefit (MB428-A line 12) is 0.00 from
23,140.80.

At 100 every part is 0; one cent below the Manitoba threshold the rate is the contribution rate
only; once line 65 is positive the Manitoba part is 10.8% x 0.99 + 9% x 10.8% x 0.99 less the
credit on CPP and EI (0.0659 x 10.8%) while the family tax benefit lasts.
The engine rounds the marginal rate half-up to 0.0001 like the average rate
(`ca/take_home_average_rate_rounding`), so each expected marginal rate in the tests is the exact
figure derived in the comments rounded half-up to four decimals; the parts stay exact.

The fall of the age amount (Worksheet MB428 "Line 58080 - Age amount", MB428 line 10) is a term of
the Manitoba rate for a filer born in 1960 or earlier: 15% x 10.8% x N = 0.0162 x N from a net
income of 27,749.01 to 52,601.99, N = 0.99 in 2025 (a filer born in 1955 is 70 and still pays CPP),
so 0.016038. 27,993.94 and 27,993.95 are a net income of 27,749.00 and 27,749.01; 53,097.97 and
53,097.98 are 52,601.99 and 52,602.00 (the printed "$52,602 or more, enter 0"). Exact Manitoba
terms with the credit on the CPP base and EI (10.8% x 0.0659 = 0.0071172) taken off:
10.8% bracket 0.10692 - 0.0071172 = 0.0998028; 12.75% bracket 0.126225 - 0.0071172 = 0.1191078;
family tax benefit 0.00972 x 0.99 = 0.0096228. The marginal totals are in
`test_return_marginal_tax_rate_values.py`.
"""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal
from typing import Any

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
ROUNDING = D("0.0001")
MANITOBA = JurisdictionCode("CA-MB")
RETURN = "ca-mb/return"
YEAR = 2025

FEDERAL_FORM = "ca/take_home_marginal_rates"
BASIC_FEDERAL_TAX = "ca/marginal_basic_federal_tax"
FEDERAL_GATE = "ca/marginal_federal_gate"
LINE_65 = "ca-mb/manitoba_tax_after_credits_return"
MANITOBA_GATE = "ca-mb/manitoba_rate_gate"
FAMILY_TAX_BENEFIT = "ca-mb/family_tax_benefit_return"
FAMILY_TAX_BENEFIT_GATE = "ca-mb/family_tax_benefit_gate"
FEDERAL = "ca-mb/marginal_federal_rate"
MANITOBA_RATE = "ca-mb/manitoba_marginal_rate"
AGE_RATE = "ca-mb/marginal_manitoba_age_credit_rate"
CONTRIBUTION = "ca-mb/marginal_contribution_rate"
MARGINAL = "ca-mb/marginal_tax_rate"

# Salary, then the federal marginal rate, the Manitoba marginal rate, the contribution rate and the
# marginal tax rate, worked by hand from the printed rates and the gates.
PARTS = [
    ("100", "0", "0", "0", "0"),
    ("17403.90", "0", "0", "0.0759", "0.0759"),
    ("17403.91", "0", "0.1094256", "0.0759", "0.1853"),
    ("18820.26", "0", "0.1094256", "0.0759", "0.1853"),
    ("18820.27", "0.1339945", "0.1094256", "0.0759", "0.3193"),
    ("20000", "0.1339945", "0.1094256", "0.0759", "0.3193"),
    ("23140.79", "0.1339945", "0.1094256", "0.0759", "0.3193"),
    ("23140.80", "0.1339945", "0.0998028", "0.0759", "0.3097"),
    ("70000", "0.1957725", "0.120879", "0.0595", "0.3762"),
]


def _summary(salary: str) -> Worksheet:
    # No fixture: the bundled Manitoba manifest, as the calculator loads it, salary the only input.
    worksheets = build_tax_computation().compute(
        TaxCalculationRequest(MANITOBA, YEAR, (Artifact(EMPLOYMENT_INCOME, D(salary)),))
    )
    (summary,) = worksheets[RETURN]
    return summary


def _federal(salary: str) -> Worksheet:
    # The federal form's sheet, which holds the federal gate.
    worksheets = build_tax_computation().compute(
        TaxCalculationRequest(MANITOBA, YEAR, (Artifact(EMPLOYMENT_INCOME, D(salary)),))
    )
    (federal,) = worksheets[FEDERAL_FORM]
    return federal


def _value(sheet: Worksheet, name: str) -> Decimal:
    value = sheet.get(bundled_kinds().kind(name)).value
    assert isinstance(value, Decimal)
    return value


@pytest.mark.parametrize(("salary", "federal", "manitoba", "contribution", "marginal"), PARTS)
def test_each_part_and_the_total_of_the_marginal_tax_rate(
    salary: str, federal: str, manitoba: str, contribution: str, marginal: str
) -> None:
    summary = _summary(salary)

    assert _value(summary, FEDERAL) == D(federal)
    assert _value(summary, MANITOBA_RATE) == D(manitoba)
    assert _value(summary, CONTRIBUTION) == D(contribution)
    assert _value(summary, MARGINAL) == D(marginal)
    assert (D(federal) + D(manitoba) + D(contribution)).quantize(
        ROUNDING, rounding=ROUND_HALF_UP
    ) == D(marginal)


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
    ("salary", "line_65", "manitoba_gate"),
    [
        ("17403.90", "0.00", "0"),
        ("17403.91", "0.01", "1"),
    ],
)
def test_the_manitoba_gate_opens_where_line_65_is_first_above_zero(
    salary: str, line_65: str, manitoba_gate: str
) -> None:
    summary = _summary(salary)

    assert _value(summary, LINE_65) == D(line_65)
    assert _value(summary, MANITOBA_GATE) == D(manitoba_gate)


@pytest.mark.parametrize(
    ("salary", "benefit_is_positive"),
    [("20000", True), ("23140.79", True), ("23140.80", False), ("30000", False), ("70000", False)],
)
def test_the_family_tax_benefit_gate_follows_schedule_mb428_a_line_12(
    salary: str, benefit_is_positive: bool
) -> None:
    summary = _summary(salary)

    assert (_value(summary, FAMILY_TAX_BENEFIT) > 0) is benefit_is_positive
    assert _value(summary, FAMILY_TAX_BENEFIT_GATE) == D(int(benefit_is_positive))


# Born 1955: salary, age term, Manitoba marginal rate. 27,993.94 is a net income of exactly
# the threshold (line 4 is 0.00, no effect); the family tax benefit's fall is still counted.
BORN_1955 = [
    ("0", "0", "0"),
    ("27993.94", "0", "0.1094256"),
    ("27993.95", "0.016038", "0.1254636"),
    ("40000", "0.016038", "0.1254636"),
    ("46000", "0.016038", "0.1254636"),
    ("50000", "0.016038", "0.1351458"),
    ("53097.97", "0.016038", "0.1351458"),
    ("53097.98", "0", "0.1191078"),
    ("60000", "0", "0.1191078"),
]
# Born 1980 or no year of birth: no age amount, so no age term at any salary.
UNDER_65 = [
    ("0", "0", "0"),
    ("27993.94", "0", "0.0998028"),
    ("27993.95", "0", "0.0998028"),
    ("40000", "0", "0.0998028"),
    ("50000", "0", "0.1191078"),
    ("53097.97", "0", "0.1191078"),
    ("53097.98", "0", "0.1191078"),
    ("60000", "0", "0.1191078"),
]
AGE_CASES = [(born, *row) for born in (1955,) for row in BORN_1955] + [
    (born, *row) for born in (1980, None) for row in UNDER_65
]


def _aged_summary(salary: str, born: int | None) -> Worksheet:
    given: list[Artifact[Any]] = [Artifact(EMPLOYMENT_INCOME, D(salary))]
    if born is not None:
        given.append(Artifact(BIRTH_YEAR, born))
    worksheets = build_tax_computation().compute(
        TaxCalculationRequest(MANITOBA, YEAR, tuple(given))
    )
    (summary,) = worksheets[RETURN]
    return summary


@pytest.mark.parametrize(("born", "salary", "age", "manitoba"), AGE_CASES)
def test_the_age_term_and_the_manitoba_marginal_rate(
    born: int | None, salary: str, age: str, manitoba: str
) -> None:
    summary = _aged_summary(salary, born)

    assert _value(summary, AGE_RATE) == D(age)
    assert _value(summary, MANITOBA_RATE) == D(manitoba)


def test_the_age_term_is_the_printed_rate_times_the_credit_rate_times_the_net_income_rate() -> None:
    # 15% x 10.8% x 0.99, exact, the credit rate not rounded to the cent.
    assert _value(_aged_summary("40000", 1955), AGE_RATE) == D("0.15") * D("0.108") * D("0.99")
