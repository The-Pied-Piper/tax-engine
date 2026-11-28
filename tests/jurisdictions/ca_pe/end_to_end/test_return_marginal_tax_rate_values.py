"""The Prince Edward Island marginal rate at a few salaries, worked by hand.

Each figure is worked from the printed rates.

The marginal rate (`ca-pe/marginal_tax_rate`) is the extra take-home deductions on a further dollar
of salary, for a salary-only filer: the federal and Prince Edward Island income tax rates and the
CPP, CPP2 and EI rates. Each figure below is the exact sum of its parts, and the parts are the
printed rates (T1 "Line 73: Rate", PE428 "Line 5: Rate", PE428 line 85 "Applicable rate 5%",
Schedule 8 lines 11, 12 and 22, T2204 lines 10 and 16), with the net income rate
N = 1 - enhanced CPP rate - CPP2 rate (T1 line 22215 takes the enhanced and the second additional
contributions off the income) and the credits at the federal and the Prince Edward Island credit
rate (9.5%) on the CPP base and EI rates:

    federal  = bracket rate x N + BPA phase-down - federal credit rate x (CPP base + EI)
    PE       = bracket rate x N - PE credit rate x (CPP base + EI)  (+ 5% x N while the low-income
               tax reduction is phased out), and 0 where the reduction absorbs the tax
    marginal = federal + PE + CPP base + CPP enhanced + CPP2 + EI

The check against an extra run of the engine is in `test_return_marginal_tax_rate_extra_run.py`.

- 2025, $10,000: CPP 4.95% + 1% and EI 1.64% = 0.0759; no income tax.
- 2025, $20,000: federal 14.5% x 0.99 - 14.5% x 0.0659 = 0.1339945; Prince Edward Island
  9.5% x 0.99 - 9.5% x 0.0659 = 0.0877895 (the reduction is not phased out: net income is under the
  base amount of 22,650); contributions 0.0759: 0.2976840.
- 2025, $28,000 (net income 27,755, over the base amount of 22,650 and the reduction left is
  positive): PE 0.0877895 + 5% x 0.99 = 0.1372895; federal 0.1339945; contributions 0.0759:
  0.347184.
- 2025, $40,000 (the reduction is gone; taxable income is in column 2, 13.47%): PE
  13.47% x 0.99 - 9.5% x 0.0659 = 0.127102: 0.3369965.
- 2025, $70,000 (over the EI maximum of $65,700; taxable income is in column 3, 16.6%): federal
  20.5% x 0.99 - 14.5% x 0.0495 = 0.1957725; PE 16.6% x 0.99 - 9.5% x 0.0495 = 0.1596375;
  contributions 0.0495 + 0.01: 0.41491.
- 2025, $153,824 (above the CPP ceilings, so N = 1 and nothing is left to credit; column 5, 19%):
  federal 26% + PE 19% = 0.45.
- 2025, $200,000 and $250,000 (no contributions): federal 29% + 14.5% x 1,591 / 75,532 (0.0210639
  to seven places) = 0.2930542655; PE 19%: 0.4830542655.
- 2026, $40,000: federal 14% x 0.99 - 14% x 0.0658 = 0.129388; PE 0.127102 (the 2026 datasets are
  the 2025 ones carried forward, provisional); contributions 0.0758: 0.33229.
- 2026, $70,000 (over the EI maximum of $68,900): federal 20.5% x 0.99 - 14% x 0.0495 = 0.19602;
  PE 0.1596375; contributions 0.0595: 0.4151575.

The engine rounds the marginal rate half-up to 0.0001 like the average rate
(`ca/take_home_average_rate_rounding`), so the expected values in the parametrization are the exact
sums derived above rounded half-up to four places (e.g. 0.297684 is 0.2977).

The fall of the Prince Edward Island age amount in the marginal rate, worked by hand, is pinned
below it, for a filer who gives a year of birth as well as the salary:

The age amount (PE428 line 10, Worksheet PE428 "Line 58080 - Age amount") is the printed maximum
of 6,510.00 less 15% (line 5) of the net income over 36,600.00 (line 3), for a filer born in 1960
or earlier. Each dollar of that fall is tax at the credit rate of 9.5% (PE428 line 49), and the
part of a further dollar of salary that is net income is N = 1 less the enhanced CPP rate and the
second additional CPP rate (T1 line 22215 takes both off the income). So while the net income is
over 36,600.00 and the amount is still above zero:

    age term = 0.15 x N x 0.095 = 0.01425 x N

and 0 otherwise. The amount, line 7 of the worksheet, is 0 from a net income of 80,000.00
(6,510.00 / 0.15 = 43,400.00 over the threshold); line 6 is rounded half-up to the cent, so the
cent-rounded amount is already 0.00 at 79,999.97 (0.15 x 43,399.97 = 6,509.9955) and still 0.01 at
79,999.96 (0.15 x 43,399.96 = 6,509.994).

Net income is the salary less the CPP enhanced and second additional deductions. 2025, born 1955
(the CPP is paid): 1% of the salary over 3,500 up to 71,300 (678.00 at most), and 4% of the salary
over 71,300 up to 81,200 (396.00 at most). 2026, born 1955 (71 all year, so no CPP): the net
income is the salary. The salaries below are worked back from the net income wanted:

- 2025, N = 0.99 up to 71,300: net income 0.99 x salary + 35.00. 36,934.34 gives
  36,934.34 - 334.34 = 36,600.00; 36,935.35 gives 36,935.35 - 334.35 = 36,601.00; 50,000 gives
  49,535.00; 0 gives 0.
- 2025, N = 0.96 from 71,300 to 81,200: net income salary - 678.00 - 0.04 x (salary - 71,300).
  81,067.71 gives 81,067.71 - 678.00 - 390.71 = 79,999.00; 81,068.75 gives
  81,068.75 - 678.00 - 390.75 = 80,000.00. N = 0.96 gives 0.01425 x 0.96 = 0.01368.
- 2025, 90,000: net income 90,000 - 678 - 396 = 88,926, over the amount's end: 0.
- 2026, N = 1: the term is 0.01425 at every salary the amount is still claimed.

A filer born in 1980 (under 65) or with no year of birth claims no age amount, so the term is 0
whatever the net income. In 2025 the filer born in 1955 pays the same CPP as the one born in 1980,
so the Prince Edward Island marginal rate differs from theirs by exactly the term.
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
PRINCE_EDWARD_ISLAND = JurisdictionCode("CA-PE")
RETURN = "ca-pe/return"
AGE_TERM = "ca-pe/marginal_prince_edward_island_age_credit_rate"
PROVINCIAL = "ca-pe/prince_edward_island_marginal_rate"
LINE_4 = "ca-pe/marginal_age_income_over_threshold"
CLAIMED = "ca-pe/marginal_age_amount_claimed"


@pytest.mark.parametrize(
    ("year", "salary", "rate"),
    [
        (2025, "0", "0"),
        (2025, "2020", "1"),
        (2025, "2000", "1"),
        (2025, "2000.01", "1"),
        (2025, "3500", "0.0759"),
        (2025, "3500.01", "0.0759"),
        (2025, "10000", "0.0759"),
        (2025, "20000", "0.2977"),
        (2025, "28000", "0.3472"),
        (2025, "40000", "0.3370"),
        (2025, "70000", "0.4149"),
        (2025, "153824", "0.4500"),
        (2025, "200000", "0.4831"),
        (2025, "250000", "0.4831"),
        (2026, "2000", "1"),
        (2026, "2000.01", "1"),
        (2026, "3500", "0.0758"),
        (2026, "3500.01", "0.0758"),
        (2026, "40000", "0.3323"),
        (2026, "70000", "0.4152"),
    ],
)
def test_the_marginal_rate_is_the_sum_of_the_rates_that_apply_rounded_to_four_decimals(
    year: int, salary: str, rate: str
) -> None:
    worksheets = build_tax_computation().compute(
        TaxCalculationRequest(PRINCE_EDWARD_ISLAND, year, (Artifact(EMPLOYMENT_INCOME, D(salary)),))
    )
    (summary,) = worksheets["ca-pe/return"]

    assert summary.get(bundled_kinds().kind("ca-pe/marginal_tax_rate")).value == D(rate)


# Year, salary, then the worksheet's line 4 (net income over 36,600.00), the age amount claimed
# (line 7) and the term for a filer born in 1955.
BORN_1955 = [
    # 2025: net income 0, then exactly the threshold (no effect), one dollar over, mid-range.
    (2025, "0", "0.00", "6510.00", "0"),
    (2025, "36934.34", "0.00", "6510.00", "0"),
    (2025, "36935.35", "1.00", "6509.85", "0.0141075"),
    (2025, "50000", "12935.00", "4569.75", "0.0141075"),
    # 2025: the last whole dollar of net income before the amount is used up, and the first at 0.
    (2025, "81067.71", "43399.00", "0.15", "0.01368"),
    (2025, "81068.75", "43400.00", "0.00", "0"),
    (2025, "90000", "52326.00", "0.00", "0"),
    # 2026: net income is the salary.
    (2026, "0", "0.00", "6510.00", "0"),
    (2026, "36600", "0.00", "6510.00", "0"),
    (2026, "36601", "1.00", "6509.85", "0.01425"),
    (2026, "60000", "23400.00", "3000.00", "0.01425"),
    (2026, "79999", "43399.00", "0.15", "0.01425"),
    (2026, "79999.96", "43399.96", "0.01", "0.01425"),
    (2026, "79999.97", "43399.97", "0.00", "0"),
    (2026, "80000", "43400.00", "0.00", "0"),
    (2026, "90000", "53400.00", "0.00", "0"),
]


def _worksheet(year: int, salary: str, birth_year: int | None) -> Worksheet:
    artifacts: list[Artifact[Decimal] | Artifact[int]] = [Artifact(EMPLOYMENT_INCOME, D(salary))]
    if birth_year is not None:
        artifacts.append(Artifact(BIRTH_YEAR, birth_year))
    worksheets = build_tax_computation().compute(
        TaxCalculationRequest(PRINCE_EDWARD_ISLAND, year, tuple(artifacts))
    )
    (summary,) = worksheets[RETURN]
    return summary


def _figure(summary: Worksheet, kind: str) -> Decimal:
    value = summary.get(bundled_kinds().kind(kind)).value
    assert isinstance(value, Decimal)
    return value


@pytest.mark.parametrize(("year", "salary", "line_4", "claimed", "term"), BORN_1955)
def test_the_age_amount_term_of_a_filer_born_in_1955_is_the_credit_rate_on_its_fall(
    year: int, salary: str, line_4: str, claimed: str, term: str
) -> None:
    summary = _worksheet(year, salary, 1955)

    assert _figure(summary, LINE_4) == D(line_4)
    assert _figure(summary, CLAIMED) == D(claimed)
    assert _figure(summary, AGE_TERM) == D(term)


@pytest.mark.parametrize("birth_year", [1980, None])
@pytest.mark.parametrize(
    ("year", "salary"),
    [
        (2025, "0"),
        (2025, "36934.34"),
        (2025, "36935.35"),
        (2025, "50000"),
        (2025, "81067.71"),
        (2025, "81068.75"),
        (2026, "36601"),
        (2026, "60000"),
        (2026, "79999"),
        (2026, "79999.97"),
    ],
)
def test_a_filer_born_in_1980_or_with_no_year_of_birth_has_no_age_amount_term(
    birth_year: int | None, year: int, salary: str
) -> None:
    summary = _worksheet(year, salary, birth_year)

    assert _figure(summary, CLAIMED) == D("0")
    assert _figure(summary, AGE_TERM) == D("0")


@pytest.mark.parametrize(
    ("salary", "term"),
    [
        ("36934.34", "0"),
        ("36935.35", "0.0141075"),
        ("50000", "0.0141075"),
        ("81067.71", "0.01368"),
        ("81068.75", "0"),
    ],
)
@pytest.mark.parametrize("other_birth_year", [1980, None])
def test_the_provincial_marginal_rate_of_the_1955_filer_is_higher_by_the_term_in_2025(
    salary: str, term: str, other_birth_year: int | None
) -> None:
    older = _figure(_worksheet(2025, salary, 1955), PROVINCIAL)
    other = _figure(_worksheet(2025, salary, other_birth_year), PROVINCIAL)

    assert older - other == D(term)
