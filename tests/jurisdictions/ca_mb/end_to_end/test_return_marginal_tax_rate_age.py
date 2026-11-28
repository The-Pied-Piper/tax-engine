"""The fall of the Manitoba age amount in the marginal tax rate, worked by hand from the printed
rates, through the real engine (2025 and 2026).

For a filer born in 1960 or earlier, Worksheet MB428 "Line 58080 - Age amount" line 4 is the net
income over the threshold of 27,749.00, line 5 is the printed rate of 15%, and line 7 is the maximum
of 3,728.00 less 15% of line 4, claimed up to a net income of 52,601.99 (the printed "$52,602 or
more, enter 0"). A further dollar of net income takes 15% of a dollar off the amount, and each
dollar of it is tax at the MB428 line 52 rate of 10.8%. With N the part of a dollar of salary left
in the net income (1 - enhanced CPP rate, 0.99, or 1 where no CPP is paid):

    age term = 15% x 10.8% x N = 0.0162 x N, from 0.01 over the threshold to 52,601.99 of net income

The Manitoba marginal rate adds it to the bracket rate beside the family tax benefit's fall (9% x
10.8% x N while Schedule MB428-A line 12 is above 0; a filer born in 1960 or earlier has the age
amount of 2,065.00 on its line 4, so line 12 is 4,130.00 less 9% of the net income, above 0 up to a
net income of 45,888.88) and less the credit on CPP and EI. The federal age amount falls the same
way from its own threshold (T1: 15% x N x the federal credit rate), which the federal half carries.

The exact Manitoba terms, with the credit on the CPP base and EI taken off (10.8% x the
credit-earning contribution rate), for 2025 (N = 0.99, credit-earning rate 0.0659, a filer born in
1955 is 70 and still pays CPP) and 2026 (born in 1955 pays no CPP, N = 1, credit-earning rate
0.0163 EI; born in 1980, N = 0.99, rate 0.0658):

    2025, 10.8% bracket: 0.10692 - 0.0071172 = 0.0998028; 12.75%: 0.126225 - 0.0071172 = 0.1191078
    2025 family tax benefit 0.00972 x 0.99 = 0.0096228; age 0.0162 x 0.99 = 0.016038
    2026 born 1955: 10.8%: 0.108 - 0.0017604 = 0.1062396; 12.75%: 0.1275 - 0.0017604 = 0.1257396;
         family tax benefit 0.00972; age 0.0162
    2026 born 1980: 10.8%: 0.10692 - 0.0071064 = 0.0998136; 12.75%: 0.126225 - 0.0071064 = 0.1191186

The marginal tax rate is the federal rate (14.5% blended in 2025, 14% in 2026, rising with the
bracket, and with the federal age term of 15% x N x the federal credit rate: 0.0215325 in 2025,
0.021 in 2026 from a net income of 46,432.00 in 2026 and 45,522.00 in 2025), plus the Manitoba rate
and the contribution rate (2025: 0.0759; 2026: 0.0758, or 0.0163 for the filer born in 1955),
rounded half-up to 0.0001. The net income is the salary less the enhanced CPP (1% of the salary over
3,500, rounded to the cent) in 2025 and for a filer born in 1980 in 2026, the salary itself for a
filer born in 1955 in 2026, which fixes each salary below: 27,993.94 and 27,993.95 are a net income
of 27,749.00 and 27,749.01 in 2025; 53,097.97 and 53,097.98 are 52,601.99 and 52,602.00.
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
MANITOBA = JurisdictionCode("CA-MB")
RETURN = "ca-mb/return"
AGE_RATE = "ca-mb/marginal_manitoba_age_rate"
MANITOBA_RATE = "ca-mb/manitoba_marginal_rate"
MARGINAL = "ca-mb/marginal_tax_rate"


def _summary(year: int, salary: str, born: int | None) -> Worksheet:
    artifacts: list[Artifact[Decimal] | Artifact[int]] = [Artifact(EMPLOYMENT_INCOME, D(salary))]
    if born is not None:
        artifacts.append(Artifact(BIRTH_YEAR, born))
    worksheets = build_tax_computation().compute(
        TaxCalculationRequest(MANITOBA, year, tuple(artifacts))
    )
    (summary,) = worksheets[RETURN]
    return summary


def _value(sheet: Worksheet, name: str) -> Decimal:
    value = sheet.get(bundled_kinds().kind(name)).value
    assert isinstance(value, Decimal)
    return value


# Born 1955, 2025: salary, age term, Manitoba marginal rate. 27,993.94 is a net income of exactly
# the threshold (line 4 is 0.00, no effect); the family tax benefit's fall is still counted.
BORN_1955_2025 = [
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
BORN_1955_2026 = [
    ("0", "0", "0"),
    ("27749", "0", "0.1159596"),
    ("27749.01", "0.0162", "0.1321596"),
    ("40000", "0.0162", "0.1321596"),
    ("46000", "0.0162", "0.1224396"),
    ("50000", "0.0162", "0.1419396"),
    ("52601.99", "0.0162", "0.1419396"),
    ("52602", "0", "0.1257396"),
    ("60000", "0", "0.1257396"),
]
# Born 1980 or no year of birth: no age amount, so no age term at any salary.
UNDER_65_2025 = [
    ("0", "0", "0"),
    ("27993.94", "0", "0.0998028"),
    ("27993.95", "0", "0.0998028"),
    ("40000", "0", "0.0998028"),
    ("50000", "0", "0.1191078"),
    ("53097.97", "0", "0.1191078"),
    ("53097.98", "0", "0.1191078"),
    ("60000", "0", "0.1191078"),
]
UNDER_65_2026 = [
    ("0", "0", "0"),
    ("27993.94", "0", "0.0998136"),
    ("27993.95", "0", "0.0998136"),
    ("40000", "0", "0.0998136"),
    ("50000", "0", "0.1191186"),
    ("53097.97", "0", "0.1191186"),
    ("53097.98", "0", "0.1191186"),
    ("60000", "0", "0.1191186"),
]
CASES = (
    [(2025, 1955, *row) for row in BORN_1955_2025]
    + [(2026, 1955, *row) for row in BORN_1955_2026]
    + [
        (year, born, *row)
        for born in (1980, None)
        for year, rows in ((2025, UNDER_65_2025), (2026, UNDER_65_2026))
        for row in rows
    ]
)


@pytest.mark.parametrize(("year", "born", "salary", "age", "manitoba"), CASES)
def test_the_age_term_and_the_manitoba_marginal_rate(
    year: int, born: int | None, salary: str, age: str, manitoba: str
) -> None:
    summary = _summary(year, salary, born)

    assert _value(summary, AGE_RATE) == D(age)
    assert _value(summary, MANITOBA_RATE) == D(manitoba)


# Salary, marginal tax rate: federal + Manitoba + contribution rates, worked as in the header.
TOTALS = [
    (2025, 1955, "40000", "0.3354"),  # 0.1339945 + 0.1254636 + 0.0759 = 0.3353581
    (2025, 1955, "46000", "0.3569"),  # 0.155527 + 0.1254636 + 0.0759 = 0.3568906
    (2025, 1955, "50000", "0.3666"),  # 0.155527 + 0.1351458 + 0.0759 = 0.3665728
    (2025, 1955, "53097.97", "0.3666"),
    (2025, 1955, "53097.98", "0.3505"),  # 0.155527 + 0.1191078 + 0.0759 = 0.3505348
    (2025, 1955, "60000", "0.4099"),  # 0.214927 + 0.1191078 + 0.0759 = 0.4099348
    (2025, 1980, "40000", "0.3097"),  # 0.1339945 + 0.0998028 + 0.0759 = 0.3096973
    (2025, 1980, "53097.97", "0.3290"),  # 0.1339945 + 0.1191078 + 0.0759 = 0.3290023
    (2025, None, "53097.98", "0.3290"),
    (2026, 1955, "40000", "0.2862"),  # 0.137718 + 0.1321596 + 0.0163 = 0.2861776
    (2026, 1955, "46000", "0.2765"),  # 0.137718 + 0.1224396 + 0.0163 = 0.2764576
    (2026, 1955, "50000", "0.3170"),  # 0.158718 + 0.1419396 + 0.0163 = 0.3169576
    (2026, 1955, "52601.99", "0.3170"),
    (2026, 1955, "52602", "0.3008"),  # 0.158718 + 0.1257396 + 0.0163 = 0.3007576
    (2026, 1980, "40000", "0.3050"),  # 0.129388 + 0.0998136 + 0.0758 = 0.3050016
    (2026, None, "50000", "0.3243"),  # 0.129388 + 0.1191186 + 0.0758 = 0.3243066
]


@pytest.mark.parametrize(("year", "born", "salary", "rate"), TOTALS)
def test_the_marginal_tax_rate_with_the_fall_of_the_age_amount(
    year: int, born: int | None, salary: str, rate: str
) -> None:
    assert _value(_summary(year, salary, born), MARGINAL) == D(rate)


def test_the_age_term_is_the_printed_rate_times_the_credit_rate_times_the_net_income_rate() -> None:
    # 15% x 10.8% x 0.99, exact, the credit rate not rounded to the cent.
    assert _value(_summary(2025, "40000", 1955), AGE_RATE) == D("0.15") * D("0.108") * D("0.99")
