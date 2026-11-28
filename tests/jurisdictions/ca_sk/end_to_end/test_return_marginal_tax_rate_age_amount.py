"""The Saskatchewan marginal rate for a filer born in 1960 or earlier: the age amount falling.

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
THRESHOLD_GATE = "ca-sk/marginal_age_threshold_gate"
AMOUNT_GATE = "ca-sk/marginal_age_amount_gate"
SASKATCHEWAN_RATE = "ca-sk/saskatchewan_marginal_rate"
MARGINAL = "ca-sk/marginal_tax_rate"
# The year of birth of the aged filer. Born in 1955 a filer turns 70 during 2025, a year that still
# has CPP months (and so the enhanced CPP deduction from the net income), so 2025 uses 1950 (no CPP
# months), the net income there being the salary; 2026 uses 1955.
AGED = {2025: 1950, 2026: 1955}


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


@pytest.mark.parametrize(
    ("year", "salary", "threshold_gate", "amount_gate"),
    [
        (2025, "43066", "0", "1"),
        (2025, "43067", "1", "1"),
        (2025, "81632", "1", "1"),
        (2025, "81633", "1", "0"),
        (2026, "43927", "0", "1"),
        (2026, "43928", "1", "1"),
        (2026, "83266", "1", "1"),
        (2026, "83267", "1", "0"),
    ],
)
def test_born_1955_the_two_gates_open_over_the_threshold_and_while_an_amount_is_claimed(
    year: int, salary: str, threshold_gate: str, amount_gate: str
) -> None:
    summary = _summary(year, AGED[year], salary)

    assert _value(summary, THRESHOLD_GATE) == D(threshold_gate)
    assert _value(summary, AMOUNT_GATE) == D(amount_gate)


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
