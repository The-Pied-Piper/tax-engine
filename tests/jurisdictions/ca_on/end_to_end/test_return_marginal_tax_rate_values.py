"""The Ontario marginal rate at a few salaries, worked by hand from the printed rates.

The marginal rate (`ca-on/marginal_tax_rate`) is the extra take-home deductions on a further dollar
of salary: the federal and Ontario tax rates, the Ontario health premium slope, and the CPP, CPP2
and EI rates, for a salary-only filer. Each figure below is the exact sum of its parts, and the
parts are the printed rates (T1 "Line 73: Rate", ON428 "Line 5: Rate", the ON428 line 89 chart,
Schedule 8 lines 11, 12 and 22, T2204 lines 10 and 16, ON428-A line 18), with
the net income rate N = 1 - enhanced CPP rate - CPP2 rate, because T1 line 22215 takes the
enhanced and the second additional contributions off the income, and the credits at the federal
and the Ontario credit rate on the CPP base and EI rates:

    federal  = bracket rate x N + BPA phase-down - federal credit rate x (CPP base + EI)
    Ontario  = (bracket rate x N - Ontario credit rate x (CPP base + EI)) x surtax factor
               (+ the LIFT reduction rate x N), and 0 where the LIFT credit absorbs the tax
    premium  = ON428 line 89 chart row rate x N
    marginal = federal + Ontario + premium + CPP base + CPP enhanced + CPP2 + EI

The engine rounds the marginal rate half-up to 0.0001 like the average rate
(`ca/take_home_average_rate_rounding`), so the expected values in the parametrization are the exact
sums derived below rounded half-up to four places (e.g. 0.34335775 is 0.3434).

The extra-run check over a sweep is in `test_return_marginal_tax_rate_extra_run.py`.

- 2025, $2,020: only the EI of T2204 line 16 moves, 1 for 1 between $2,000 and $2,033 (a 100%
  band): 1.
- 2025, $10,000: CPP 4.95% + 1% and EI 1.64% = 0.0759; no income tax (below the basic personal
  amounts).
- 2025, $22,000: federal 14.5% x 0.99 - 14.5% x (0.0495 + 0.0164) = 0.1339945; Ontario 0, the LIFT
  credit ($875) is more than the Ontario tax; premium row 6% x 0.99 = 0.0594; contributions 0.0759:
  0.2692945.
- 2025, $40,000: federal 0.1339945; Ontario 5.05% x 0.99 - 5.05% x 0.0659 = 0.04666705 plus the LIFT
  reduction 5% x 0.99 = 0.0495 (net income is over $32,500): 0.09616705; premium 0 (flat row);
  contributions 0.0759: 0.30606155.
- 2025, $70,000 (over the EI maximum of $65,700): federal 20.5% x 0.99 - 14.5% x 0.0495 =
  0.1957725; Ontario 9.15% x 0.99 - 5.05% x 0.0495 = 0.08808525; premium 0; contributions 0.0495 +
  0.01: 0.34335775.
- 2025, $75,000 (CPP2 band, no CPP base or EI): N = 0.96; federal 20.5% x 0.96 = 0.1968; Ontario
  9.15% x 0.96 = 0.08784; contributions 0.04: 0.32464.
- 2025, $120,000 and $275,000: no contributions; federal 26% or 33%; Ontario 11.16% or 13.16% times
  the surtax factor 1.56: 0.434096 and 0.535296.
- 2025, $200,000: the federal basic personal amount falls over $177,882 to $253,414 (T1 line 77,
  Federal Worksheet lines 2, 6 and 8): 29% + 14.5% x 1,591 / 75,532 (0.0210639 to seven places)
  = 0.2930542655; Ontario 12.16% x 1.56 = 0.189696: 0.4827502655.
- 2026, $10,000: CPP 4.95% + 1%, EI 1.63%: 0.0758.
- 2026, $70,000 (over the EI maximum of $68,900): federal 20.5% x 0.99 - 14% x 0.0495 = 0.19602;
  Ontario 9.15% x 0.99 - 5.05% x 0.0495 = 0.08808525; contributions 0.0595: 0.34360525.
- 2026, $200,000: 29% + 14% x 1,623 / 77,042 (0.0210664 to seven places) = 0.292949296; Ontario
  12.16% x 1.56 = 0.189696: 0.482645296.
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
ONTARIO = JurisdictionCode("CA-ON")


@pytest.mark.parametrize(
    ("year", "salary", "rate"),
    [
        (2025, "2020", "1"),
        (2025, "10000", "0.0759"),
        (2025, "22000", "0.2693"),
        (2025, "40000", "0.3061"),
        (2025, "70000", "0.3434"),
        (2025, "75000", "0.3246"),
        (2025, "120000", "0.4341"),
        (2025, "200000", "0.4828"),
        (2025, "275000", "0.5353"),
        (2026, "10000", "0.0758"),
        (2026, "70000", "0.3436"),
        (2026, "200000", "0.4826"),
    ],
)
def test_the_marginal_rate_is_the_sum_of_the_rates_that_apply_rounded_to_four_decimals(
    year: int, salary: str, rate: str
) -> None:
    worksheets = build_tax_computation().compute(
        TaxCalculationRequest(ONTARIO, year, (Artifact(EMPLOYMENT_INCOME, D(salary)),))
    )
    (summary,) = worksheets["ca-on/return"]

    assert summary.get(bundled_kinds().kind("ca-on/marginal_tax_rate")).value == D(rate)
