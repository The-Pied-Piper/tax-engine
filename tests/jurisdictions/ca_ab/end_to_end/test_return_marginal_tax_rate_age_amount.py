"""The fall of the Alberta age amount in the Alberta marginal tax rate, for 2025 and 2026, through
the real engine, worked by hand from the printed rates.

A filer born in 1960 or earlier claims the age amount (AB428 line 17, Worksheet AB428 "Line 58080 -
Age amount"). The amount falls by the printed rate (line 5 "Applicable rate 15%") of every dollar
of net income over the threshold (line 3: 46,308 for 2025, 47,234 for 2026) until it is 0 (the
maximum, line 1: 6,221 for 2025, 6,345 for 2026), and each dollar of that fall costs the Alberta
credit rate (AB428 line 53, 8%). So over the threshold, while an amount is still claimed:

    Alberta age term = 15% x N x 8%      (N is the part of a further dollar left in the net income)
    federal age term = 15% x N x federal credit rate (14.5% for 2025, 14% for 2026)

The federal term uses the federal threshold (45,522 for 2025, 46,432 for 2026) and maximum (9,028;
9,209), which are over by the time these salaries reach the Alberta threshold and last longer. The
Alberta term counts only where AB428 line 68 is above 0, as the rest of the Alberta rate.

The salaries are the salary that puts the net income (T1 line 23600) at a printed figure. Below
the CPP maximum the enhanced CPP deduction is 1% of the salary over 3,500, rounded to the cent, and
N = 0.99; above the second additional maximum the two deductions are at their maximum (2025: 1% of
71,300 - 3,500 = 678 and 4% of 81,200 - 71,300 = 396; 2026: 711 and 416) and N = 1.

- 2025, net income 46,308 (salary 46,740.40: 1% of 43,240.40 is 432.40, rounded; 46,740.40 - 432.40
  = 46,308.00): worksheet line 4 is 0, no Alberta term; one dollar more (salary 46,741.41, net
  46,309.00): line 4 is 1, the term 0.15 x 0.99 x 0.08 = 0.01188 (the Alberta rate 0.073928 +
  0.01188 = 0.085808).
- 2025, net income 87,781 (salary 88,855.00, 87,781 + 1,074): line 4 is 41,473, line 6 is 6,220.95,
  line 7 is 0.05, still claimed: 10% + 15% x 8% = 0.112; one dollar more (88,856.00): line 4 is
  41,474, line 6 is 6,221.10, line 7 is 0: 0.1.
- 2026, net income 47,234 (salary 47,675.76: 1% of 44,175.76 is 441.76; 47,675.76 - 441.76 =
  47,234.00) and 47,235 (salary 47,676.77); net income 89,533 (salary 90,660.00, 89,533 + 1,127):
  line 4 is 42,299, line 6 is 6,344.85, line 7 is 0.15; 89,534 (salary 90,661.00): line 4 is 42,300,
  line 6 is 6,345.00, line 7 is 0.
- The contribution rate is 0.0759 (2025) or 0.0758 (2026) below the CPP maximum (CPP 4.95% + 1% and
  EI 1.64% or 1.63%) and 0 above all the maximums. The federal rate before the age term is the
  bracket rate x N less the federal credit rate x (CPP base + EI).
- A filer born in 1980, or with no year of birth, claims no age amount: the rate is the one without
  the age term, and the amount gate (`ca-ab/marginal_age_amount_gate`) is 0.

The filer is born in 1955 for 2025 and in 1956 for 2026: a filer 70 or older all year (born 1955 or
earlier, for 2026) pays no CPP, which changes N and the contribution rate and is not what is pinned
here.

The marginal tax rate is the exact sum of its three parts rounded half-up to 0.0001.
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
ALBERTA = JurisdictionCode("CA-AB")
BORN = {2025: 1955, 2026: 1956}
RETURN = "ca-ab/return"

# Year, salary, then for a filer without the age amount and for one born in 1955 (1956 for 2026): the Alberta
# marginal rate, the federal marginal rate and the marginal tax rate; the contribution rate, the
# age threshold gate and the age amount gate of the filer born in 1955 or 1956.
ROWS = [
    (2025, "0", ("0", "0", "0"), ("0", "0", "0"), "0", "0", "1"),
    (
        2025,
        "46740.40",
        ("0.073928", "0.1339945", "0.2838"),
        ("0.073928", "0.155527", "0.3054"),
        "0.0759",
        "0",
        "1",
    ),
    (
        2025,
        "46741.41",
        ("0.073928", "0.1339945", "0.2838"),
        ("0.085808", "0.155527", "0.3172"),
        "0.0759",
        "1",
        "1",
    ),
    (
        2025,
        "50000",
        ("0.073928", "0.1339945", "0.2838"),
        ("0.085808", "0.155527", "0.3172"),
        "0.0759",
        "1",
        "1",
    ),
    (2025, "88855", ("0.1", "0.205", "0.305"), ("0.112", "0.22675", "0.3388"), "0", "1", "1"),
    (2025, "88856", ("0.1", "0.205", "0.305"), ("0.1", "0.22675", "0.3268"), "0", "1", "0"),
    (2026, "0", ("0", "0", "0"), ("0", "0", "0"), "0", "0", "1"),
    (
        2026,
        "47675.76",
        ("0.073936", "0.129388", "0.2791"),
        ("0.073936", "0.150178", "0.2999"),
        "0.0758",
        "0",
        "1",
    ),
    (
        2026,
        "47676.77",
        ("0.073936", "0.129388", "0.2791"),
        ("0.085816", "0.150178", "0.3118"),
        "0.0758",
        "1",
        "1",
    ),
    (
        2026,
        "50000",
        ("0.073936", "0.129388", "0.2791"),
        ("0.085816", "0.150178", "0.3118"),
        "0.0758",
        "1",
        "1",
    ),
    (2026, "90660", ("0.1", "0.205", "0.305"), ("0.112", "0.226", "0.338"), "0", "1", "1"),
    (2026, "90661", ("0.1", "0.205", "0.305"), ("0.1", "0.226", "0.326"), "0", "1", "0"),
]


def _summary(year: int, salary: str, birth_year: int | None) -> Worksheet:
    given: tuple[Artifact[Decimal] | Artifact[int], ...] = (Artifact(EMPLOYMENT_INCOME, D(salary)),)
    if birth_year is not None:
        given = (*given, Artifact(BIRTH_YEAR, birth_year))
    worksheets = build_tax_computation().compute(TaxCalculationRequest(ALBERTA, year, given))
    (summary,) = worksheets[RETURN]
    return summary


def _value(sheet: Worksheet, name: str) -> Decimal:
    value = sheet.get(bundled_kinds().kind(name)).value
    assert isinstance(value, Decimal)
    return value


@pytest.mark.parametrize(
    ("year", "salary", "without", "born_1955", "contribution", "threshold_gate", "amount_gate"),
    ROWS,
)
def test_the_age_amount_fall_is_in_the_rates_of_a_filer_born_in_1955(
    year: int,
    salary: str,
    without: tuple[str, str, str],
    born_1955: tuple[str, str, str],
    contribution: str,
    threshold_gate: str,
    amount_gate: str,
) -> None:
    summary = _summary(year, salary, BORN[year])

    assert _value(summary, "ca-ab/alberta_marginal_rate") == D(born_1955[0])
    assert _value(summary, "ca-ab/marginal_federal_rate") == D(born_1955[1])
    assert _value(summary, "ca-ab/marginal_contribution_rate") == D(contribution)
    assert _value(summary, "ca-ab/marginal_tax_rate") == D(born_1955[2])
    assert _value(summary, "ca-ab/marginal_age_threshold_gate") == D(threshold_gate)
    assert _value(summary, "ca-ab/marginal_age_amount_gate") == D(amount_gate)
    assert D(born_1955[2]) >= D(without[2])


@pytest.mark.parametrize(("year", "salary", "without"), [(row[0], row[1], row[2]) for row in ROWS])
@pytest.mark.parametrize("birth_year", [1980, None])
def test_a_filer_born_in_1980_or_with_no_year_has_no_age_term(
    year: int, salary: str, without: tuple[str, str, str], birth_year: int | None
) -> None:
    summary = _summary(year, salary, birth_year)

    assert _value(summary, "ca-ab/alberta_marginal_rate") == D(without[0])
    assert _value(summary, "ca-ab/marginal_federal_rate") == D(without[1])
    assert _value(summary, "ca-ab/marginal_tax_rate") == D(without[2])
    assert _value(summary, "ca-ab/marginal_age_amount_gate") == D("0")
    assert _value(summary, "ca-ab/marginal_alberta_age_credit_rate") == D("0")


@pytest.mark.parametrize(
    ("year", "salary", "age_credit_rate"),
    [
        (2025, "46740.40", "0"),
        (2025, "46741.41", "0.01188"),
        (2025, "88855", "0.012"),
        (2025, "88856", "0"),
        (2026, "47675.76", "0"),
        (2026, "47676.77", "0.01188"),
        (2026, "90660", "0.012"),
        (2026, "90661", "0"),
    ],
)
def test_the_alberta_age_credit_rate_is_the_fall_times_the_credit_rate_inside_the_range(
    year: int, salary: str, age_credit_rate: str
) -> None:
    summary = _summary(year, salary, BORN[year])

    assert _value(summary, "ca-ab/marginal_alberta_age_credit_rate") == D(age_credit_rate)
