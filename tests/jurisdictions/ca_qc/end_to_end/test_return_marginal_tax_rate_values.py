"""The Quebec marginal rate at a few salaries, worked by hand from the printed rates.

The marginal rate (`ca-qc/marginal_tax_rate`) is the extra take-home deductions on a further dollar
of salary: the federal tax (5005-R line 43500, less the refundable Quebec abatement of line 44000,
which is 16.5% of the basic federal tax), the Quebec tax (TP-1
line 450, with the prescription drug insurance premium), and the QPP, QPP2, EI and QPIP rates, for
a salary-only filer. The parts are the printed rates (5005-R "Line 74: Rate", Work Chart 401 line
5, Work Chart 201 line 9, TP-1 Schedule K line 80, Schedule 8 lines 11, 12 and 22, T2204 lines 10
and 16, Schedule 10 line 16), with the part of a salary dollar left in the net income
N = 1 - QPP first additional rate - QPP second additional rate (5005-R line 22215 and TP-1 line 248
take those contributions off the income) and T = N - 6% while the deduction for workers is under
its $1,420 maximum:

    federal  = (bracket rate x N + BPA phase-down - 14.5% x (QPP base + EI + QPIP)) x (1 - 16.5%),
               0 where no federal tax is paid
    Quebec   = Work Chart 401 rate x T, 0 where no Quebec tax is paid
    premium  = Schedule K line 80 rate x T, from a premium income of one cent to the $755 maximum
    marginal = federal + Quebec + premium + QPP base + QPP first additional + QPP2 + EI + QPIP

The engine rounds the marginal rate half-up to 0.0001 like the average rate
(`ca/take_home_average_rate_rounding`), so each hand-derived exact sum below is stated rounded
half-up to four decimals in the test table (the exact sum stays in the worked lines).

The extra-run check over a sweep is in `test_return_marginal_tax_rate_extra_run.py`.

- 2025, $10,000: no income tax; QPP 5.4% + 1%, EI 1.31%, QPIP 0.494%: 0.08204.
- 2025, $22,000: federal 0.1331042 x 0.835 = 0.1111420; Quebec 14% x 0.93 = 0.1302; the premium
  row 7.84% x 0.93 = 0.072912; contributions 0.08204: 0.3962940.
- 2025, $40,000: federal 0.1111420; Quebec 14% x 0.99 (T = 0.99, the deduction for workers is at
  its maximum) = 0.1386; the premium is at its maximum, 0; contributions 0.08204: 0.3317820.
- 2025, $70,000 (over the EI maximum): federal (20.5% x 0.99 - 14.5% x (0.054 + 0.00494)) x 0.835 =
  0.1944037 x 0.835 = 0.1623271; Quebec 19% x 0.99 = 0.1881; contributions 0.054 + 0.01 +
  0.00494: 0.4193671.
- 2025, $75,000 (QPP2 band, no QPP base or EI): N = 0.96; federal (20.5% x 0.96 - 14.5% x 0.00494)
  x 0.835 = 0.1960837 x 0.835 = 0.1637299; Quebec 19% x 0.96; contributions 0.04 + 0.00494:
  0.3910699.
- 2025, $120,000: over the QPIP maximum, no contributions; federal 26% x 0.835 = 0.2171, Quebec
  24%: 0.4571.
- 2025, $200,000: the federal basic personal amount falls over $177,882 to $253,414: (29% + 14.5% x
  (1,591 / 75,532, which is 0.0210639 to seven places)) x 0.835 = 0.2447004, Quebec 25.75%:
  0.5022004.
- 2025, $300,000: federal 33% x 0.835 = 0.27555, Quebec 25.75%: 0.53305,
  which rounds half-up to 0.5331.
- 2026, $10,000, $70,000 and $200,000: the same parts with the 2026 datasets (provisional).
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
QUEBEC = JurisdictionCode("CA-QC")


@pytest.mark.parametrize(
    ("year", "salary", "rate"),
    [
        (2025, "10000", "0.0820"),
        (2025, "22000", "0.3963"),
        (2025, "40000", "0.3318"),
        (2025, "70000", "0.4194"),
        (2025, "75000", "0.3911"),
        (2025, "120000", "0.4571"),
        (2025, "200000", "0.5022"),
        (2025, "300000", "0.5331"),
        (2026, "10000", "0.0803"),
        (2026, "70000", "0.4182"),
        (2026, "200000", "0.5021"),
    ],
)
def test_the_marginal_rate_is_the_sum_of_the_rates_that_apply_rounded_to_four_decimals(
    year: int, salary: str, rate: str
) -> None:
    worksheets = build_tax_computation().compute(
        TaxCalculationRequest(QUEBEC, year, (Artifact(EMPLOYMENT_INCOME, D(salary)),))
    )
    (summary,) = worksheets["ca-qc/return"]

    assert summary.get(bundled_kinds().kind("ca-qc/marginal_tax_rate")).value == D(rate)
