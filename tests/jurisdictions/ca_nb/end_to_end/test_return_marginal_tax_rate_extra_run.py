"""The New Brunswick marginal rate agrees with a double run of the engine.

Checked for 2025 and 2026.

The marginal rate (`ca-nb/marginal_tax_rate`) is the change in the take-home deductions per extra
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

- an exact band edge where the EI premium starts ($2,000): the published rate at the edge is the
  lower band's, which is 0, so the run is checked from one dollar above the edge. A contribution
  band that starts at its lower bound reads its own rate there, so $3,500 where the CPP starts is
  not a break: the run from $3,500 stays inside the CPP band;
- a break inside the run: the CPP ceiling, a federal or New Brunswick bracket (taxable income is
  the salary less the CPP enhanced and second additional deductions), where the federal basic
  personal amount stops falling, where the New Brunswick tax (NB428 line 97) is first above zero
  because the low-income tax reduction no longer absorbs it, or where the reduction stops at the
  single income limit of $48,653 (NB428 line 86 is 0 from a net income of $48,653).

The cent rounding of the forms' lines moves a difference over a step of $1 by more than the
tolerance, which is why no step below $10 is used.
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


NEW_BRUNSWICK = JurisdictionCode("CA-NB")
RETURN = "ca-nb/return"
MARGINAL = "ca-nb/marginal_tax_rate"
TOLERANCE = D("0.001")
# The take-home deductions, as the manifest's `take_home` block names them.
DEDUCTIONS = (
    ("ca/t1_tax_and_credits", "ca/total_payable"),
    ("ca/schedule_8", "ca/schedule_8_cpp_base_contributions_on_return"),
    ("ca/schedule_8", "ca/cpp_part_3_line_12"),
    ("ca/schedule_8", "ca/cpp_part_3_line_22"),
    ("ca/t2204", "ca/t2204_line_16"),
)
# Salaries in each part of the rate (no tax, the EI band, the low-income reduction and its
# phase-out, the brackets, the CPP2 band, the basic personal amount's phase-down), and the salaries
# of `KNOWN_EXCEPTIONS`.
SALARIES = (
    1_500,
    2_000,
    2_020,
    3_500,
    5_000,
    10_000,
    15_000,
    18_750,
    20_000,
    23_100,
    23_300,
    24_000,
    26_000,
    28_000,
    30_000,
    35_000,
    40_000,
    45_000,
    49_050,
    50_000,
    51_750,
    52_750,
    59_000,
    60_000,
    70_000,
    71_250,
    75_000,
    90_000,
    103_650,
    105_750,
    115_750,
    120_000,
    150_000,
    182_500,
    191_100,
    194_950,
    200_000,
    250_000,
    300_000,
)
# Every $250 from $1,000 to $400,000 and the salaries above: the sweep of every year.
SWEEP = tuple(sorted({*range(1_000, 400_001, 250), *SALARIES}))
# A smaller step near a narrow band, so the extra run does not cross the band's end: the EI band of
# T2204 line 16 ($2,000 to $2,033) is narrower than $100.
NARROW_BAND_STEPS = {2_020: 10}
# (tax year, salary): why the run of $100 is not the derivative there. Each salary is run again
# over a smaller step in `SMALLER_STEPS`, from the point the rate is meant for.
KNOWN_EXCEPTIONS: dict[tuple[int, int], str] = {
    (2025, 2_000): "the EI band of T2204 line 16 starts at $2,000 and ends at $2,033",
    (2025, 18_750): "federal tax (T1 line 42900) starts at $18,820.27",
    (2025, 23_100): "the New Brunswick tax (NB428 line 97) is first above zero at $23,147.60",
    (2025, 49_050): "the low-income tax reduction (NB428 line 86) stops at $48,653 of net income",
    (2025, 51_750): "the NB428 bracket at taxable income $51,306",
    (2025, 71_250): "the CPP base and enhanced ceiling is $71,300",
    (2025, 103_650): "the NB428 bracket at taxable income $102,614",
    (2025, 115_750): "the federal bracket at taxable income $114,750",
    (2025, 191_100): "the NB428 bracket at taxable income $190,060",
    (2026, 2_000): "the EI band of T2204 line 16 starts at $2,000 and ends at $2,033",
    (2026, 23_300): "the New Brunswick tax (NB428 line 97) is first above zero at $23,361.79",
    (2026, 49_050): "the low-income tax reduction (NB428 line 86) stops at $48,653 of net income",
    (2026, 52_750): "the NB428 bracket at taxable income $52,333",
    (2026, 59_000): "the federal bracket at the second row's start",
    (2026, 105_750): "the NB428 bracket at taxable income $104,666",
    (2026, 182_500): "the federal basic personal amount starts to fall",
    (2026, 194_950): "the NB428 bracket at taxable income $193,861",
}
# (tax year, salary): (salary the run starts from, step).
SMALLER_STEPS = {
    (2025, 2_000): (2_001, 10),
    (2025, 18_750): (18_750, 25),
    (2025, 23_100): (23_100, 25),
    (2025, 49_050): (49_050, 25),
    (2025, 51_750): (51_750, 25),
    (2025, 71_250): (71_250, 25),
    (2025, 103_650): (103_650, 25),
    (2025, 115_750): (115_750, 25),
    (2025, 191_100): (191_100, 25),
    (2026, 2_000): (2_001, 10),
    (2026, 23_300): (23_300, 25),
    (2026, 49_050): (49_050, 25),
    (2026, 52_750): (52_750, 25),
    (2026, 59_000): (59_000, 25),
    (2026, 105_750): (105_750, 25),
    (2026, 182_500): (182_500, 25),
    (2026, 194_950): (194_950, 25),
}

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
        TaxCalculationRequest(NEW_BRUNSWICK, year, (Artifact(EMPLOYMENT_INCOME, salary),))
    )
    kinds = bundled_kinds()
    return sum(
        (worksheets[form][0].get(kinds.kind(kind)).value for form, kind in DEDUCTIONS), D("0")
    )


def _marginal_rate(year: int, salary: Decimal) -> Decimal:
    worksheets = build_tax_computation().compute(
        TaxCalculationRequest(NEW_BRUNSWICK, year, (Artifact(EMPLOYMENT_INCOME, salary),))
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
    start, step = SMALLER_STEPS[(year, salary)]
    extra_run = (_deductions(year, D(start + step)) - _deductions(year, D(start))) / step

    assert abs(_marginal_rate(year, D(start)) - extra_run) <= TOLERANCE


@pytest.mark.parametrize(("year", "salary"), EXCEPTION_CASES)
def test_the_run_of_100_dollars_crosses_the_break_of_each_known_exception(
    year: int, salary: int
) -> None:
    run = (_deductions(year, D(salary + 100)) - _deductions(year, D(salary))) / 100

    assert abs(_marginal_rate(year, D(salary)) - run) > TOLERANCE


@pytest.mark.parametrize("year", (2025, 2026))
def test_a_sweep_of_every_250_dollars_disagrees_only_at_the_known_exceptions(year: int) -> None:
    # Umar's sweep: every $250 from $1,000 to $400,000 and the salaries above, with one engine
    # built once so that the 3,000 runs finish in reasonable time.
    engine = build_tax_computation()
    kinds = bundled_kinds()

    def run(salary: int) -> tuple[Decimal, Decimal]:
        worksheets = engine.compute(
            TaxCalculationRequest(NEW_BRUNSWICK, year, (Artifact(EMPLOYMENT_INCOME, D(salary)),))
        )
        deductions = D("0")
        for form, kind in DEDUCTIONS:
            value = worksheets[form][0].get(kinds.kind(kind)).value
            assert isinstance(value, Decimal)
            deductions += value
        marginal = worksheets[RETURN][0].get(kinds.kind(MARGINAL)).value
        assert isinstance(marginal, Decimal)
        return deductions, marginal

    disagreements = set()
    for salary in SWEEP:
        step = NARROW_BAND_STEPS.get(salary, 100)
        deductions, marginal = run(salary)
        if abs(marginal - (run(salary + step)[0] - deductions) / step) > TOLERANCE:
            disagreements.add(salary)

    assert disagreements == {salary for (y, salary) in KNOWN_EXCEPTIONS if y == year}


def test_every_known_exception_is_a_salary_of_the_sweep() -> None:
    assert {salary for _year, salary in KNOWN_EXCEPTIONS} <= set(SALARIES)


def test_every_known_exception_is_a_salary_with_a_smaller_step() -> None:
    assert set(KNOWN_EXCEPTIONS) == set(SMALLER_STEPS)
