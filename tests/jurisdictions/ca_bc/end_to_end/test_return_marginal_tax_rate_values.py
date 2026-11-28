"""The British Columbia marginal rate at a few salaries, worked by hand from the printed rates.

The marginal rate (`ca-bc/marginal_tax_rate`) is the extra take-home deductions on a further dollar
of salary, for a salary-only filer: the federal and British Columbia income tax rates and the CPP,
CPP2 and EI rates (British Columbia has no surtax and no health premium). Each figure below is the
exact sum of its parts, and the parts are the printed rates (T1 "Line 73: Rate", BC428 "Line 5:
Rate" and "Line 12: Rate", BC428 lines 73 to 79 and the payroll factor S of T4127 for the tax
reduction, Schedule 8 lines 11, 12 and 22, T2204 lines 10 and 16), with the net income rate N = 1 -
enhanced CPP rate - CPP2 rate, because T1 line 22215 takes the enhanced and the second additional
contributions off the income, and the credits at the federal and the British Columbia credit rate
on the CPP base and EI rates (c):

    federal  = bracket rate x N + BPA phase-down - 14.5% (14% in 2026) x c
    BC       = bracket rate x N - BC credit rate x c + 3.56% x N inside the tax reduction's range,
               and 0 where BC428 line 80 is 0.00
    marginal = federal + BC + CPP base + CPP enhanced + CPP2 + EI

The BC credit rate is 5.06% (5.60% in 2026). The 2026 figures are provisional: the 2026 forms are
not published, and the 2026 datasets follow the July 2026 payroll rates or are carried forward.
The engine rounds the marginal rate half-up to 0.0001 like the average rate
(`ca/take_home_average_rate_rounding`), so each expected rate in the test is the exact figure below
rounded half-up to four decimals. The extra-run check over a sweep is in
`test_return_marginal_tax_rate_extra_run.py`, the gates in `test_return_marginal_tax_rate_gates.py`.

- 2025, $2,020: only the EI of T2204 line 16 moves, 1 for 1 between $2,000 and $2,033: 1.
- 2025, $10,000: CPP 4.95% + 1% and EI 1.64% = 0.0759; no income tax.
- 2025, $20,000: federal 14.5% x 0.99 - 14.5% x 0.0659 = 0.1339945; the tax reduction of 562 takes
  all the British Columbia tax, so 0; contributions 0.0759: 0.2098945.
- 2025, $30,000 (net income 29,735, inside the reduction's range): federal 0.1339945; British
  Columbia 5.06% x 0.99 - 5.06% x 0.0659 + 3.56% x 0.99 = 0.04675946 + 0.035244 = 0.08200346;
  contributions 0.0759: 0.29189796.
- 2025, $45,000 (past the reduction): federal 0.1339945; British Columbia 0.04675946; contributions
  0.0759: 0.25665396.
- 2025, $70,000 (over the EI maximum of $65,700): federal 20.5% x 0.99 - 14.5% x 0.0495 =
  0.1957725; British Columbia 7.7% x 0.99 - 5.06% x 0.0495 = 0.0737253; contributions 0.0495 +
  0.01: 0.3289978.
- 2025, $75,000 (CPP2 band, no CPP base or EI): N = 0.96; federal 20.5% x 0.96 = 0.1968; British
  Columbia 7.7% x 0.96 = 0.07392; contributions 0.04: 0.31072.
- 2025, $100,000: no contributions; federal 20.5%; British Columbia 10.5%: 0.31.
- 2025, $120,000: no contributions; federal 26%; British Columbia 12.29%: 0.3829.
- 2025, $150,000 (above the table 1 limit of 137,407, so BC428 line 12): 26% + 14.7%: 0.407.
- 2025, $200,000: the federal basic personal amount falls over $177,882 to $253,414: 29% + 14.5% x
  1,591 / 75,532 (0.0210639 to seven places) = 0.2930542655; British Columbia 16.8%: 0.4610542655.
- 2026, $10,000: CPP 4.95% + 1% and EI 1.63%: 0.0758.
- 2026, $30,000 (inside the reduction's range, 25,570 to 44,952): federal 14% x 0.99 - 14% x 0.0658
  = 0.129388; British Columbia 5.6% x 0.99 - 5.6% x 0.0658 + 3.56% x 0.99 = 0.0517552 + 0.035244 =
  0.0869992; contributions 0.0758: 0.2921872.
- 2026, $70,000 (over the EI maximum of $68,900): federal 20.5% x 0.99 - 14% x 0.0495 = 0.19602;
  British Columbia 7.7% x 0.99 - 5.6% x 0.0495 = 0.073458; contributions 0.0595: 0.328978.
- 2026, $250,000: 29% + 14% x 1,623 / 77,042 (0.0210664 to seven places) = 0.292949296; British
  Columbia 16.8%: 0.460949296.

The fall of the age amount in the British Columbia marginal rate, worked by hand, both years.

A filer born in 1960 or earlier claims the age amount on BC428 line 17 (Worksheet BC428 "Line 58080
- Age amount") and on T1 line 30100. Worksheet line 4 is the net income over the threshold (BC:
43,169.00 in 2025 and 44,119.00 in 2026; federal: 45,522.00 and 46,432.00), line 5 the printed 15%,
line 6 line 4 times 15% and line 7 the maximum (BC: 5,799.00 and 5,927.00; federal: 9,028.00 and
9,209.00) less line 6, not below 0. Each further dollar of net income over a threshold takes 15
cents off that credit amount, and the credit is worth the credit rate (BC428 line 55: 5.06% in
2025, 5.60% in 2026; T1 line 114: 14.5% in 2025, 14% in 2026), so the rate on a further dollar of
salary is higher by

    15% x N x credit rate,   N = the part of a dollar left in the net income (1 less the CPP first
                             and second additional rates)

in British Columbia while line 4 is above 0 and an amount is still claimed, and in the federal part
from the federal threshold on (the federal amount reaches 0 only at a net income above 105,000, so
it is still falling where the British Columbia amount has run out).

The net income is the salary less the CPP enhanced contribution (T1 line 22215): 1% of the salary
over 3,500 up to the year's maximum pensionable earnings (71,300 in 2025), and the CPP2 contribution
of 4% of the salary over it, up to the second ceiling (81,200). A filer born in 1955 pays CPP in
2025 (turning 70 in the year) but not in 2026, so in 2026 her net income is her salary, N = 1 and
the contributions are the EI rate alone (1.63% up to 68,900); a filer born in 1980 pays CPP in
both years.

Each total is the exact sum of the federal rate, the British Columbia rate and the contribution
rate, rounded half-up to 0.0001. Without an age amount (born 1980, or no year of birth):

- 2025, 43,569.70 and 43,570.71: federal 14.5% x 0.99 - 14.5% x 0.0659 = 0.1339945; British
  Columbia 5.06% x 0.99 - 5.06% x 0.0659 = 0.04675946; contributions 0.0759: 0.25665396.
- 2025, 47,000: the same. 2025, 60,000: federal 20.5% x 0.99 - 14.5% x 0.0659 = 0.1933945;
  British Columbia 7.7% x 0.99 - 5.06% x 0.0659 = 0.07289546; 0.0759: 0.34218996.
- 2025, 82,902.96 and .97 (no contributions): 20.5% + 7.7% = 0.282.
- 2026, 44,119 and 44,120 (net income under 44,952, where the British Columbia tax reduction of
  BC428 lines 73 to 79 is still falling: 3.56% x 0.99 more): federal 14% x 0.99 - 14% x 0.0658 =
  0.129388; British Columbia 5.6% x 0.99 - 5.6% x 0.0658 + 3.56% x 0.99 = 0.0517552 + 0.035244 =
  0.0869992; contributions 0.0758: 0.2921872.
- 2026, 47,000: the reduction has run out: 0.129388 + 0.0517552 + 0.0758 = 0.2569432.
- 2026, 60,000: federal 20.5% x 0.99 - 14% x 0.0658 = 0.193738; British Columbia 7.7% x 0.99 - 5.6%
  x 0.0658 = 0.0725452; 0.0758: 0.3420832.
- 2026, 83,632.29 and .30 (CPP2 band, N = 0.96): 20.5% x 0.96 + 7.7% x 0.96 + 4% = 0.31072.

With the age amount (born 1955):

- 2025, 43,570.71: British Columbia part + 0.15 x 0.99 x 0.0506 = 0.0075141: 0.26416806.
- 2025, 47,000: federal + 0.15 x 0.99 x 0.145 = 0.0215325, British Columbia + 0.0075141: 0.1339945 +
  0.0215325 + 0.04675946 + 0.0075141 + 0.0759 = 0.28570056.
- 2025, 60,000: 0.1933945 + 0.0215325 + 0.07289546 + 0.0075141 + 0.0759 = 0.37123656.
- 2025, 82,902.96: federal 20.5% + 0.15 x 0.145 = 0.02175; British Columbia 7.7% + 0.15 x 0.0506 =
  0.00759: 0.205 + 0.02175 + 0.077 + 0.00759 = 0.31134.
- 2025, 82,902.97: the British Columbia term is gone, the federal one stays: 0.30375 (rounded half
  up, 0.3038).
- 2026 (no CPP: N = 1, EI 1.63% to 68,900): federal 14% x 1 - 14% x 0.0163 = 0.137718 (20.5% -
  0.002282 = 0.202718 over 58,523); British Columbia 5.6% - 5.6% x 0.0163 = 0.0550872 (7.7% -
  0.0009128 = 0.0760872 over 50,363); the terms are 0.15 x 0.056 = 0.0084 (British Columbia) and
  0.15 x 0.14 = 0.021 (federal).
  - 44,119 (the tax reduction is still falling, 3.56% x 1 more): 0.137718 + 0.0550872 + 0.0356 +
    0.0163 = 0.2447052.
  - 44,120: + 0.0084: 0.2531052.
  - 47,000: 0.137718 + 0.021 + 0.0550872 + 0.0084 + 0.0163 = 0.2385052.
  - 60,000: 0.202718 + 0.021 + 0.0760872 + 0.0084 + 0.0163 = 0.3245052.
  - 83,632.29 (no EI above 68,900): 0.205 + 0.021 + 0.077 + 0.0084 = 0.3114.
  - 83,632.30: 0.205 + 0.021 + 0.077 = 0.303.

British Columbia's gate on BC428 line 80 stays on the age term, but a filer over the age threshold
always owes British Columbia tax, so the gate is open at every salary here.
"""

from __future__ import annotations

from decimal import Decimal
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
BRITISH_COLUMBIA = JurisdictionCode("CA-BC")


@pytest.mark.parametrize(
    ("year", "salary", "rate"),
    [
        (2025, "0", "0"),
        (2025, "2020", "1"),
        (2025, "10000", "0.0759"),
        (2025, "20000", "0.2099"),
        (2025, "30000", "0.2919"),
        (2025, "45000", "0.2567"),
        (2025, "70000", "0.329"),
        (2025, "75000", "0.3107"),
        (2025, "100000", "0.31"),
        (2025, "120000", "0.3829"),
        (2025, "150000", "0.407"),
        (2025, "200000", "0.4611"),
        (2026, "10000", "0.0758"),
        (2026, "30000", "0.2922"),
        (2026, "70000", "0.329"),
        (2026, "250000", "0.4609"),
    ],
)
def test_the_marginal_rate_is_the_sum_of_the_rates_that_apply_rounded_to_four_decimals(
    year: int, salary: str, rate: str
) -> None:
    worksheets = build_tax_computation().compute(
        TaxCalculationRequest(BRITISH_COLUMBIA, year, (Artifact(EMPLOYMENT_INCOME, D(salary)),))
    )
    (summary,) = worksheets["ca-bc/return"]

    assert summary.get(bundled_kinds().kind("ca-bc/marginal_tax_rate")).value == D(rate)


def _age_return(year: int, salary: str, birth_year: int | None) -> Worksheet:
    given: list[Artifact[Any]] = [Artifact(EMPLOYMENT_INCOME, D(salary))]
    if birth_year is not None:
        given.append(Artifact(BIRTH_YEAR, birth_year))
    worksheets = build_tax_computation().compute(
        TaxCalculationRequest(BRITISH_COLUMBIA, year, tuple(given))
    )
    (summary,) = worksheets["ca-bc/return"]
    return summary


def _value(summary: Worksheet, name: str) -> Decimal:
    value = summary.get(bundled_kinds().kind(name)).value
    assert isinstance(value, Decimal)
    return value


# (year, salary, marginal rate born 1955, marginal rate born 1980 or with no year of birth),
# hand-worked in the module text.
AGE_RATES = [
    (2025, "0", "0", "0"),
    (2025, "43569.70", "0.2567", "0.2567"),
    (2025, "43570.71", "0.2642", "0.2567"),
    (2025, "47000", "0.2857", "0.2567"),
    (2025, "60000", "0.3712", "0.3422"),
    (2025, "82902.96", "0.3113", "0.282"),
    (2025, "82902.97", "0.3038", "0.282"),
    (2026, "0", "0", "0"),
    (2026, "44119", "0.2447", "0.2922"),
    (2026, "44120", "0.2531", "0.2922"),
    (2026, "47000", "0.2385", "0.2569"),
    (2026, "60000", "0.3245", "0.3421"),
    (2026, "83632.29", "0.3114", "0.3107"),
    (2026, "83632.30", "0.303", "0.3107"),
]


@pytest.mark.parametrize(("year", "salary", "born_1955", "_born_1980"), AGE_RATES)
def test_a_filer_born_1955_pays_the_fall_of_the_age_amount_in_the_marginal_rate(
    year: int, salary: str, born_1955: str, _born_1980: str
) -> None:
    summary = _age_return(year, salary, 1955)

    assert _value(summary, "ca-bc/marginal_tax_rate") == D(born_1955)


@pytest.mark.parametrize(("year", "salary", "_born_1955", "born_1980"), AGE_RATES)
@pytest.mark.parametrize("birth_year", [1980, None])
def test_a_filer_born_1980_or_with_no_birth_year_has_no_age_amount_in_the_marginal_rate(
    year: int, salary: str, _born_1955: str, born_1980: str, birth_year: int | None
) -> None:
    summary = _age_return(year, salary, birth_year)

    assert _value(summary, "ca-bc/marginal_tax_rate") == D(born_1980)


@pytest.mark.parametrize(
    ("year", "last_born", "credit_rate", "federal_credit_rate"),
    [(2025, 1960, "0.0506", "0.145"), (2026, 1961, "0.056", "0.14")],
)
def test_the_age_term_is_the_printed_rate_times_the_net_income_rate_times_the_credit_rate(
    year: int, last_born: int, credit_rate: str, federal_credit_rate: str
) -> None:
    # The last year of birth that is 65 at the end of the year (1960 in 2025, 1961 in 2026) and the
    # year after it differ in the age amount alone, and both pay CPP: 15% x 0.99 x the credit rate
    # in each part, at a salary over both thresholds.
    claims = _age_return(year, "60000", last_born)
    does_not = _age_return(year, "60000", last_born + 1)
    net_income_rate = D("0.99")

    assert _value(claims, "ca-bc/marginal_british_columbia_age_reduction_rate") == D("0.15")
    assert _value(does_not, "ca-bc/marginal_british_columbia_age_credit_rate") == D("0")
    assert _value(claims, "ca-bc/marginal_british_columbia_age_credit_rate") == (
        D("0.15") * net_income_rate * D(credit_rate)
    )
    assert _value(claims, "ca-bc/british_columbia_marginal_rate") - _value(
        does_not, "ca-bc/british_columbia_marginal_rate"
    ) == (D("0.15") * net_income_rate * D(credit_rate))
    assert _value(claims, "ca-bc/marginal_federal_rate") - _value(
        does_not, "ca-bc/marginal_federal_rate"
    ) == (D("0.15") * net_income_rate * D(federal_credit_rate))
