"""The Alberta marginal rate at a few salaries, worked by hand from the printed rates.

The marginal rate (`ca-ab/marginal_tax_rate`) is the extra take-home deductions on a further dollar
of salary, for a salary-only filer with no paid credits. Each figure below is the exact sum of its
parts, and the parts are the printed rates (T1 "Line 73: Rate", AB428 "Line 5: Rate", "Line 12:
Rate" and "Line 53: Alberta non-refundable tax credit rate 8%", Schedule 8 lines 11, 12 and 22,
T2204 lines 10 and 16), with the net income rate N = 1 - enhanced CPP rate - CPP2 rate, because T1
line 22215 takes the enhanced and the second additional contributions off the income, and the
credits at the federal and the Alberta credit rate on the CPP base and EI rates:

    federal  = bracket rate x N + BPA phase-down - federal credit rate x (CPP base + EI)
    Alberta  = bracket rate x N - 8% x (CPP base + EI), counted where AB428 line 68 is above 0
               (Alberta has no tax reduction, surtax or health premium)
    marginal = federal + Alberta + CPP base + CPP enhanced + CPP2 + EI

The engine rounds the marginal rate half-up to 0.0001 like the average rate
(`ca/take_home_average_rate_rounding`), so each expected marginal rate in the tests is the exact
figure derived in the comments rounded half-up to four decimals; the parts stay exact.

The extra-run check over a sweep is in `test_return_marginal_tax_rate_extra_run.py`.

- $100: nothing moves (under the CPP exemption and the EI $2,000): 0.
- $2,001: only the EI of T2204 line 16 moves, 1 for 1 between $2,000 and $2,033: 1.
- $2,000 and $3,500, both years (exact band edges): a rate is 0 on either edge of its band (the
  federal form's rule), so the EI rate is 0 at $2,000 and the CPP rate 0 at $3,500 ($3,500 has the
  EI rate only: 1.64% in 2025, 1.63% in 2026), and the next cent is in the next band (1; then CPP
  4.95% + 1% and EI).
- 2025, $71,300 (the CPP maximum pensionable earnings, where the CPP base ends and the CPP2 band
  starts): both are edges, so neither rate counts: 20.5% + 10% = 0.305; a cent more earns CPP2 at
  4% and no CPP base: 0.3328 (N = 0.96: 20.5% x 0.96 + 10% x 0.96 + 4%).
- 2025, $20,000: federal 14.5% x 0.99 - 14.5% x 0.0659 = 0.1339945; Alberta line 68 is 0.00 (the
  credits are over the tax), so 0; contributions 0.0759: 0.2098945. At $23,931.13 line 68 is first
  0.01, and the Alberta part 8% x 0.99 - 8% x 0.0659 = 0.073928 counts.
- 2025, $70,000 (over the EI maximum): federal 20.5% x 0.99 - 14.5% x 0.0495 = 0.1957725; Alberta
  10% x 0.99 - 8% x 0.0495 = 0.09504; contributions 0.0495 + 0.01: 0.3503125.
- $120,000 and $160,000 (no contributions): the bracket rates alone, 26% + 10% and 26% + 12%.
- 2025, $200,000: the federal basic personal amount falls over $177,882 to $253,414 (T1 line 77,
  Federal Worksheet lines 2, 6 and 8): 29% + 14.5% x 1,591 / 75,532 (0.0210639 to seven places) =
  0.2930542655; Alberta 13% (AB428 line 12): 0.4230542655.
- 2026, $70,000: federal 20.5% x 0.99 - 14% x 0.0495 = 0.19602; Alberta 0.09504; 0.0595: 0.35056.
- 2026, $200,000: 29% + 14% x 1,623 / 77,042 (0.0210664 to seven places) = 0.292949296; Alberta
  13%: 0.422949296.
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
ALBERTA = JurisdictionCode("CA-AB")


@pytest.mark.parametrize(
    ("year", "salary", "rate"),
    [
        (2025, "100", "0"),
        (2026, "100", "0"),
        (2025, "2000", "0"),
        (2025, "2000.01", "1"),
        (2026, "2000", "0"),
        (2026, "2000.01", "1"),
        (2025, "3500", "0.0164"),
        (2025, "3500.01", "0.0759"),
        (2025, "71300", "0.305"),
        (2025, "71300.01", "0.3328"),
        (2026, "3500", "0.0163"),
        (2026, "3500.01", "0.0758"),
        (2025, "20000", "0.2099"),
        (2026, "20000", "0.2052"),
        (2025, "70000", "0.3503"),
        (2026, "70000", "0.3506"),
        (2025, "120000", "0.36"),
        (2026, "120000", "0.36"),
        (2025, "160000", "0.38"),
        (2026, "160000", "0.38"),
        (2025, "200000", "0.4231"),
        (2026, "200000", "0.4229"),
    ],
)
def test_the_marginal_rate_is_the_exact_sum_of_the_rates_that_apply(
    year: int, salary: str, rate: str
) -> None:
    worksheets = build_tax_computation().compute(
        TaxCalculationRequest(ALBERTA, year, (Artifact(EMPLOYMENT_INCOME, D(salary)),))
    )
    (summary,) = worksheets["ca-ab/return"]

    assert summary.get(bundled_kinds().kind("ca-ab/marginal_tax_rate")).value == D(rate)
