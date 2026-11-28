"""The Saskatchewan marginal rate at a few salaries, worked by hand from the printed rates.

The marginal rate (`ca-sk/marginal_tax_rate`) is the extra take-home deductions on a further dollar
of salary, for a salary-only filer with no paid credits. Each figure below is the exact sum of its
parts, and the parts are the printed rates (T1 "Line 73: Rate", SK428 "Line 5: Rate" and "Line 52:
Saskatchewan non-refundable tax credit rate 10.5%", Schedule 8 lines 11, 12 and 22, T2204 lines 10
and 16), with the net income rate N = 1 - enhanced CPP rate - CPP2 rate, because T1 line 22215
takes the enhanced and the second additional contributions off the income, and the credits at the
federal and the Saskatchewan credit rate on the CPP base and EI rates:

    federal       = bracket rate x N + BPA phase-down - federal credit rate x (CPP base + EI)
    Saskatchewan  = bracket rate x N - 10.5% x (CPP base + EI), counted where SK428 line 67 is
                    above 0 (Saskatchewan has no tax reduction, surtax or health premium)
    marginal      = federal + Saskatchewan + CPP base + CPP enhanced + CPP2 + EI

The extra-run check over a sweep is in `test_return_marginal_tax_rate_extra_run.py`.

- 2025, $100: nothing moves (under the CPP exemption and the EI $2,000): 0.
- 2025, $2,020: only the EI of T2204 line 16 moves, 1 for 1 between $2,000 and $2,033: 1.
- $2,000 and $3,500, both years (exact band edges): the rate at $2,000 is the lower band's (the EI
  rate is 0), but a contribution band reads its own rate from its lower bound, so at exactly
  $3,500 the CPP applies: CPP 4.95% + 1% and EI, 0.0759 in 2025 and 0.0758 in 2026, as at the
  next cent.
- 2025, $10,000: CPP 4.95% + 1% and EI 1.64% = 0.0759; no income tax.
- 2025, $20,000: federal 14.5% x 0.99 - 14.5% x 0.0659 = 0.1339945; Saskatchewan line 67 is 0.00
  (the credits are over the tax), so 0; contributions 0.0759: 0.2098945. At $20,866.58 line 67 is
  first 0.01, and the Saskatchewan part 10.5% x 0.99 - 10.5% x 0.0659 = 0.0970305 counts.
- 2025, $50,000: federal 0.1339945; Saskatchewan 0.0970305; contributions 0.0759: 0.306925.
- 2025, $70,000 (over the EI maximum of $65,700): federal 20.5% x 0.99 - 14.5% x 0.0495 =
  0.1957725; Saskatchewan 12.5% x 0.99 - 10.5% x 0.0495 = 0.1185525; contributions 0.0495 + 0.01:
  0.373825.
- 2025, $75,000 (CPP2 band, no CPP base or EI): N = 0.96; federal 20.5% x 0.96 = 0.1968;
  Saskatchewan 12.5% x 0.96 = 0.12; contributions 0.04: 0.3568.
- 2025, $120,000: no contributions; federal 26%, Saskatchewan 12.5%: 0.385.
- 2025, $200,000: the federal basic personal amount falls over $177,882 to $253,414 (T1 line 77,
  Federal Worksheet lines 2, 6 and 8): 29% + 14.5% x 1,591 / 75,532 (0.0210639 to seven places)
  = 0.2930542655; Saskatchewan 14.5%: 0.4380542655.
- 2026, $21,827.32: Saskatchewan 10.5% x 0.99 - 10.5% x 0.0658 = 0.097041 (EI is 1.63%).
- 2026, $10,000: CPP 4.95% + 1% and EI 1.63%: 0.0758.
- 2026, $70,000 (over the EI maximum of $68,900): federal 20.5% x 0.99 - 14% x 0.0495 = 0.19602;
  Saskatchewan 0.1185525; contributions 0.0595: 0.3740725.
- 2026, $200,000: 29% + 14% x 1,623 / 77,042 (0.0210664 to seven places) = 0.292949296;
  Saskatchewan 14.5%: 0.437949296.

The engine rounds the marginal rate half-up to 0.0001 like the average rate
(`ca/take_home_average_rate_rounding`), so the expected values in the parametrization are the exact
sums derived below rounded half-up to four places (e.g. 0.2098945 is 0.2099).

The age amount falling, for a filer born in 1960 or earlier (the gates are in
`test_return_marginal_tax_rate_gates.py` and `..._gates_2026.py`, the extra run in
`test_return_marginal_tax_rate_extra_run.py`):

Worksheet SK428 (5008-D) "Line 58080 - Age amount": line 3 is the income threshold, line 4 the net
income over it, line 5 the applicable rate 15% (`ca-sk/age_rate`, Saskatchewan's own printed rate),
and line 7 the maximum less 15% of line 4, not below 0. Each dollar of that fall is Saskatchewan
tax at the credit rate of SK428 line 52, 10.5%, so while the net income is over the threshold and
an age amount is still claimed, a further dollar of salary adds 15% x 10.5% x the net income rate
= 0.01575 (a filer of 65 or older pays no CPP, so the net income rate is 1) to the Saskatchewan
rate, and 15% x the federal credit rate (14.5% in 2025, 14% in 2026) = 0.02175 (0.021) to the
federal rate where the net income is over the federal threshold (45,522, 46,432).

Figures (net income is the salary for an aged filer, born 1950 in 2025 and 1955 in 2026: no CPP,
so no enhanced CPP deduction):

- 2025: threshold 43,066, maximum 5,785; the amount is 5,784.90 at a net income of 81,632
  (15% x 38,566 = 5,784.90, so 0.10 is left) and 0 from 81,633 (15% x 38,567 = 5,785.05).
- 2026: threshold 43,927, maximum 5,901; 5,900.85 at 83,266 (15% x 39,339, 0.15 left) and 0 from
  83,267 (15% x 39,340 = 5,901.00 exactly).

For the aged filer the contribution rate is the EI rate only (1.64% in 2025, 1.63% in
2026, under the maximum insurable earnings of 65,700 and 68,900), credited at 10.5% and the
federal rate:

    Saskatchewan = bracket rate - 10.5% x EI [+ 0.01575 while the age amount falls]
    federal      = bracket rate - federal credit rate x EI [+ the federal fall]
    marginal     = federal + Saskatchewan + EI, rounded half-up to 0.0001

2025 (EI 0.0164; 10.5% x EI = 0.001722; 14.5% x EI = 0.002378):
- 43,066: line 4 is 0, so no fall: Saskatchewan 0.105 - 0.001722 = 0.103278; federal 0.145 -
  0.002378 = 0.142622; marginal 0.2623.
- 43,067: Saskatchewan 0.103278 + 0.01575 = 0.119028; federal as above; marginal 0.27805, 0.2781.
- 60,000: Saskatchewan 0.125 - 0.001722 + 0.01575 = 0.139028; federal 0.205 - 0.002378 + 0.02175 =
  0.224372; marginal 0.3798.
- 81,632 (over the EI maximum, EI 0): Saskatchewan 0.125 + 0.01575 = 0.14075; federal 0.205 +
  0.02175 = 0.22675; marginal 0.3675. At 81,633 the amount is 0: 0.125; 0.22675; 0.35175, 0.3518.

2026 (EI 0.0163; 10.5% x EI = 0.0017115; 14% x EI = 0.002282):
- 43,927: Saskatchewan 0.1032885; federal 0.14 - 0.002282 = 0.137718; marginal 0.2573065, 0.2573.
- 43,928: Saskatchewan 0.1190385; marginal 0.2730565, 0.2731.
- 60,000: Saskatchewan 0.125 - 0.0017115 + 0.01575 = 0.1390385; federal 0.205 - 0.002282 + 0.021 =
  0.223718; marginal 0.3790565, 0.3791.
- 83,266 (EI 0): Saskatchewan 0.14075; federal 0.226; marginal 0.36675, 0.3668. At 83,267: 0.125;
  0.226; 0.351.

A filer born in 1980 (under 65) or with no year of birth claims no age amount, so the fall is 0:
2025, 43,067: Saskatchewan 0.105 x 0.99 - 10.5% x 0.0659 = 0.0970305 (net income rate 0.99, CPP
base 4.95% + enhanced 1% + EI 1.64%), marginal 0.1339945 + 0.0970305 + 0.0759 = 0.306925, 0.3069;
2025, 60,000: Saskatchewan 0.125 x 0.99 - 10.5% x 0.0659 = 0.1168305, federal 0.205 x 0.99 -
14.5% x 0.0659 = 0.1933945, marginal 0.386125, 0.3861; 2026, 60,000: Saskatchewan 0.12375 -
10.5% x 0.0658 = 0.116841, federal 0.20295 - 14% x 0.0658 = 0.193738, marginal 0.386379, 0.3864.
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
SASKATCHEWAN = JurisdictionCode("CA-SK")
RETURN = "ca-sk/return"
AGE_CREDIT_RATE = "ca-sk/marginal_saskatchewan_age_credit_rate"
AMOUNT_GATE = "ca-sk/marginal_age_amount_gate"
SASKATCHEWAN_RATE = "ca-sk/saskatchewan_marginal_rate"
MARGINAL = "ca-sk/marginal_tax_rate"
# The year of birth of the aged filer. Born in 1955 a filer turns 70 during 2025, a year that still
# has CPP months (and so the enhanced CPP deduction from the net income), so 2025 uses 1950 (no CPP
# months), the net income there being the salary; 2026 uses 1955.
AGED = {2025: 1950, 2026: 1955}


@pytest.mark.parametrize(
    ("year", "salary", "rate"),
    [
        (2025, "100", "0"),
        (2025, "2020", "1"),
        (2025, "2000", "1"),
        (2025, "2000.01", "1"),
        (2025, "3500", "0.0759"),
        (2025, "3500.01", "0.0759"),
        (2025, "10000", "0.0759"),
        (2025, "20000", "0.2099"),
        (2025, "20866.57", "0.2099"),
        (2025, "20866.58", "0.3069"),
        (2025, "50000", "0.3069"),
        (2025, "70000", "0.3738"),
        (2025, "75000", "0.3568"),
        (2025, "120000", "0.385"),
        (2025, "200000", "0.4381"),
        (2026, "2000", "1"),
        (2026, "2000.01", "1"),
        (2026, "3500", "0.0758"),
        (2026, "3500.01", "0.0758"),
        (2026, "10000", "0.0758"),
        (2026, "70000", "0.3741"),
        (2026, "200000", "0.4379"),
    ],
)
def test_the_marginal_rate_is_the_sum_of_the_rates_that_apply_rounded_to_four_decimals(
    year: int, salary: str, rate: str
) -> None:
    worksheets = build_tax_computation().compute(
        TaxCalculationRequest(SASKATCHEWAN, year, (Artifact(EMPLOYMENT_INCOME, D(salary)),))
    )
    (summary,) = worksheets["ca-sk/return"]

    assert summary.get(bundled_kinds().kind("ca-sk/marginal_tax_rate")).value == D(rate)


def _summary(year: int, birth_year: int | None, salary: str) -> Worksheet:
    salary_input: tuple[Artifact[Decimal], ...] = (Artifact(EMPLOYMENT_INCOME, D(salary)),)
    year_input: tuple[Artifact[int], ...] = (
        () if birth_year is None else (Artifact(BIRTH_YEAR, birth_year),)
    )
    worksheets = build_tax_computation().compute(
        TaxCalculationRequest(SASKATCHEWAN, year, (*salary_input, *year_input))
    )
    (summary,) = worksheets[RETURN]
    return summary


def _value(sheet: Worksheet, name: str) -> Decimal:
    value = sheet.get(bundled_kinds().kind(name)).value
    assert isinstance(value, Decimal)
    return value


# (tax year, salary, Saskatchewan age credit rate, Saskatchewan rate, marginal rate): born 1955.
BORN_1955 = [
    (2025, "0", "0", "0", "0"),
    (2025, "43066", "0", "0.103278", "0.2623"),
    (2025, "43067", "0.01575", "0.119028", "0.2781"),
    (2025, "60000", "0.01575", "0.139028", "0.3798"),
    (2025, "81632", "0.01575", "0.14075", "0.3675"),
    (2025, "81633", "0", "0.125", "0.3518"),
    (2026, "0", "0", "0", "0"),
    (2026, "43927", "0", "0.1032885", "0.2573"),
    (2026, "43928", "0.01575", "0.1190385", "0.2731"),
    (2026, "60000", "0.01575", "0.1390385", "0.3791"),
    (2026, "83266", "0.01575", "0.14075", "0.3668"),
    (2026, "83267", "0", "0.125", "0.351"),
]


@pytest.mark.parametrize(("year", "salary", "age_credit", "saskatchewan", "marginal"), BORN_1955)
def test_born_1955_the_age_amount_fall_is_tax_at_the_credit_rate(
    year: int, salary: str, age_credit: str, saskatchewan: str, marginal: str
) -> None:
    summary = _summary(year, AGED[year], salary)

    assert _value(summary, AGE_CREDIT_RATE) == D(age_credit)
    assert _value(summary, SASKATCHEWAN_RATE) == D(saskatchewan)
    assert _value(summary, MARGINAL) == D(marginal)


# (tax year, salary, Saskatchewan rate, marginal rate): born 1980 and no year of birth.
NOT_AGED = [
    (2025, "0", "0", "0"),
    (2025, "43066", "0.0970305", "0.3069"),
    (2025, "43067", "0.0970305", "0.3069"),
    (2025, "60000", "0.1168305", "0.3861"),
    (2026, "60000", "0.116841", "0.3864"),
]


@pytest.mark.parametrize("birth_year", [1980, None])
@pytest.mark.parametrize(("year", "salary", "saskatchewan", "marginal"), NOT_AGED)
def test_born_1980_or_with_no_year_the_age_amount_adds_nothing(
    birth_year: int | None, year: int, salary: str, saskatchewan: str, marginal: str
) -> None:
    summary = _summary(year, birth_year, salary)

    assert _value(summary, AGE_CREDIT_RATE) == D("0")
    assert _value(summary, AMOUNT_GATE) == D("0")
    assert _value(summary, SASKATCHEWAN_RATE) == D(saskatchewan)
    assert _value(summary, MARGINAL) == D(marginal)
