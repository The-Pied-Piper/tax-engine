"""The Manitoba marginal rate agrees with an extra run of the engine, for 2025 and 2026.

The marginal rate (`ca-mb/marginal_tax_rate`) is the change in the take-home deductions per extra
dollar of salary: T1 line 43500 "Total payable" plus the CPP base contribution (Schedule 8 line 25),
the CPP enhanced contribution (line 12 of Part 3), the CPP2 contribution (line 22) and the EI
premium of T2204 line 16, for a salary-only filer. The return calculates it with the rates of the
forms and runs nothing twice. This test is the independent check: it runs the real engine at a
salary and at the salary plus a step, and compares the change in those deductions per dollar with
the rate the return calculated at the salary. It does so at a list of salaries (`SALARIES`) and at
every $250 from $1,000 to $410,000 (`SWEEP`), which takes in the end of the basic personal amount
phase-out at a net income of $400,000.

The step is $100. A forward difference over $100 is not the derivative where the run crosses a break
in the rate, so each salary the sweep finds that disagrees is in `KNOWN_EXCEPTIONS` with the break
its run crosses or the band edge it sits on, and is checked again below: a break with a step of
$10, which does not cross it; an edge a dollar higher. A step smaller than $10 is not used, since
the cent rounding of the forms' lines (about a cent for each of the tax lines) moves a forward
difference by more than the tolerance. A disagreement that is not in the list is a wrong rate.
The list holds the breaks that fall in the grid of the list and the sweep; it is not every break
of the rate (a break between two grid salaries, such as the 2026 federal 33% column near $259,540,
is not run over).

The engine is built once and each run is kept: the sweep is about 6,500 runs.
"""

from __future__ import annotations

from decimal import Decimal
from functools import cache, lru_cache

import pytest

from tax_engine import build_tax_computation
from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tests.kinds import bundled_kinds

D = Decimal
MANITOBA = JurisdictionCode("CA-MB")
RETURN = "ca-mb/return"
MARGINAL = "ca-mb/marginal_tax_rate"
TOLERANCE = D("0.001")
STEP = 100
SMALL_STEP = 10
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
    19_000,
    19_900,
    21_000,
    22_900,
    23_300,
    30_000,
    40_000,
    47_000,
    50_000,
    60_000,
    65_000,
    70_000,
    72_300,
    75_000,
    80_000,
    85_000,
    100_000,
    120_000,
    150_000,
    175_000,
    190_000,
    200_000,
    210_000,
    250_000,
    300_000,
    390_000,
    400_000,
    401_000,
    401_100,
    405_000,
)
SWEEP = tuple(range(1_000, 410_001, 250))
# Salaries a dollar over a narrow band use a smaller step, so the extra run does not cross its end.
NARROW_BAND_STEPS = {1_999: 1, 2_001: 10, 2_020: 10, 3_501: 10}
# (tax year, salary): the forward difference over $100 is not the derivative there. Each reason is
# a break in the rate inside the run (checked again with a $10 step) or, for the first dollar of a
# band of the contributions, an edge where the rate at the salary is the lower band's (checked a
# dollar higher).
KNOWN_EXCEPTIONS: dict[tuple[int, int], str] = {
    (2025, 2_000): "edge: the EI premium starts above $2,000 (T2204 line 16): $0 at $2,000",
    (2026, 2_000): "edge: the EI premium starts above $2,000 (T2204 line 16): $0 at $2,000",
    (2025, 3_500): "edge: the CPP base and first additional rates start above the $3,500 exemption",
    (2026, 3_500): "edge: the CPP base and first additional rates start above the $3,500 exemption",
    (2025, 18_750): "T1 line 42900 first above $0 at $18,820.27 (federal gate opens)",
    (2025, 71_250): "the CPP first additional band ends and CPP2 starts at $71,300",
    (2025, 101_000): "MB428 line 5 moves to the 17.4% column above a taxable income of $100,000",
    (2025, 115_750): "the federal 26% column starts above a taxable income of $114,750",
    (2025, 201_000): "the basic personal amount phase-out starts at a net income of $200,000.07",
    (2025, 401_000): "the phase-out ends: Worksheet MB428 line 9 is 0.00 from $401,073.94",
    (2026, 59_000): "the federal 20.5% column ends above a taxable income of $58,523",
    (2026, 182_500): "the federal 29% column starts above a taxable income of $181,440",
    (2026, 401_100): "the phase-out ends: Worksheet MB428 line 9 is 0.00 from $401,126.94",
}

CASES = [
    pytest.param(year, salary, id=f"{year}-{salary}")
    for year in (2025, 2026)
    for salary in SALARIES
    if (year, salary) not in KNOWN_EXCEPTIONS
]


@lru_cache(maxsize=1)
def _engine() -> TaxComputationService:
    return build_tax_computation()


@cache
def _run(year: int, salary: int) -> tuple[Decimal, Decimal]:
    """The take-home deductions and the return's marginal rate at a salary."""
    worksheets = _engine().compute(
        TaxCalculationRequest(MANITOBA, year, (Artifact(EMPLOYMENT_INCOME, D(salary)),))
    )
    kinds = bundled_kinds()
    deductions = sum(
        (worksheets[form][0].get(kinds.kind(kind)).value for form, kind in DEDUCTIONS), D("0")
    )
    rate = worksheets[RETURN][0].get(kinds.kind(MARGINAL)).value
    assert isinstance(rate, Decimal)
    return deductions, rate


def _gap(year: int, salary: int, step: int) -> Decimal:
    """The rate at the salary less the extra-run change in the deductions per dollar."""
    deductions, rate = _run(year, salary)
    extra_run = (_run(year, salary + step)[0] - deductions) / step
    return abs(rate - extra_run)


def _is_edge(year: int, salary: int) -> bool:
    return KNOWN_EXCEPTIONS[(year, salary)].startswith("edge")


@pytest.mark.parametrize("year,salary", CASES)
def test_the_marginal_rate_is_the_extra_dollar_change_in_the_take_home_deductions(
    year: int, salary: int
) -> None:
    step = NARROW_BAND_STEPS.get(salary, STEP)

    assert _gap(year, salary, step) <= TOLERANCE


@pytest.mark.parametrize("year", [2025, 2026])
def test_every_salary_of_the_sweep_is_the_extra_dollar_change_but_the_known_exceptions(
    year: int,
) -> None:
    disagreeing = {salary for salary in SWEEP if _gap(year, salary, STEP) > TOLERANCE}

    assert disagreeing == {
        salary for y, salary in KNOWN_EXCEPTIONS if y == year and salary in SWEEP
    }


@pytest.mark.parametrize("year,salary", sorted(KNOWN_EXCEPTIONS))
def test_every_known_exception_disagrees_over_100_and_agrees_over_a_smaller_run(
    year: int, salary: int
) -> None:
    assert salary in SALARIES or salary in SWEEP
    assert _gap(year, salary, STEP) > TOLERANCE
    if _is_edge(year, salary):
        assert _gap(year, salary + 1, SMALL_STEP) <= TOLERANCE
    else:
        assert _gap(year, salary, SMALL_STEP) <= TOLERANCE
