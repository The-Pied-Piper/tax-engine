"""The Nova Scotia marginal rate at a few salaries, worked by hand.

Each figure is worked from the printed rates.

The marginal rate (`ca-ns/marginal_tax_rate`) is the extra take-home deductions on a further dollar
of salary, for a salary-only filer: the federal and Nova Scotia income tax rates and the CPP, CPP2
and EI rates. Each figure below is the exact sum of its parts, and the parts are the printed rates
(T1 "Line 73: Rate", NS428 "Line 5: Rate", NS428 line 82 "Applicable rate 5%", Schedule 8 lines 11,
12 and 22, T2204 lines 10 and 16), with the net income rate N = 1 - enhanced CPP rate - CPP2 rate
(T1 line 22215 takes the enhanced and the second additional contributions off the income) and the
credits at the federal and the Nova Scotia credit rate (8.79%, NS428 line 47) on the CPP base and EI
rates:

    federal  = bracket rate x N + BPA phase-down - federal credit rate x (CPP base + EI)
    NS       = bracket rate x N - 8.79% x (CPP base + EI)  (+ 5% x N while the low-income tax
               reduction is phased out), and 0 where the reduction absorbs the tax
    marginal = federal + NS + CPP base + CPP enhanced + CPP2 + EI

The check against an extra run of the engine is in `test_return_marginal_tax_rate_extra_run.py`.

- 2025, $10,000: CPP 4.95% + 1% and EI 1.64% = 0.0759; no income tax.
- 2025, $15,000 (net income 14,885, under the base amount of 15,000): the reduction of $300 absorbs
  the tax, so Nova Scotia 0; no federal tax; contributions 0.0759.
- 2025, $18,000 (net income over 15,000 and the reduction left is positive, tax above zero): NS
  8.79% x 0.99 - 8.79% x 0.0659 + 5% x 0.99 = 0.13072839; no federal tax; contributions 0.0759:
  0.20662839.
- 2025, $28,000: federal 14.5% x 0.99 - 14.5% x 0.0659 = 0.1339945; NS (the reduction is gone)
  0.08122839; contributions 0.0759: 0.29112289.
- 2025, $40,000 (second bracket, 14.95%): NS 14.95% x 0.99 - 8.79% x 0.0659 = 0.14221239; federal
  0.1339945; contributions 0.0759: 0.35210689.
- 2025, $70,000 (over the EI maximum of $65,700, third bracket 16.67%): federal 20.5% x 0.99 -
  14.5% x 0.0495 = 0.1957725; NS 16.67% x 0.99 - 8.79% x 0.0495 = 0.16068195; contributions
  0.0495 + 0.01: 0.4160 (0.41595445 rounded).
- 2025, $200,000 (no contributions; fifth bracket 21%): federal 29% + 14.5% x 1,591 / 75,532
  (0.0210639 to seven places) = 0.2930542655; NS 0.21: 0.5030542655.
- 2026, $28,000: federal 14% x 0.99 - 14% x 0.0658 = 0.129388; NS 8.79% x 0.99 - 8.79% x 0.0658 =
  0.08123718; contributions 0.0758: 0.28642518.
- 2026, $70,000 (over the EI maximum of $68,900): federal 20.5% x 0.99 - 14% x 0.0495 = 0.19602; NS
  0.16068195; contributions 0.0595: 0.41620195.

The age amount (NS428 line 10, Worksheet NS428 "Line 58080 - Age amount") of a filer born in 1960 or
earlier falls by line 5 "Applicable rate 15%" of the net income over the threshold of 30,828 (line
4), and every dollar of that fall is tax at the Nova Scotia credit rate (NS428 line 47, 8.79%), so
a further dollar of salary adds

    15% x N x 8.79% = 0.01305315 (N = 0.99 in 2025 for a filer who pays CPP; 0.013185 where N = 1)

to the Nova Scotia part while the net income is over the threshold and an age amount is still
claimed, and nothing otherwise (a filer under 65 or with no birth year claims none). In 2026 a filer
born in 1955 is past 70 and pays no CPP, so N = 1, the contribution rate is the EI rate of 1.63%
alone and the net income is the salary. The salaries are worked back from the net income wanted:
net income = salary less 1% of the salary over 3,500 (the enhanced CPP, rounded to the cent). The
cases for a filer born in 1955 are:

- 2025, 14.95% bracket (taxable income from 30,507 to 61,015), CPP 4.95% + 1% and EI 1.64%:
  14.95% x 0.99 - 8.79% x 0.0659 = 0.14221239, plus the age term 0.01305315: 0.15526554.
- 2025, 16.67% bracket, over the EI maximum (CPP base 4.95% only): 16.67% x 0.99 - 8.79% x 0.0495
  = 0.16068195, plus the age term: 0.1737351.
- 2026, 8.79% bracket (to 30,995): 8.79% - 8.79% x 0.0163 = 0.08646723.
- 2026, 14.95% bracket (to 61,991): 14.95% - 8.79% x 0.0163 = 0.14806723, plus 0.013185: 0.16125223.
- 2026, 16.67% bracket, over the EI maximum of 68,900 (no contribution): 0.1667, plus 0.013185:
  0.179885.

The engine rounds the marginal rate half-up to 0.0001 like the average rate
(`ca/take_home_average_rate_rounding`), so the expected values in the parametrization are the exact
sums derived above rounded half-up to four places (e.g. 0.29112289 is 0.2911).
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
NOVA_SCOTIA = JurisdictionCode("CA-NS")


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
        (2025, "15000", "0.0759"),
        (2025, "18000", "0.2066"),
        (2025, "28000", "0.2911"),
        (2025, "40000", "0.3521"),
        (2025, "70000", "0.4160"),
        (2025, "200000", "0.5031"),
        (2026, "2000", "1"),
        (2026, "2000.01", "1"),
        (2026, "3500", "0.0758"),
        (2026, "3500.01", "0.0758"),
        (2026, "28000", "0.2864"),
        (2026, "70000", "0.4162"),
    ],
)
def test_the_marginal_rate_is_the_sum_of_the_rates_that_apply_rounded_to_four_decimals(
    year: int, salary: str, rate: str
) -> None:
    worksheets = build_tax_computation().compute(
        TaxCalculationRequest(NOVA_SCOTIA, year, (Artifact(EMPLOYMENT_INCOME, D(salary)),))
    )
    (summary,) = worksheets["ca-ns/return"]

    assert summary.get(bundled_kinds().kind("ca-ns/marginal_tax_rate")).value == D(rate)


# Year, salary, age term and Nova Scotia marginal rate for a filer born in 1955, worked above.
BORN_1955_VALUES = [
    # 2025: net income = salary less 1% of the salary over 3,500.
    (2025, "0", "0", "0"),
    (2025, "31104.04", "0", "0.14221239"),
    (2025, "31104.05", "0.01305315", "0.15526554"),
    (2025, "31105.05", "0.01305315", "0.15526554"),
    (2025, "40000", "0.01305315", "0.15526554"),
    (2025, "69716.80", "0.01305315", "0.1737351"),
    (2025, "69716.81", "0", "0.16068195"),
    # 2026: no CPP, so net income = salary.
    (2026, "0", "0", "0"),
    (2026, "30828", "0", "0.08646723"),
    (2026, "30828.01", "0.013185", "0.09965223"),
    (2026, "30829", "0.013185", "0.09965223"),
    (2026, "40000", "0.013185", "0.16125223"),
    (2026, "60000", "0.013185", "0.16125223"),
    (2026, "69667.96", "0.013185", "0.179885"),
    (2026, "69667.97", "0", "0.1667"),
]


def _age_summary(year: int, salary: str, born: int | None) -> Worksheet:
    extra = () if born is None else (Artifact(BIRTH_YEAR, born),)
    worksheets = build_tax_computation().compute(
        TaxCalculationRequest(NOVA_SCOTIA, year, (Artifact(EMPLOYMENT_INCOME, D(salary)), *extra))
    )
    (summary,) = worksheets["ca-ns/return"]
    return summary


def _age_value(sheet: Worksheet, name: str) -> Decimal:
    value = sheet.get(bundled_kinds().kind(name)).value
    assert isinstance(value, Decimal)
    return value


@pytest.mark.parametrize(("year", "salary", "term", "provincial"), BORN_1955_VALUES)
def test_born_1955_the_age_term_and_the_nova_scotia_part_are_the_worked_rates(
    year: int, salary: str, term: str, provincial: str
) -> None:
    summary = _age_summary(year, salary, 1955)

    assert _age_value(summary, "ca-ns/marginal_age_rate") == D("0.15")
    assert _age_value(summary, "ca-ns/marginal_nova_scotia_age_credit_rate") == D(term)
    assert _age_value(summary, "ca-ns/nova_scotia_marginal_rate") == D(provincial)


@pytest.mark.parametrize(
    ("year", "salary", "provincial"),
    [
        (2025, "0", "0"),
        (2025, "31104.04", "0.14221239"),
        (2025, "31104.05", "0.14221239"),
        (2025, "31105.05", "0.14221239"),
        (2025, "40000", "0.14221239"),
        (2025, "69716.80", "0.16068195"),
        (2025, "69716.81", "0.16068195"),
        (2026, "0", "0"),
        # 14.95% x 0.99 - 8.79% x 0.0658 = 0.148005 - 0.00578382.
        (2026, "40000", "0.14222118"),
    ],
)
@pytest.mark.parametrize("born", [1980, None])
def test_born_1980_or_with_no_birth_year_the_age_amount_never_changes_the_rate(
    born: int | None, year: int, salary: str, provincial: str
) -> None:
    # A filer under 65 (or with no birth year) claims no age amount: the amount gate is shut
    # although the net income is over the threshold, and the Nova Scotia part is the bracket rate
    # after the CPP and EI credits alone.
    summary = _age_summary(year, salary, born)

    assert _age_value(summary, "ca-ns/marginal_age_amount_claimed") == D("0")
    assert _age_value(summary, "ca-ns/marginal_age_amount_gate") == D("0")
    assert _age_value(summary, "ca-ns/marginal_nova_scotia_age_credit_rate") == D("0")
    assert _age_value(summary, "ca-ns/nova_scotia_marginal_rate") == D(provincial)


@pytest.mark.parametrize(
    ("year", "salary", "born", "marginal"),
    [
        # Below the federal age threshold the federal part is the bracket rate alone: 2025,
        # 14.5% x 0.99 - 14.5% x 0.0659 = 0.1339945 with contributions of 0.0759.
        (2025, "31104.04", 1955, "0.3521"),  # 0.1339945 + 0.14221239 + 0.0759
        (2025, "31104.04", 1980, "0.3521"),
        (2025, "31104.05", 1955, "0.3652"),  # 0.1339945 + 0.15526554 + 0.0759
        (2025, "31104.05", 1980, "0.3521"),
        (2025, "40000", 1955, "0.3652"),
        (2025, "40000", 1980, "0.3521"),
        # 2026, born 1955: no CPP, federal 14% - 14% x 0.0163 = 0.137718, EI 0.0163.
        (2026, "30828", 1955, "0.2405"),  # 0.137718 + 0.08646723 + 0.0163
        (2026, "30828.01", 1955, "0.2537"),  # 0.137718 + 0.09965223 + 0.0163
        (2026, "40000", 1955, "0.3153"),  # 0.137718 + 0.16125223 + 0.0163
        # 2026, born 1980: federal 14% x 0.99 - 14% x 0.0658 = 0.129388, contributions 0.0758.
        (2026, "40000", 1980, "0.3474"),  # 0.129388 + 0.14222118 + 0.0758
    ],
)
def test_the_total_marginal_rate_below_the_federal_age_threshold(
    year: int, salary: str, born: int, marginal: str
) -> None:
    assert _age_value(_age_summary(year, salary, born), "ca-ns/marginal_tax_rate") == D(marginal)
