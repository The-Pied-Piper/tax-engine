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

The fall of the Manitoba age amount. For a filer born in 1960 or earlier, Worksheet MB428 "Line
58080 - Age amount" line 4 is the net income over the threshold of 27,749.00, line 5 is the printed
rate of 15%, and line 7 is the maximum of 3,728.00 less 15% of line 4, claimed up to a net income of
52,601.99 (the printed "$52,602 or more, enter 0"). A further dollar of net income takes 15% of a
dollar off the amount, and each dollar of it is tax at the MB428 line 52 rate of 10.8%. With N the
part of a dollar of salary left in the net income (1 - enhanced CPP rate, 0.99, or 1 where no CPP
is paid):

    age term = 15% x 10.8% x N = 0.0162 x N, from 0.01 over the threshold to 52,601.99 of net income

The Manitoba marginal rate adds it to the bracket rate beside the family tax benefit's fall, and the
federal age amount falls the same way from its own threshold (T1: 15% x N x the federal credit
rate, 0.0215325 in 2025 and 0.021 in 2026 from a net income of 45,522.00 in 2025 and 46,432.00 in
2026), which the federal half carries. The marginal tax rate of a filer born in 1955 is the sum
worked in the comments of `AGE_TOTALS`; the Manitoba parts are in `..._gates.py` (2025) and
`..._gates_2026.py` (2026). A filer born in 1955 is 70 and still pays CPP in 2025 and pays none in
2026 (N = 1, the contribution rate 0.0163, the EI rate only).

At the exact edge $2,000 the rate is the lower band's (the EI rate is 0). A contribution band reads
its own rate from its lower bound, so at exactly $3,500 the CPP rate already applies: CPP 4.95% +
1% and EI, 0.0759 in 2025 and 0.0758 in 2026, the same as the next cent.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import pytest

from tax_engine import build_tax_computation
from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca.catalog.personal_amounts import BIRTH_YEAR
from tests.kinds import bundled_kinds

D = Decimal
MANITOBA = JurisdictionCode("CA-MB")


@pytest.mark.parametrize(
    ("year", "salary", "rate"),
    [
        (2025, "2000", "1"),
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
        (2026, "2000", "1"),
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


# Year, year of birth, salary, marginal tax rate: federal + Manitoba + contribution rates, each
# worked below (the age term is in the Manitoba rate, the federal age term in the federal one).
AGE_TOTALS = [
    (2025, 1955, "40000", "0.3354"),  # 0.1339945 + 0.1254636 + 0.0759 = 0.3353581
    (2025, 1955, "46000", "0.3569"),  # 0.155527 + 0.1254636 + 0.0759 = 0.3568906
    (2025, 1955, "50000", "0.3666"),  # 0.155527 + 0.1351458 + 0.0759 = 0.3665728
    (2025, 1955, "53097.97", "0.3666"),
    (2025, 1955, "53097.98", "0.3505"),  # 0.155527 + 0.1191078 + 0.0759 = 0.3505348
    (2025, 1955, "60000", "0.4099"),  # 0.214927 + 0.1191078 + 0.0759 = 0.4099348
    (2025, 1980, "40000", "0.3097"),  # 0.1339945 + 0.0998028 + 0.0759 = 0.3096973
    (2025, 1980, "53097.97", "0.3290"),  # 0.1339945 + 0.1191078 + 0.0759 = 0.3290023
    (2025, None, "53097.98", "0.3290"),
    (2026, 1955, "40000", "0.2862"),  # 0.137718 + 0.1321596 + 0.0163 = 0.2861776
    (2026, 1955, "46000", "0.2765"),  # 0.137718 + 0.1224396 + 0.0163 = 0.2764576
    (2026, 1955, "50000", "0.3170"),  # 0.158718 + 0.1419396 + 0.0163 = 0.3169576
    (2026, 1955, "52601.99", "0.3170"),
    (2026, 1955, "52602", "0.3008"),  # 0.158718 + 0.1257396 + 0.0163 = 0.3007576
    (2026, 1980, "40000", "0.3050"),  # 0.129388 + 0.0998136 + 0.0758 = 0.3050016
    (2026, None, "50000", "0.3243"),  # 0.129388 + 0.1191186 + 0.0758 = 0.3243066
]


@pytest.mark.parametrize(("year", "born", "salary", "rate"), AGE_TOTALS)
def test_the_marginal_rate_with_the_fall_of_the_age_amount(
    year: int, born: int | None, salary: str, rate: str
) -> None:
    given: list[Artifact[Any]] = [Artifact(EMPLOYMENT_INCOME, D(salary))]
    if born is not None:
        given.append(Artifact(BIRTH_YEAR, born))
    worksheets = build_tax_computation().compute(
        TaxCalculationRequest(MANITOBA, year, tuple(given))
    )
    (summary,) = worksheets["ca-mb/return"]

    assert summary.get(bundled_kinds().kind("ca-mb/marginal_tax_rate")).value == D(rate)
