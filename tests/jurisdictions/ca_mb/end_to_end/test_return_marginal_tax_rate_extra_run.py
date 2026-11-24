"""The Manitoba marginal rate agrees with an extra run of the engine, for 2025 and 2026.

The marginal rate (`ca-mb/marginal_tax_rate`) is the change in the take-home deductions per extra
dollar of salary: T1 line 43500 "Total payable" plus the CPP base contribution (Schedule 8 line 25),
the CPP enhanced contribution (line 12 of Part 3), the CPP2 contribution (line 22) and the EI
premium of T2204 line 16, for a salary-only filer. The return calculates it with the rates of the
forms, and runs nothing twice. This test is the independent check: it runs the real engine at a
salary and at the salary plus a step, and compares the change in those deductions per dollar with
the rate the return calculated at the salary.

The step is $100. The EI band of T2204 line 16 ($2,000 to $2,033) is narrower than that, so the
salaries inside or just over it use a smaller step ($10, and $1 at $1,999, where a step of $10 would
cross $2,000). A sweep of every $250 from $1,000 to $410,000 in both years (and the 2026 break at
$401,100, found separately) agreed everywhere except at the salaries in `KNOWN_EXCEPTIONS`: there
the run of $100 crosses a break in the rate, so the forward difference is not the derivative. Each
is listed with its break and run again with a step that stays inside the band (`SMALLER_STEPS`), at
which the rate agrees. A step below $10 is not used where a break is not near: the cent rounding of
the forms' lines moves a forward difference by more than the tolerance. The salaries that sit
exactly on the lower edge of a band ($2,000 and $3,500) are pinned by value in
`test_return_marginal_tax_rate_values.py` (the rate at the edge and one cent above it): at an
exact edge the published rate is the lower band's (the EI rate is 0 at $2,000, the CPP rate 0 at
$3,500), and any run goes into the next band.
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
    2_001,
    2_020,
    3_000,
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
# A smaller step inside the narrow EI band of T2204 line 16, so the extra run does not cross it.
NARROW_BAND_STEPS = {1_999: 1, 2_001: 10, 2_020: 10}
# (tax year, salary): the forward difference is not the derivative there. Each reason is a break in
# the rate inside the run of $100; the salary is run again with a smaller step in
# `SMALLER_STEPS`, inside the band, where the rate agrees.
KNOWN_EXCEPTIONS: dict[tuple[int, int], str] = {
    (2025, 18_750): "federal tax (T1 line 42900) first above zero, at $18,820.27",
    (2025, 71_250): "the CPP first additional band ends and CPP2 starts at $71,300",
    (2025, 101_000): "MB428 line 5 moves to the 17.4% column above a taxable income of $100,000",
    (2025, 115_750): "the federal 26% column starts above a taxable income of $114,750",
    (2025, 201_000): "the basic personal amount phase-out starts at a net income of $200,000.07",
    (2025, 401_000): "the phase-out ends: Worksheet MB428 line 9 is 0.00 from $401,073.94",
    (2026, 59_000): "the federal 20.5% column ends above a taxable income of $58,523",
    (2026, 182_500): "the federal 29% column starts above a taxable income of $181,440",
    (2026, 401_100): "the phase-out ends: Worksheet MB428 line 9 is 0.00 from $401,126.94",
}
SMALLER_STEPS = {key: 10 for key in KNOWN_EXCEPTIONS}

CASES = [
    pytest.param(year, salary, id=f"{year}-{salary}")
    for year in (2025, 2026)
    for salary in SALARIES
    if (year, salary) not in KNOWN_EXCEPTIONS
]
EXCEPTION_CASES = [
    pytest.param(year, salary, id=f"{year}-{salary}") for (year, salary) in KNOWN_EXCEPTIONS
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
    step = NARROW_BAND_STEPS.get(salary, 100)
    extra_run = (_deductions(year, D(salary + step)) - _deductions(year, D(salary))) / step

    assert abs(_marginal_rate(year, D(salary)) - extra_run) <= TOLERANCE


@pytest.mark.parametrize(("year", "salary"), EXCEPTION_CASES)
def test_a_known_exception_agrees_with_a_run_that_stays_inside_the_band(
    year: int, salary: int
) -> None:
    step = SMALLER_STEPS[(year, salary)]
    extra_run = (_deductions(year, D(salary + step)) - _deductions(year, D(salary))) / step

    assert abs(_marginal_rate(year, D(salary)) - extra_run) <= TOLERANCE


@pytest.mark.parametrize(("year", "salary"), EXCEPTION_CASES)
def test_the_run_of_100_dollars_crosses_the_break_of_each_known_exception(
    year: int, salary: int
) -> None:
    run = (_deductions(year, D(salary + 100)) - _deductions(year, D(salary))) / 100

    assert abs(_marginal_rate(year, D(salary)) - run) > TOLERANCE


def test_every_known_exception_is_a_salary_of_the_sweep() -> None:
    assert {salary for _year, salary in KNOWN_EXCEPTIONS} <= set(SALARIES)


def test_every_known_exception_is_a_salary_with_a_smaller_step() -> None:
    assert set(KNOWN_EXCEPTIONS) == set(SMALLER_STEPS)
