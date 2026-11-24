"""The Newfoundland and Labrador marginal rate agrees with a double run of the engine.

Checked for 2025 and 2026.

The marginal rate (`ca-nl/marginal_tax_rate`) is the change in the take-home deductions per extra
dollar of salary: T1 line 43500 "Total payable" plus the CPP base contribution (Schedule 8 line
25), the CPP enhanced contribution (line 12 of Part 3), the CPP2 contribution (line 22) and the
EI premium of T2204 line 16, for a salary-only filer. The return calculates it from the rates of
the forms and runs nothing twice. This test is the independent check: it runs the real engine at a
salary and at the salary plus $100, and compares the change in those deductions per dollar with the
rate the return calculated at the salary.

The sweep takes every salary from $1,000 to $400,000 in steps of $250 and some salaries between,
for both years, and `KNOWN_EXCEPTIONS` lists each salary where the rate changes inside the $100
run, so that the forward difference is not the derivative there. For each one the check is
repeated from the point the rate is meant for with a smaller step ($25, or $10 where the break is
within $25), where it agrees.
A break is one of two kinds:

- an exact band edge ($2,000 where the EI premium starts, $3,500 where the CPP starts): the
  published rate at an edge is the lower band's, which is 0 or the rate before the band, so the
  run is checked from one dollar above the edge;
- a break inside the run: the CPP ceiling, a federal or Newfoundland and Labrador bracket (taxable
  income is the salary less the CPP enhanced and second additional deductions), where the federal
  basic personal amount stops falling, or where the low-income tax reduction (NL428 lines 101 to
  104) is used up.

The cent rounding of the forms' lines moves a difference over a step of $1 by more than the
tolerance, which is why no step below $10 is used.
"""

from __future__ import annotations

from decimal import Decimal
from functools import cache

import pytest

from tax_engine import build_tax_computation
from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tests.kinds import bundled_kinds

D = Decimal


@cache
def _engine() -> TaxComputationService:
    return build_tax_computation()


NEWFOUNDLAND = JurisdictionCode("CA-NL")
RETURN = "ca-nl/return"
MARGINAL = "ca-nl/marginal_tax_rate"
TOLERANCE = D("0.001")
STEP = 100
# The take-home deductions, as the manifest's `take_home` block names them.
DEDUCTIONS = (
    ("ca/t1_tax_and_credits", "ca/total_payable"),
    ("ca/schedule_8", "ca/schedule_8_cpp_base_contributions_on_return"),
    ("ca/schedule_8", "ca/cpp_part_3_line_12"),
    ("ca/schedule_8", "ca/cpp_part_3_line_22"),
    ("ca/t2204", "ca/t2204_line_16"),
)
YEARS = (2025, 2026)
# Every $250 from $1,000 to $400,000, plus salaries in each part of the rate (no tax, the EI band,
# the low-income reduction and its phase-out, the brackets, the CPP2 band, the basic personal
# amount's phase-down) and the off-grid salaries of `KNOWN_EXCEPTIONS`.
SPOTS = (
    1_500, 2_020, 5_000, 10_000, 15_000, 20_000, 24_000, 26_000, 28_000, 30_000, 30_333, 35_000,
    40_000, 50_000, 60_000, 68_811, 70_000, 75_000, 90_000, 118_156, 120_000, 150_000, 200_000,
    250_000, 300_000,
)  # fmt: skip
SALARIES = tuple(sorted({*range(1_000, 400_001, 250), *SPOTS}))
# (tax year, salary): (salary the run starts from, step, why the $100 run is not the derivative).
EDGE = "an exact band edge: the published rate is the lower band's"
EI_BAND = "the EI band of T2204 line 16 ($2,000 to $2,033) is narrower than the $100 step"
KNOWN_EXCEPTIONS: dict[tuple[int, int], tuple[int, int, str]] = {
    (2025, 2_000): (2_001, 10, "EI starts above $2,000 (T2204 line 16), " + EDGE),
    (2025, 2_020): (2_020, 10, EI_BAND),
    (2025, 3_500): (3_501, 10, "the CPP starts above $3,500, " + EDGE),
    (2025, 18_750): (18_750, 25, "federal tax (T1 line 42900) starts at $18,820.27"),
    (2025, 30_333): (30_430, 25, "the low-income tax reduction (NL428 line 104) is used up"),
    (2025, 71_250): (71_250, 25, "the CPP base and enhanced ceiling is $71,300"),
    (2025, 115_750): (115_750, 25, "the federal bracket at taxable income $114,750"),
    (2025, 283_250): (283_250, 25, "the NL428 bracket at taxable income $282,214"),
    (2026, 2_000): (2_001, 10, "EI starts above $2,000 (T2204 line 16), " + EDGE),
    (2026, 2_020): (2_020, 10, EI_BAND),
    (2026, 3_500): (3_501, 10, "the CPP starts above $3,500, " + EDGE),
    (2026, 30_750): (30_750, 10, "the low-income tax reduction (NL428 line 104) is used up"),
    (2026, 45_000): (45_000, 25, "the NL428 bracket where table 1 moves to its second row"),
    (2026, 59_000): (59_000, 25, "the federal bracket at the second row's start"),
    (2026, 68_811): (68_901, 25, "the EI maximum yearly insurable earnings is $68,900"),
    (2026, 118_156): (118_156, 10, "the federal bracket at taxable income $117,045"),
    (2026, 182_500): (182_500, 25, "the federal basic personal amount starts to fall"),
}


@cache
def _compute(year: int, salary: int) -> dict[str, tuple[Worksheet, ...]]:
    return _engine().compute(
        TaxCalculationRequest(NEWFOUNDLAND, year, (Artifact(EMPLOYMENT_INCOME, D(salary)),))
    )


def _deductions(year: int, salary: int) -> Decimal:
    worksheets = _compute(year, salary)
    kinds = bundled_kinds()
    total = D("0")
    for form, kind in DEDUCTIONS:
        value = worksheets[form][0].get(kinds.kind(kind)).value
        assert isinstance(value, Decimal)
        total += value
    return total


def _marginal_rate(year: int, salary: int) -> Decimal:
    value = _compute(year, salary)[RETURN][0].get(bundled_kinds().kind(MARGINAL)).value
    assert isinstance(value, Decimal)
    return value


def _extra_run(year: int, salary: int, step: int) -> Decimal:
    return (_deductions(year, salary + step) - _deductions(year, salary)) / step


@pytest.mark.parametrize("year", YEARS)
def test_the_marginal_rate_agrees_with_the_double_run_except_at_the_known_exceptions(
    year: int,
) -> None:
    disagreements = {
        salary
        for salary in SALARIES
        if abs(_marginal_rate(year, salary) - _extra_run(year, salary, STEP)) > TOLERANCE
    }

    assert disagreements == {salary for (y, salary) in KNOWN_EXCEPTIONS if y == year}


@pytest.mark.parametrize(("year", "salary"), sorted(KNOWN_EXCEPTIONS))
def test_an_exception_agrees_over_a_smaller_step_from_the_point_the_rate_is_meant_for(
    year: int, salary: int
) -> None:
    start, step, _reason = KNOWN_EXCEPTIONS[(year, salary)]

    assert abs(_marginal_rate(year, start) - _extra_run(year, start, step)) <= TOLERANCE


def test_every_known_exception_is_a_salary_of_the_sweep() -> None:
    assert {salary for _year, salary in KNOWN_EXCEPTIONS} <= set(SALARIES)
