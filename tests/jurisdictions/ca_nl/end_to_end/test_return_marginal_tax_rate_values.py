"""The Newfoundland and Labrador marginal rate at a few salaries, worked by hand.

Each figure is worked from the printed rates.

The marginal rate (`ca-nl/marginal_tax_rate`) is the extra take-home deductions on a further dollar
of salary, for a salary-only filer: the federal and Newfoundland and Labrador income tax rates and
the CPP, CPP2 and EI rates. Each figure below is the exact sum of its parts, and the parts are the
printed rates (T1 "Line 73: Rate", NL428 "Line 5: Rate" and "Line 12: Rate", NL428 line 102
"Applicable rate 16%", Schedule 8 lines 11, 12 and 22, T2204 lines 10 and 16),
with the net income rate N = 1 - enhanced CPP rate - CPP2 rate (T1 line 22215 takes the enhanced
and the second additional contributions off the income) and the credits at the federal and the
Newfoundland and Labrador credit rate on the CPP base and EI rates:

    federal  = bracket rate x N + BPA phase-down - federal credit rate x (CPP base + EI)
    NL       = bracket rate x N - NL credit rate x (CPP base + EI)  (+ 16% x N while the low-income
               tax reduction is phased out), and 0 where the reduction absorbs the tax
    marginal = federal + NL + CPP base + CPP enhanced + CPP2 + EI

The check against an extra run of the engine is in `test_return_marginal_tax_rate_extra_run.py`.

- 2025, $10,000: CPP 4.95% + 1% and EI 1.64% = 0.0759; no income tax.
- 2025, $20,000: federal 14.5% x 0.99 - 14.5% x 0.0659 = 0.1339945; Newfoundland and Labrador 0
  (the low-income reduction of $997 is more than the tax); contributions 0.0759: 0.2098945.
- 2025, $28,000 (net income 27,755, over the low-income threshold of 23,928 and the reduction left
  is positive): NL 8.7% x 0.99 - 8.7% x 0.0659 + 16% x 0.99 = 0.2387967; federal 0.1339945;
  contributions 0.0759: 0.4486912.
- 2025, $40,000 (the reduction is gone): NL 0.0803967: 0.2902912.
- 2025, $70,000 (over the EI maximum of $65,700): federal 20.5% x 0.99 - 14.5% x 0.0495 =
  0.1957725; NL 14.5% x 0.99 - 8.7% x 0.0495 = 0.1392435; contributions 0.0495 + 0.01: 0.394516.
- 2025, $200,000 and $250,000 (no contributions): federal 29% + 14.5% x 1,591 / 75,532 (0.0210639
  to seven places) = 0.2930542655; NL 17.8% (line 5) or 19.8% (line 12): 0.4710542655 and
  0.4910542655.
- 2026, $40,000: federal 14% x 0.99 - 14% x 0.0658 = 0.129388; NL 0.0804054; contributions 0.0758:
  0.2855934.
- 2026, $70,000 (over the EI maximum of $68,900): federal 20.5% x 0.99 - 14% x 0.0495 = 0.19602;
  NL 0.1392435; contributions 0.0595: 0.3947635.

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
NEWFOUNDLAND = JurisdictionCode("CA-NL")


@pytest.mark.parametrize(
    ("year", "salary", "rate"),
    [
        (2025, "0", "0"),
        (2025, "2020", "1"),
        (2025, "2000", "0"),
        (2025, "2000.01", "1"),
        (2025, "3500", "0.0164"),
        (2025, "3500.01", "0.0759"),
        (2025, "10000", "0.0759"),
        (2025, "20000", "0.2099"),
        (2025, "28000", "0.4487"),
        (2025, "40000", "0.2903"),
        (2025, "70000", "0.3945"),
        (2025, "200000", "0.4711"),
        (2025, "250000", "0.4911"),
        (2026, "2000", "0"),
        (2026, "2000.01", "1"),
        (2026, "3500", "0.0163"),
        (2026, "3500.01", "0.0758"),
        (2026, "40000", "0.2856"),
        (2026, "70000", "0.3948"),
    ],
)
def test_the_marginal_rate_is_the_exact_sum_of_the_rates_that_apply(
    year: int, salary: str, rate: str
) -> None:
    worksheets = build_tax_computation().compute(
        TaxCalculationRequest(NEWFOUNDLAND, year, (Artifact(EMPLOYMENT_INCOME, D(salary)),))
    )
    (summary,) = worksheets["ca-nl/return"]

    assert summary.get(bundled_kinds().kind("ca-nl/marginal_tax_rate")).value == D(rate)
