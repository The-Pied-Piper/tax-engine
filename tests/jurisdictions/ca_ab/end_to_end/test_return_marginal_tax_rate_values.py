"""The Alberta marginal rate at a few salaries, worked by hand from the printed rates.

The marginal rate (`ca-ab/marginal_tax_rate`) is the extra take-home deductions on a further dollar
of salary, for a salary-only filer with no paid credits. Each figure below is the exact sum of its
parts, and the parts are the printed rates (T1 "Line 73: Rate", AB428 "Line 5: Rate", "Line 12:
Rate" and "Line 53: Alberta non-refundable tax credit rate 8%", Schedule 8 lines 11, 12 and 22,
T2204 lines 10 and 16), with the net income rate N = 1 - enhanced CPP rate - CPP2 rate, because T1
line 22215 takes the enhanced and the second additional contributions off the income, and the
credits at the federal and the Alberta credit rate on the CPP base and EI rates:

    federal  = bracket rate x N + BPA phase-down - federal credit rate x (CPP base + EI)
    Alberta  = bracket rate x N - 8% x (CPP base + EI), counted where AB428 line 68 is above 0
               (Alberta has no tax reduction, surtax or health premium)
    marginal = federal + Alberta + CPP base + CPP enhanced + CPP2 + EI

The engine rounds the marginal rate half-up to 0.0001 like the average rate
(`ca/take_home_average_rate_rounding`), so each expected marginal rate in the tests is the exact
figure derived in the comments rounded half-up to four decimals; the parts stay exact.

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

The extra-run check over a sweep is in `test_return_marginal_tax_rate_extra_run.py`.

- $100: nothing moves (under the CPP exemption and the EI $2,000): 0.
- $2,001: only the EI of T2204 line 16 moves, 1 for 1 between $2,000 and $2,033: 1.
- $2,000 and $3,500, both years (exact band edges): the EI band reads the lower band at $2,000 (0),
  but a contribution band reads its own rate from its lower bound, so the CPP starts at exactly
  $3,500: CPP 4.95% + 1% and EI (1.64% in 2025, 1.63% in 2026) = 0.0759 and 0.0758, the same as
  the next cent; no income tax at that salary.
- 2025, $71,300 (the CPP maximum pensionable earnings, where the CPP base ends and the CPP2 band
  starts): the CPP2 band starts at exactly $71,300, so it reads its 4% there, like a cent more:
  0.3328 (N = 0.96: 20.5% x 0.96 + 10% x 0.96 + 4%), and no CPP base.
- 2025, $20,000: federal 14.5% x 0.99 - 14.5% x 0.0659 = 0.1339945; Alberta line 68 is 0.00 (the
  credits are over the tax), so 0; contributions 0.0759: 0.2098945. At $23,931.13 line 68 is first
  0.01, and the Alberta part 8% x 0.99 - 8% x 0.0659 = 0.073928 counts.
- 2025, $70,000 (over the EI maximum): federal 20.5% x 0.99 - 14.5% x 0.0495 = 0.1957725; Alberta
  10% x 0.99 - 8% x 0.0495 = 0.09504; contributions 0.0495 + 0.01: 0.3503125.
- $120,000 and $160,000 (no contributions): the bracket rates alone, 26% + 10% and 26% + 12%.
- 2025, $200,000: the federal basic personal amount falls over $177,882 to $253,414 (T1 line 77,
  Federal Worksheet lines 2, 6 and 8): 29% + 14.5% x 1,591 / 75,532 (0.0210639 to seven places) =
  0.2930542655; Alberta 13% (AB428 line 12): 0.4230542655.
- 2026, $70,000: federal 20.5% x 0.99 - 14% x 0.0495 = 0.19602; Alberta 0.09504; 0.0595: 0.35056.
- 2026, $200,000: 29% + 14% x 1,623 / 77,042 (0.0210664 to seven places) = 0.292949296; Alberta
  13%: 0.422949296.

The age amount cases (`ROWS`, below) are the salaries that put the net income (T1 line 23600) at a
printed figure. Below the CPP maximum the enhanced CPP deduction is 1% of the salary over 3,500,
rounded to the cent, and N = 0.99; above the second additional maximum the two deductions are at
their maximum (2025: 1% of 71,300 - 3,500 = 678 and 4% of 81,200 - 71,300 = 396; 2026: 711 and 416)
and N = 1.

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
- The contribution rate is 0.0759 (2025) or 0.0758 (2026) below the CPP maximum (CPP 4.95% + 1%
  and EI 1.64% or 1.63%) and 0 above all the maximums. The federal rate before the age term is the
  bracket rate x N less the federal credit rate x (CPP base + EI).
- A filer born in 1980, or with no year of birth, claims no age amount: the rate is the one without
  the age term.

The filer is born in 1955 for 2025 and in 1956 for 2026: a filer 70 or older all year (born 1955 or
earlier, for 2026) pays no CPP, which changes N and the contribution rate and is not what is pinned
here. The gates and the credit rate of the age term are in `test_return_marginal_tax_rate_gates.py`
and `..._gates_2026.py`.
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


@pytest.mark.parametrize(
    ("year", "salary", "rate"),
    [
        (2025, "100", "0"),
        (2026, "100", "0"),
        (2025, "2000", "1"),
        (2025, "2000.01", "1"),
        (2026, "2000", "1"),
        (2026, "2000.01", "1"),
        (2025, "3500", "0.0759"),
        (2025, "3500.01", "0.0759"),
        (2025, "71300", "0.3328"),
        (2025, "71300.01", "0.3328"),
        (2026, "3500", "0.0758"),
        (2026, "3500.01", "0.0758"),
        (2025, "20000", "0.2099"),
        (2026, "20000", "0.2052"),
        (2025, "70000", "0.3503"),
        (2026, "70000", "0.3506"),
        (2025, "120000", "0.36"),
        (2026, "120000", "0.36"),
        (2025, "160000", "0.38"),
        (2026, "160000", "0.38"),
        (2025, "200000", "0.4231"),
        (2026, "200000", "0.4229"),
    ],
)
def test_the_marginal_rate_is_the_sum_of_the_rates_that_apply_rounded_to_four_decimals(
    year: int, salary: str, rate: str
) -> None:
    worksheets = build_tax_computation().compute(
        TaxCalculationRequest(ALBERTA, year, (Artifact(EMPLOYMENT_INCOME, D(salary)),))
    )
    (summary,) = worksheets["ca-ab/return"]

    assert summary.get(bundled_kinds().kind("ca-ab/marginal_tax_rate")).value == D(rate)


# Year, salary, then for a filer without the age amount and for one born in 1955 (1956 for 2026):
# the Alberta marginal rate, the federal marginal rate and the marginal tax rate; then the
# contribution rate (the same for both).
AGE_ROWS = [
    (2025, "0", ("0", "0", "0"), ("0", "0", "0"), "0"),
    (
        2025,
        "46740.40",
        ("0.073928", "0.1339945", "0.2838"),
        ("0.073928", "0.155527", "0.3054"),
        "0.0759",
    ),
    (
        2025,
        "46741.41",
        ("0.073928", "0.1339945", "0.2838"),
        ("0.085808", "0.155527", "0.3172"),
        "0.0759",
    ),
    (
        2025,
        "50000",
        ("0.073928", "0.1339945", "0.2838"),
        ("0.085808", "0.155527", "0.3172"),
        "0.0759",
    ),
    (2025, "88855", ("0.1", "0.205", "0.305"), ("0.112", "0.22675", "0.3388"), "0"),
    (2025, "88856", ("0.1", "0.205", "0.305"), ("0.1", "0.22675", "0.3268"), "0"),
    (2026, "0", ("0", "0", "0"), ("0", "0", "0"), "0"),
    (
        2026,
        "47675.76",
        ("0.073936", "0.129388", "0.2791"),
        ("0.073936", "0.150178", "0.2999"),
        "0.0758",
    ),
    (
        2026,
        "47676.77",
        ("0.073936", "0.129388", "0.2791"),
        ("0.085816", "0.150178", "0.3118"),
        "0.0758",
    ),
    (
        2026,
        "50000",
        ("0.073936", "0.129388", "0.2791"),
        ("0.085816", "0.150178", "0.3118"),
        "0.0758",
    ),
    (2026, "90660", ("0.1", "0.205", "0.305"), ("0.112", "0.226", "0.338"), "0"),
    (2026, "90661", ("0.1", "0.205", "0.305"), ("0.1", "0.226", "0.326"), "0"),
]


def _age_summary(year: int, salary: str, birth_year: int | None) -> Worksheet:
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


@pytest.mark.parametrize(("year", "salary", "without", "born_1955", "contribution"), AGE_ROWS)
def test_the_age_amount_fall_is_in_the_rates_of_a_filer_born_in_1955(
    year: int,
    salary: str,
    without: tuple[str, str, str],
    born_1955: tuple[str, str, str],
    contribution: str,
) -> None:
    summary = _age_summary(year, salary, BORN[year])

    assert _value(summary, "ca-ab/alberta_marginal_rate") == D(born_1955[0])
    assert _value(summary, "ca-ab/marginal_federal_rate") == D(born_1955[1])
    assert _value(summary, "ca-ab/marginal_contribution_rate") == D(contribution)
    assert _value(summary, "ca-ab/marginal_tax_rate") == D(born_1955[2])
    assert D(born_1955[2]) >= D(without[2])


@pytest.mark.parametrize(
    ("year", "salary", "without"), [(row[0], row[1], row[2]) for row in AGE_ROWS]
)
@pytest.mark.parametrize("birth_year", [1980, None])
def test_a_filer_born_in_1980_or_with_no_year_has_no_age_term(
    year: int, salary: str, without: tuple[str, str, str], birth_year: int | None
) -> None:
    summary = _age_summary(year, salary, birth_year)

    assert _value(summary, "ca-ab/alberta_marginal_rate") == D(without[0])
    assert _value(summary, "ca-ab/marginal_federal_rate") == D(without[1])
    assert _value(summary, "ca-ab/marginal_tax_rate") == D(without[2])
