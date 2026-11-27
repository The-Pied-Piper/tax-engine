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
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine import build_tax_computation
from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tests.kinds import bundled_kinds

D = Decimal
PRINCE_EDWARD_ISLAND = JurisdictionCode("CA-PE")


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
