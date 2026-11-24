"""The Manitoba marginal rate agrees with an extra run of the engine, for 2025 and 2026.

The marginal rate (`ca-mb/marginal_tax_rate`) is the change in the take-home deductions per extra
dollar of salary: T1 line 43500 "Total payable" plus the CPP base contribution (Schedule 8 line 25),
the CPP enhanced contribution (line 12 of Part 3), the CPP2 contribution (line 22) and the EI
premium of T2204 line 16, for a salary-only filer. The return calculates it with the rates of the
forms, and runs nothing twice. This test is the independent check: it runs the real engine at a
salary and at the salary plus a step, and compares the change in those deductions per dollar with
the rate the return calculated at the salary.

The step is $100. The EI band of T2204 line 16 ($2,000 to $2,033) is narrower than that, so the
salaries inside or just over it use a smaller step ($10, and $1 at $1,999, where a step of $10
would cross $2,000). A step smaller than $10 is not used elsewhere, since the cent rounding of the
forms' lines (about a cent for each of the tax lines) moves a forward difference by more than the
tolerance. The other narrow bands and breaks are salaries just under where the rate changes, where
$100 would reach it; they use a $10 step, which does not, and the reason is in
`NARROW_BAND_STEPS`. A salary that sits exactly on the first dollar of a band of the contributions
is in `KNOWN_EXCEPTIONS` with the reason: the rate there is the lower band's, so the salary a
dollar over (in the list) is the check.

The list was found by a denser run, every $250 from $1,000 to $410,000, for both years, which
disagreed only at the salaries below (and the 2026 break at $401,100, found separately).
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
RETURN = "ca-mb/return"
MARGINAL = "ca-mb/marginal_tax_rate"
TOLERANCE = D("0.001")
# The take-home deductions, as the manifest's `take_home` block names them.
DEDUCTIONS = (
    ("ca/t1_tax_and_credits", "ca/total_payable"),
    ("ca/schedule_8", "ca/schedule_8_cpp_base_contributions_on_return"),
    ("ca/schedule_8", "ca/cpp_part_3_line_12"),
    ("ca/schedule_8", "ca/cpp_part_3_line_22"),
    ("ca/t2204", "ca/t2204_line_16"),
)

SALARIES = (
    1_000,
    1_500,
    1_999,
    2_000,
    2_001,
    2_020,
    3_000,
    3_500,
    3_501,
    5_000,
    8_000,
    10_000,
    15_000,
    17_300,
    17_500,
    18_750,
    19_000,
    19_900,
    21_000,
    22_900,
    23_300,
    30_000,
    40_000,
    47_000,
    50_000,
    59_000,
    60_000,
    65_000,
    70_000,
    71_250,
    72_300,
    75_000,
    80_000,
    85_000,
    100_000,
    101_000,
    115_750,
    120_000,
    150_000,
    175_000,
    182_500,
    190_000,
    200_000,
    201_000,
    210_000,
    250_000,
    300_000,
    390_000,
    400_000,
    401_000,
    401_100,
    405_000,
)
# A smaller step near a narrow band or a break, so the extra run does not cross it.
NARROW_BAND_STEPS = {
    1_999: 1,  # EI starts above $2,000
    2_001: 10,  # the EI band of T2204 line 16 ends at $2,033
    2_020: 10,
    3_501: 10,  # CPP starts above the $3,500 exemption
    18_750: 10,  # T1 line 42900 first above $0 at $18,820.27 (federal gate opens)
    71_250: 10,  # the CPP first additional band ends and CPP2 starts at $71,300
    101_000: 10,  # MB428 line 5 moves to the 17.4% column above a taxable income of $100,000
    115_750: 10,  # the federal 26% column starts above a taxable income of $114,750
    201_000: 10,  # the basic personal amount phase-out starts at a net income of $200,000.07
}
# (tax year, salary): the same, for a break in one year only (the datasets of 2026 carry other
# figures, so the break is at another salary; the year it is not in runs over $100 as usual).
YEAR_NARROW_BAND_STEPS = {
    (2025, 401_000): 10,  # the phase-out ends: Worksheet MB428 line 9 is 0.00 from $401,073.94
    (2026, 401_100): 10,  # the phase-out ends: Worksheet MB428 line 9 is 0.00 from $401,126.94
    (2026, 59_000): 10,  # the federal 20.5% column ends above a taxable income of $58,523
    (2026, 182_500): 10,  # the federal 29% column starts above a taxable income of $181,440
}
# (tax year, salary): the first dollar of a band of the contributions, where the rate at the salary
# is the lower band's and the forward difference the upper band's.
KNOWN_EXCEPTIONS: dict[tuple[int, int], str] = {
    (2025, 2_000): "the EI premium starts above $2,000 (T2204 line 16): $0 at $2,000",
    (2026, 2_000): "the EI premium starts above $2,000 (T2204 line 16): $0 at $2,000",
    (2025, 3_500): "the CPP base and first additional rates start above the $3,500 exemption",
    (2026, 3_500): "the CPP base and first additional rates start above the $3,500 exemption",
}

CASES = [
    pytest.param(year, salary, id=f"{year}-{salary}")
    for year in (2025, 2026)
    for salary in SALARIES
    if (year, salary) not in KNOWN_EXCEPTIONS
]


def _deductions(year: int, salary: Decimal) -> Decimal:
    worksheets = build_tax_computation().compute(
        TaxCalculationRequest(MANITOBA, year, (Artifact(EMPLOYMENT_INCOME, salary),))
    )
    kinds = bundled_kinds()
    return sum(
        (worksheets[form][0].get(kinds.kind(kind)).value for form, kind in DEDUCTIONS), D("0")
    )


def _marginal_rate(year: int, salary: Decimal) -> Decimal:
    worksheets = build_tax_computation().compute(
        TaxCalculationRequest(MANITOBA, year, (Artifact(EMPLOYMENT_INCOME, salary),))
    )
    value = worksheets[RETURN][0].get(bundled_kinds().kind(MARGINAL)).value
    assert isinstance(value, Decimal)
    return value


@pytest.mark.parametrize(("year", "salary"), CASES)
def test_the_marginal_rate_is_the_extra_dollar_change_in_the_take_home_deductions(
    year: int, salary: int
) -> None:
    step = YEAR_NARROW_BAND_STEPS.get((year, salary), NARROW_BAND_STEPS.get(salary, 100))
    extra_run = (_deductions(year, D(salary + step)) - _deductions(year, D(salary))) / step

    assert abs(_marginal_rate(year, D(salary)) - extra_run) <= TOLERANCE


def test_every_known_exception_is_a_salary_of_the_list() -> None:
    assert {salary for _year, salary in KNOWN_EXCEPTIONS} <= set(SALARIES)
