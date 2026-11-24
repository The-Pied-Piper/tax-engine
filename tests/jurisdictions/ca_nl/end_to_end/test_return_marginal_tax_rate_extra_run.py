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
# Salaries in each part of the rate (no tax, the EI band, the low-income reduction and its
# phase-out, the brackets, the CPP2 band, the basic personal amount's phase-down), and the salaries
# of `KNOWN_EXCEPTIONS`.
SALARIES = (
    1_500, 2_000, 2_020, 3_500, 5_000, 10_000, 15_000, 18_750, 20_000, 24_000, 26_000, 28_000,
    30_000, 30_333, 30_750, 35_000, 40_000, 45_000, 50_000, 59_000, 60_000, 68_811, 70_000,
    71_250, 75_000, 90_000, 115_750, 118_156, 120_000, 150_000, 182_500, 200_000, 250_000,
    283_250, 300_000,
)  # fmt: skip
# Every $250 from $1,000 to $400,000 and the salaries above: the sweep of every year.
SWEEP = tuple(sorted({*range(1_000, 400_001, 250), *SALARIES}))
# (tax year, salary): why the run of $100 is not the derivative there. Each salary is run again
# over a smaller step in `SMALLER_STEPS`, from the point the rate is meant for.
EDGE = "an exact band edge: the published rate is the lower band's"
EI_BAND = "the EI band of T2204 line 16 ($2,000 to $2,033) is narrower than the $100 step"
KNOWN_EXCEPTIONS: dict[tuple[int, int], str] = {
    (2025, 2_000): "EI starts above $2,000 (T2204 line 16), " + EDGE,
    (2025, 2_020): EI_BAND,
    (2025, 3_500): "the CPP starts above $3,500, " + EDGE,
    (2025, 18_750): "federal tax (T1 line 42900) starts at $18,820.27",
    (2025, 30_333): "the low-income tax reduction (NL428 line 104) is used up",
    (2025, 71_250): "the CPP base and enhanced ceiling is $71,300",
    (2025, 115_750): "the federal bracket at taxable income $114,750",
    (2025, 283_250): "the NL428 bracket at taxable income $282,214",
    (2026, 2_000): "EI starts above $2,000 (T2204 line 16), " + EDGE,
    (2026, 2_020): EI_BAND,
    (2026, 3_500): "the CPP starts above $3,500, " + EDGE,
    (2026, 30_750): "the low-income tax reduction (NL428 line 104) is used up",
    (2026, 45_000): "the NL428 bracket where table 1 moves to its second row",
    (2026, 59_000): "the federal bracket at the second row's start",
    (2026, 68_811): "the EI maximum yearly insurable earnings is $68,900",
    (2026, 118_156): "the federal bracket at taxable income $117,045",
    (2026, 182_500): "the federal basic personal amount starts to fall",
}
# (tax year, salary): (salary the run starts from, step).
SMALLER_STEPS = {
    (2025, 2_000): (2_001, 10),
    (2025, 2_020): (2_020, 10),
    (2025, 3_500): (3_501, 10),
    (2025, 18_750): (18_750, 25),
    (2025, 30_333): (30_430, 25),
    (2025, 71_250): (71_250, 25),
    (2025, 115_750): (115_750, 25),
    (2025, 283_250): (283_250, 25),
    (2026, 2_000): (2_001, 10),
    (2026, 2_020): (2_020, 10),
    (2026, 3_500): (3_501, 10),
    (2026, 30_750): (30_750, 10),
    (2026, 45_000): (45_000, 25),
    (2026, 59_000): (59_000, 25),
    (2026, 68_811): (68_901, 25),
    (2026, 118_156): (118_156, 10),
    (2026, 182_500): (182_500, 25),
}

EXCEPTION_CASES = [
    pytest.param(year, salary, id=f"{year}-{salary}") for (year, salary) in KNOWN_EXCEPTIONS
]


def _worksheets(
    year: int, salary: int, engine: TaxComputationService
) -> dict[str, tuple[Worksheet, ...]]:
    return engine.compute(
        TaxCalculationRequest(NEWFOUNDLAND, year, (Artifact(EMPLOYMENT_INCOME, D(salary)),))
    )


def _deductions(year: int, salary: int, engine: TaxComputationService) -> Decimal:
    worksheets = _worksheets(year, salary, engine)
    kinds = bundled_kinds()
    total = D("0")
    for form, kind in DEDUCTIONS:
        value = worksheets[form][0].get(kinds.kind(kind)).value
        assert isinstance(value, Decimal)
        total += value
    return total


def _marginal_rate(year: int, salary: int, engine: TaxComputationService) -> Decimal:
    value = _worksheets(year, salary, engine)[RETURN][0].get(bundled_kinds().kind(MARGINAL)).value
    assert isinstance(value, Decimal)
    return value


def _extra_run(year: int, salary: int, step: int, engine: TaxComputationService) -> Decimal:
    return (_deductions(year, salary + step, engine) - _deductions(year, salary, engine)) / step


@pytest.mark.parametrize("year", YEARS)
def test_the_marginal_rate_agrees_with_the_double_run_except_at_the_known_exceptions(
    year: int,
) -> None:
    engine = build_tax_computation()
    disagreements = {
        salary
        for salary in SWEEP
        if abs(_marginal_rate(year, salary, engine) - _extra_run(year, salary, STEP, engine))
        > TOLERANCE
    }

    assert disagreements == {salary for (y, salary) in KNOWN_EXCEPTIONS if y == year}


@pytest.mark.parametrize(("year", "salary"), EXCEPTION_CASES)
def test_a_known_exception_agrees_with_a_run_that_stays_inside_the_band(
    year: int, salary: int
) -> None:
    engine = build_tax_computation()
    start, step = SMALLER_STEPS[(year, salary)]

    assert abs(_marginal_rate(year, start, engine) - _extra_run(year, start, step, engine)) <= (
        TOLERANCE
    )


def test_every_known_exception_is_a_salary_of_the_sweep() -> None:
    assert {salary for _year, salary in KNOWN_EXCEPTIONS} <= set(SALARIES)


def test_every_known_exception_is_a_salary_with_a_smaller_step() -> None:
    assert set(KNOWN_EXCEPTIONS) == set(SMALLER_STEPS)
