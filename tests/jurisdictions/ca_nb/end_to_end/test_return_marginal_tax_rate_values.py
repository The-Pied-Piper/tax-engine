"""The New Brunswick marginal rate at a few salaries, worked by hand.

Each figure is worked from the printed rates.

The marginal rate (`ca-nb/marginal_tax_rate`) is the extra take-home deductions on a further dollar
of salary, for a salary-only filer: the federal and New Brunswick income tax rates and the CPP, CPP2
and EI rates. Each figure below is the exact sum of its parts, and the parts are the printed rates
(T1 "Line 73: Rate", NB428 "Line 5: Rate", NB428 line 84 "3%", Schedule 8 lines 11, 12 and 22, T2204
lines 10 and 16), with the net income rate N = 1 - enhanced CPP rate - CPP2 rate (T1 line 22215
takes the enhanced and the second additional contributions off the income) and the credits at the
federal and the New Brunswick credit rate on the CPP base and EI rates:

    federal  = bracket rate x N + BPA phase-down - federal credit rate x (CPP base + EI)
    NB       = bracket rate x N - NB credit rate x (CPP base + EI)  (+ 3% x N while the low-income
               tax reduction is phased out), and 0 where the reduction absorbs the tax
    marginal = federal + NB + CPP base + CPP enhanced + CPP2 + EI

A filer born in 1960 or earlier (1961 or earlier for 2026) has the age amount (T1 line 30100 and
NB428 line 10), which falls by 15% of each dollar of net income over its threshold (printed rate,
Worksheet "Line 58080 - Age amount" line 5) until it is 0, so each such dollar adds the credit
rate times 15% to the tax. The fall is counted only while worksheet line 4 (the net income over the
threshold) and the age amount claimed are both above zero:

    federal  += 15% x N x federal credit rate   (threshold 45,522 and maximum 9,028 in 2025;
                                                 46,432 and 9,209 in 2026)
    NB       += 15% x N x 9.4%                  (threshold 44,945 and maximum 6,037 in 2025;
                                                 45,844 and 6,158 in 2026)

The check against an extra run of the engine is in `test_return_marginal_tax_rate_extra_run.py`.

- 2025, $10,000: CPP 4.95% + 1% and EI 1.64% = 0.0759; no income tax.
- 2025, $20,000: federal 14.5% x 0.99 - 14.5% x 0.0659 = 0.1339945; New Brunswick 0 (the
  low-income reduction of $802 is more than the tax of $497.66); contributions 0.0759: 0.2098945.
- 2025, $28,000 and $40,000 (net income 27,755 and 39,635, over the base amount of 21,920 and under
  the single income limit of 48,653, the reduction left is positive): NB 9.4% x 0.99 - 9.4% x
  0.0659 + 3% x 0.99 = 0.1165654; federal 0.1339945; contributions 0.0759: 0.3264599.
- 2025, $70,000 (over the EI maximum of $65,700; the net income is over the 14% column's start of
  51,306): federal 20.5% x 0.99 - 14.5% x 0.0495 = 0.1957725; NB 14% x 0.99 - 9.4% x 0.0495 =
  0.133947; contributions 0.0495 + 0.01: 0.3892195.
- 2025, $200,000 and $250,000 (no contributions): federal 29% + 14.5% x 1,591 / 75,532 (0.0210639
  to seven places) = 0.2930542655; NB 19.5% (line 5): 0.4880542655.
- 2026, $40,000: federal 14% x 0.99 - 14% x 0.0658 = 0.129388; NB 9.4% x 0.99 - 9.4% x 0.0658 + 3%
  x 0.99 = 0.1165748; contributions 0.0758: 0.3217628.
- 2026, $70,000 (over the EI maximum of $68,900): federal 20.5% x 0.99 - 14% x 0.0495 = 0.19602;
  NB 14% x 0.99 - 9.4% x 0.0495 = 0.133947; contributions 0.0595: 0.389467.

The engine rounds the marginal rate half-up to 0.0001 like the average rate
(`ca/take_home_average_rate_rounding`), so the expected values in the parametrization are the exact
sums derived below rounded half-up to four places (e.g. 0.2098945 is 0.2099).
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import pytest

from tax_engine import build_tax_computation
from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca.catalog.personal_amounts import BIRTH_YEAR
from tests.kinds import bundled_kinds

D = Decimal
NEW_BRUNSWICK = JurisdictionCode("CA-NB")


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
        (2025, "20000", "0.2099"),
        (2025, "28000", "0.3265"),
        (2025, "40000", "0.3265"),
        (2025, "70000", "0.3892"),
        (2025, "200000", "0.4881"),
        (2025, "250000", "0.4881"),
        (2026, "2000", "1"),
        (2026, "2000.01", "1"),
        (2026, "3500", "0.0758"),
        (2026, "3500.01", "0.0758"),
        (2026, "40000", "0.3218"),
        (2026, "70000", "0.3895"),
    ],
)
def test_the_marginal_rate_is_the_sum_of_the_rates_that_apply_rounded_to_four_decimals(
    year: int, salary: str, rate: str
) -> None:
    worksheets = build_tax_computation().compute(
        TaxCalculationRequest(NEW_BRUNSWICK, year, (Artifact(EMPLOYMENT_INCOME, D(salary)),))
    )
    (summary,) = worksheets["ca-nb/return"]

    assert summary.get(bundled_kinds().kind("ca-nb/marginal_tax_rate")).value == D(rate)


# The age amount, born 1955 (a filer who has the age amount), against born 1980 and no birth year
# (who do not). For 2025 the filer born in 1955 is 70 and still pays CPP, so the net income is the
# salary less 1% of the salary over 3,500 (the enhanced CPP deduction, 1,074 with the CPP2 deduction
# of 396 once the salary is over 81,200), N = 0.99 under 71,300 and 1 over it. For 2026 the filer is
# 71, pays no CPP, so N = 1, the net income is the salary and only EI (1.63% to 68,900) is a
# contribution. Each figure is worked from the printed rates:
#
# - 2025, 1955, $45,363.64 (net income 44,945.00, line 4 is 0.00, no fall): federal 0.1339945 + NB
#   0.1165654 (14.5% x 0.99 - 14.5% x 0.0659; 9.4% x 0.99 - 9.4% x 0.0659 + 3% x 0.99) + 0.0759 =
#   0.3264599. At $45,363.65 (net income 44,945.01, line 4 is 0.01): + NB 15% x 0.99 x 9.4% =
#   0.013959, federal still has none (its threshold is 45,522): 0.3404189.
# - 2025, 1955, $50,000 (net income 49,535, line 4 is 4,590, the low-income reduction is over):
#   federal 0.1339945 + 15% x 0.99 x 14.5% (0.0215325) = 0.155527; NB 9.4% x 0.99 - 9.4% x 0.0659
#   + 0.013959 = 0.1008244; 0.0759: 0.3322514.
# - 2025, 1955, $86,265.63 (net income 85,191.63, line 4 is 40,246.63, 15% of it is 6,036.99, so
#   0.01 is left of the age amount) and $86,265.64 (15% of 40,246.64 is 6,037.00, none left): no
#   contribution, federal 20.5% + 15% x 14.5% = 0.22675 (its amount lasts to 105,708), NB 14% +
#   15% x 9.4% = 0.1541, then 14% alone: 0.38085 and 0.36675.
# - 2026, 1955, $45,844.00 (line 4 is 0.00): federal 14% - 14% x 0.0163 = 0.137718; NB 9.4% - 9.4% x
#   0.0163 + 3% = 0.1224678; EI 0.0163: 0.2764858. At $45,845 (line 4 is 1.00) the NB fall of 15% x
#   9.4% = 0.0141 is added: 0.2905858 (the federal threshold is 46,432).
# - 2026, 1955, $50,000 (the low-income reduction is over): federal 0.137718 + 15% x 14% (0.021) =
#   0.158718; NB 9.4% - 9.4% x 0.0163 + 0.0141 = 0.1065678; 0.0163: 0.2815858. At $60,000 (EI
#   still due; second federal bracket 20.5%, NB 14%): 0.205 - 0.14 x 0.0163 + 0.021 = 0.223718;
#   0.14 - 0.094 x 0.0163 + 0.0141 = 0.1525678; 0.0163: 0.3925858.
# - 2026, 1955, $86,897.29 (net income 86,897.29, line 4 is 41,053.29, 15% of it is 6,157.99, so
#   0.01 is left) and $86,897.30 (15% of 41,053.30 is 6,157.995, which rounds to 6,158.00): no
#   contribution, federal 20.5% + 0.021 = 0.226 either side, NB 14% + 0.0141 = 0.1541, then 14%:
#   0.3801 and 0.366.
# - Born 1980 and no birth year have no age amount, so the gate on it is 0 and the rate is the one
#   without the fall: 2025 $50,000 0.1339945 + 0.0868654 + 0.0759 = 0.2967599; 2025 $86,265.63 (no
#   contribution) 20.5% + 14% = 0.345; 2026 $45,845 0.129388 + 0.1165748 + 0.0758 = 0.3217628 and
#   2026 $60,000 0.20295 - 0.14 x 0.0658 + (0.1386 - 0.094 x 0.0658) + 0.0758 = 0.4019528.
@pytest.mark.parametrize(
    ("year", "birth_year", "salary", "rate"),
    [
        (2025, 1955, "0", "0"),
        (2025, 1955, "45363.64", "0.3265"),
        (2025, 1955, "45363.65", "0.3404"),
        (2025, 1955, "50000", "0.3323"),
        (2025, 1955, "86265.63", "0.3809"),
        (2025, 1955, "86265.64", "0.3668"),
        (2025, 1980, "50000", "0.2968"),
        (2025, None, "50000", "0.2968"),
        (2025, 1980, "86265.63", "0.345"),
        (2025, None, "86265.63", "0.345"),
        (2026, 1955, "0", "0"),
        (2026, 1955, "45844", "0.2765"),
        (2026, 1955, "45845", "0.2906"),
        (2026, 1955, "50000", "0.2816"),
        (2026, 1955, "60000", "0.3926"),
        (2026, 1955, "86897.29", "0.3801"),
        (2026, 1955, "86897.30", "0.366"),
        (2026, 1980, "45845", "0.3218"),
        (2026, None, "45845", "0.3218"),
        (2026, 1980, "60000", "0.402"),
        (2026, None, "60000", "0.402"),
    ],
)
def test_the_marginal_rate_includes_the_fall_of_the_age_amount_for_a_filer_who_has_it(
    year: int, birth_year: int | None, salary: str, rate: str
) -> None:
    given: list[Artifact[Any]] = [Artifact(EMPLOYMENT_INCOME, D(salary))]
    if birth_year is not None:
        given.append(Artifact(BIRTH_YEAR, birth_year))
    worksheets = build_tax_computation().compute(
        TaxCalculationRequest(NEW_BRUNSWICK, year, tuple(given))
    )
    (summary,) = worksheets["ca-nb/return"]

    assert summary.get(bundled_kinds().kind("ca-nb/marginal_tax_rate")).value == D(rate)
