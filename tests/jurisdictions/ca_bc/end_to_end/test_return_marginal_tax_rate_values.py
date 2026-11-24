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
not published, and the 2026 datasets follow the July 2026 payroll rates or are carried forward. The extra-run check over a sweep is in
`test_return_marginal_tax_rate_extra_run.py`, the gates in
`test_return_marginal_tax_rate_gates.py`.

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
BRITISH_COLUMBIA = JurisdictionCode("CA-BC")


@pytest.mark.parametrize(
    ("year", "salary", "rate"),
    [
        (2025, "0", "0"),
        (2025, "2020", "1"),
        (2025, "10000", "0.0759"),
        (2025, "20000", "0.2098945"),
        (2025, "30000", "0.29189796"),
        (2025, "45000", "0.25665396"),
        (2025, "70000", "0.3289978"),
        (2025, "75000", "0.31072"),
        (2025, "100000", "0.31"),
        (2025, "120000", "0.3829"),
        (2025, "150000", "0.407"),
        (2025, "200000", "0.4610542655"),
        (2026, "10000", "0.0758"),
        (2026, "30000", "0.2921872"),
        (2026, "70000", "0.328978"),
        (2026, "250000", "0.460949296"),
    ],
)
def test_the_marginal_rate_is_the_exact_sum_of_the_rates_that_apply(
    year: int, salary: str, rate: str
) -> None:
    worksheets = build_tax_computation().compute(
        TaxCalculationRequest(BRITISH_COLUMBIA, year, (Artifact(EMPLOYMENT_INCOME, D(salary)),))
    )
    (summary,) = worksheets["ca-bc/return"]

    assert summary.get(bundled_kinds().kind("ca-bc/marginal_tax_rate")).value == D(rate)
