"""The Saskatchewan marginal rate at a few salaries, worked by hand from the printed rates.

The marginal rate (`ca-sk/marginal_tax_rate`) is the extra take-home deductions on a further dollar
of salary, for a salary-only filer with no paid credits. Each figure below is the exact sum of its
parts, and the parts are the printed rates (T1 "Line 73: Rate", SK428 "Line 5: Rate" and "Line 52:
Saskatchewan non-refundable tax credit rate 10.5%", Schedule 8 lines 11, 12 and 22, T2204 lines 10
and 16), with the net income rate N = 1 - enhanced CPP rate - CPP2 rate, because T1 line 22215
takes the enhanced and the second additional contributions off the income, and the credits at the
federal and the Saskatchewan credit rate on the CPP base and EI rates:

    federal       = bracket rate x N + BPA phase-down - federal credit rate x (CPP base + EI)
    Saskatchewan  = bracket rate x N - 10.5% x (CPP base + EI), counted where SK428 line 67 is
                    above 0 (Saskatchewan has no tax reduction, surtax or health premium)
    marginal      = federal + Saskatchewan + CPP base + CPP enhanced + CPP2 + EI

The extra-run check over a sweep is in `test_return_marginal_tax_rate_extra_run.py`.

- 2025, $100: nothing moves (under the CPP exemption and the EI $2,000): 0.
- 2025, $2,020: only the EI of T2204 line 16 moves, 1 for 1 between $2,000 and $2,033: 1.
- $2,000 and $3,500, both years (exact band edges): the rate at the edge is the lower band's (the
  EI rate is 0 at $2,000, the CPP rate 0 at $3,500, so $3,500 has the EI rate only: 1.64% in
  2025, 1.63% in 2026) and the next cent is in the next band (1; then CPP 4.95% + 1% and EI).
- 2025, $10,000: CPP 4.95% + 1% and EI 1.64% = 0.0759; no income tax.
- 2025, $20,000: federal 14.5% x 0.99 - 14.5% x 0.0659 = 0.1339945; Saskatchewan line 67 is 0.00
  (the credits are over the tax), so 0; contributions 0.0759: 0.2098945. At $20,866.58 line 67 is
  first 0.01, and the Saskatchewan part 10.5% x 0.99 - 10.5% x 0.0659 = 0.0970305 counts.
- 2025, $50,000: federal 0.1339945; Saskatchewan 0.0970305; contributions 0.0759: 0.306925.
- 2025, $70,000 (over the EI maximum of $65,700): federal 20.5% x 0.99 - 14.5% x 0.0495 =
  0.1957725; Saskatchewan 12.5% x 0.99 - 10.5% x 0.0495 = 0.1185525; contributions 0.0495 + 0.01:
  0.373825.
- 2025, $75,000 (CPP2 band, no CPP base or EI): N = 0.96; federal 20.5% x 0.96 = 0.1968;
  Saskatchewan 12.5% x 0.96 = 0.12; contributions 0.04: 0.3568.
- 2025, $120,000: no contributions; federal 26%, Saskatchewan 12.5%: 0.385.
- 2025, $200,000: the federal basic personal amount falls over $177,882 to $253,414 (T1 line 77,
  Federal Worksheet lines 2, 6 and 8): 29% + 14.5% x 1,591 / 75,532 (0.0210639 to seven places)
  = 0.2930542655; Saskatchewan 14.5%: 0.4380542655.
- 2026, $21,827.32: Saskatchewan 10.5% x 0.99 - 10.5% x 0.0658 = 0.097041 (EI is 1.63%).
- 2026, $10,000: CPP 4.95% + 1% and EI 1.63%: 0.0758.
- 2026, $70,000 (over the EI maximum of $68,900): federal 20.5% x 0.99 - 14% x 0.0495 = 0.19602;
  Saskatchewan 0.1185525; contributions 0.0595: 0.3740725.
- 2026, $200,000: 29% + 14% x 1,623 / 77,042 (0.0210664 to seven places) = 0.292949296;
  Saskatchewan 14.5%: 0.437949296.

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
SASKATCHEWAN = JurisdictionCode("CA-SK")


@pytest.mark.parametrize(
    ("year", "salary", "rate"),
    [
        (2025, "100", "0"),
        (2025, "2020", "1"),
        (2025, "2000", "0"),
        (2025, "2000.01", "1"),
        (2025, "3500", "0.0164"),
        (2025, "3500.01", "0.0759"),
        (2025, "10000", "0.0759"),
        (2025, "20000", "0.2099"),
        (2025, "20866.57", "0.2099"),
        (2025, "20866.58", "0.3069"),
        (2025, "50000", "0.3069"),
        (2025, "70000", "0.3738"),
        (2025, "75000", "0.3568"),
        (2025, "120000", "0.385"),
        (2025, "200000", "0.4381"),
        (2026, "2000", "0"),
        (2026, "2000.01", "1"),
        (2026, "3500", "0.0163"),
        (2026, "3500.01", "0.0758"),
        (2026, "10000", "0.0758"),
        (2026, "70000", "0.3741"),
        (2026, "200000", "0.4379"),
    ],
)
def test_the_marginal_rate_is_the_exact_sum_of_the_rates_that_apply(
    year: int, salary: str, rate: str
) -> None:
    worksheets = build_tax_computation().compute(
        TaxCalculationRequest(SASKATCHEWAN, year, (Artifact(EMPLOYMENT_INCOME, D(salary)),))
    )
    (summary,) = worksheets["ca-sk/return"]

    assert summary.get(bundled_kinds().kind("ca-sk/marginal_tax_rate")).value == D(rate)
