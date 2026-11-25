"""The Manitoba marginal rate at salaries from $0 to $410,000, worked by hand from the printed
rates.

The marginal rate (`ca-mb/marginal_tax_rate`) is the extra take-home deductions on a further dollar
of salary, for a salary-only filer with no paid credits. Each figure below is the exact sum of its
parts, and the parts are the printed rates (T1 "Line 73: Rate", Form MB428 "Line 5: Rate" and
"Line 52: Manitoba non-refundable tax credits rate 10.8%", Worksheet MB428 lines 1 to 9, Schedule
MB428-A line 12, Schedule 8 lines 11, 12 and 22, T2204 lines 10 and 16), with the net income rate
N = 1 - enhanced CPP rate - CPP2 rate, because T1 line 22215 takes the enhanced and the second
additional contributions off the income:

    federal   = bracket rate x N + BPA phase-down - federal credit rate x (CPP base + EI)
    Manitoba  = (bracket rate x N + 15,780 / 200,000 x 10.8% between a net income of 200,000.07 and
                399,999.93 + 9% x 10.8% x N while the family tax benefit is above 0)
                - 10.8% x (CPP base + EI), counted where MB428 line 65 is above 0
    marginal  = federal + Manitoba + CPP base + CPP enhanced + CPP2 + EI

The engine rounds the marginal rate half-up to 0.0001 like the average rate
(`ca/take_home_average_rate_rounding`), so each expected rate in the test is the exact figure below
rounded half-up to four decimals.

At 70,000 (2025): federal 20.5% x 0.99 - 14.5% x 0.0495 = 0.1957725; Manitoba 12.75% x 0.99 -
10.8% x 0.0495 = 0.120879; contributions 0.0495 + 0.01 = 0.0595: 0.3761515. At 250,000 (2025):
federal 29% + 14.5% x 1,591 / 75,532 (0.0210639 to seven places) = 0.2930542655; Manitoba 17.4% +
0.85212 points = 0.1825212: 0.4755754655. The extra-run check over a sweep is in
`test_return_marginal_tax_rate_extra_run.py`; the gates are in `..._gates.py` and
`..._gates_2026.py`.

At the exact edge $2,000 the rate is the lower band's (the EI rate is 0). A contribution band reads
its own rate from its lower bound, so at exactly $3,500 the CPP rate already applies: CPP 4.95% +
1% and EI, 0.0759 in 2025 and 0.0758 in 2026, the same as the next cent.
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
MANITOBA = JurisdictionCode("CA-MB")


@pytest.mark.parametrize(
    ("year", "salary", "rate"),
    [
        (2025, "2000", "0"),
        (2025, "2000.01", "1"),
        (2025, "3500", "0.0759"),
        (2025, "3500.01", "0.0759"),
        (2025, "0", "0"),
        (2025, "100", "0"),
        (2025, "17403.90", "0.0759"),
        (2025, "17403.91", "0.1853"),
        (2025, "18820.26", "0.1853"),
        (2025, "18820.27", "0.3193"),
        (2025, "20000", "0.3193"),
        (2025, "50000", "0.329"),
        (2025, "70000", "0.3762"),
        (2025, "150000", "0.434"),
        (2025, "200000", "0.4671"),
        (2025, "201074.06", "0.4671"),
        (2025, "201074.07", "0.4756"),
        (2025, "250000", "0.4756"),
        (2025, "300000", "0.5125"),
        (2025, "401073.93", "0.5125"),
        (2025, "401073.94", "0.504"),
        (2025, "410000", "0.504"),
        (2026, "2000", "0"),
        (2026, "2000.01", "1"),
        (2026, "3500", "0.0758"),
        (2026, "3500.01", "0.0758"),
        (2026, "0", "0"),
        (2026, "100", "0"),
        (2026, "17402.21", "0.0758"),
        (2026, "17402.22", "0.1852"),
        (2026, "19200.17", "0.1852"),
        (2026, "19200.18", "0.3146"),
        (2026, "20000", "0.3146"),
        (2026, "70000", "0.3764"),
        (2026, "150000", "0.434"),
        (2026, "200000", "0.4669"),
        (2026, "201127.06", "0.4669"),
        (2026, "201127.07", "0.4755"),
        (2026, "250000", "0.4755"),
        (2026, "300000", "0.5125"),
        (2026, "401126.93", "0.5125"),
        (2026, "401126.94", "0.504"),
        (2026, "410000", "0.504"),
    ],
)
def test_the_marginal_rate_is_the_sum_of_the_rates_that_apply_rounded_to_four_decimals(
    year: int, salary: str, rate: str
) -> None:
    worksheets = build_tax_computation().compute(
        TaxCalculationRequest(MANITOBA, year, (Artifact(EMPLOYMENT_INCOME, D(salary)),))
    )
    (summary,) = worksheets["ca-mb/return"]

    assert summary.get(bundled_kinds().kind("ca-mb/marginal_tax_rate")).value == D(rate)
