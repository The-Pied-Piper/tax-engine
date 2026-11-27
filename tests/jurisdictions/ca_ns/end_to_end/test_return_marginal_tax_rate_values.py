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
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
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
