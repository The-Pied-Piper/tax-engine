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

import pytest

from tax_engine import build_tax_computation
from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
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
