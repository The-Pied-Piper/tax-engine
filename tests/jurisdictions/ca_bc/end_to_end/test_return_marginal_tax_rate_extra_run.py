"""The British Columbia marginal rate agrees with an extra run of the engine, for 2025 and 2026.

The marginal rate (`ca-bc/marginal_tax_rate`) is the change in the take-home deductions per extra
dollar of salary: T1 line 43500 "Total payable" plus the CPP base contribution (Schedule 8 line
25), the CPP enhanced contribution (line 12 of Part 3), the CPP2 contribution (line 22) and the EI
premium of T2204 line 16, for a salary-only filer. The return calculates it with the rates of the
forms and runs nothing twice. This test is the independent check: it runs the real engine at a
salary and at the salary plus a step, and compares the change in those deductions per dollar with
the rate the return calculated at the salary.

Two sweeps run for each tax year: a list of chosen salaries (the same list as the Ontario check,
and the salaries around British Columbia's own breaks), and every $250 from $1,000 to $400,000.

The step is $100. A salary whose $100 run crosses a break in the rate (a bracket edge, the salary
where a tax first turns positive, the CPP and EI maximums) is run again with a smaller step that
stays inside one band: $10, or $50 where the cent rounding of the forms' lines (about a cent for
each tax line) moves a $10 difference by more than the tolerance. A step of $10 or less is used
nowhere else, for the same reason. `NARROW_STEPS` lists each such salary with the break the run
crossed; a test checks that the rate really does change inside the $100 run, so no salary is
listed for a reason that is not there. A salary that is itself the edge of a band is in
`EDGES`: the rate at an exact edge is the lower band's, while a forward difference is the upper
band's (the CPP exemption of $3,500, the EI band start of $2,000), and a salary three dollars under
the salary where BC428 line 80 turns positive (2026, $26,753) cannot be stepped without the cent
rounding; the salaries around each (the chosen list and the gates test) pin them.
"""

from __future__ import annotations

from decimal import Decimal
from functools import cache

import pytest

from tax_engine import build_tax_computation
from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tests.kinds import bundled_kinds

D = Decimal
BRITISH_COLUMBIA = JurisdictionCode("CA-BC")
RETURN = "ca-bc/return"
MARGINAL = "ca-bc/marginal_tax_rate"
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

CHOSEN = (
    1_000,
    1_500,
    1_999,
    2_001,
    2_020,
    3_000,
    5_000,
    8_000,
    10_000,
    12_000,
    15_000,
    17_000,
    19_000,
    19_900,
    21_000,
    23_000,
    26_000,
    26_760,
    26_800,
    28_000,
    31_000,
    33_000,
    36_000,
    40_000,
    45_000,
    48_300,
    50_000,
    55_000,
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
    200_300,
    210_000,
    250_000,
    300_000,
)
SWEEP = tuple(range(1_000, 400_001, 250))

# (tax year, salary): (smaller step, the break the $100 run crosses).
NARROW_STEPS: dict[tuple[int, int], tuple[int, str]] = {
    (2025, 1_999): (1, "the EI band of T2204 line 16 ($2,000 to $2,033) is under 100 wide"),
    (2025, 2_001): (10, "the EI band of T2204 line 16 ($2,000 to $2,033) is under 100 wide"),
    (2025, 2_020): (10, "the EI band of T2204 line 16 ($2,000 to $2,033) is under 100 wide"),
    (2026, 1_999): (1, "the EI band of T2204 line 16 ($2,000 to $2,033) is under 100 wide"),
    (2026, 2_001): (10, "the EI band of T2204 line 16 ($2,000 to $2,033) is under 100 wide"),
    (2026, 2_020): (10, "the EI band of T2204 line 16 ($2,000 to $2,033) is under 100 wide"),
    (2025, 18_750): (10, "T1 line 42900 turns positive at 18,820.27 (the federal part opens)"),
    (2025, 25_500): (10, "BC428 line 80 turns positive at 25,551.25 (the British Columbia part)"),
    (2025, 71_250): (10, "CPP2 starts at 71,300, the CPP base and enhanced rates end"),
    (2025, 115_750): (10, "the federal 26% bracket starts at taxable income 114,750"),
    (2026, 50_750): (10, "the British Columbia 7.7% bracket ends at taxable income 50,363"),
    (2026, 59_000): (50, "the federal 20.5% bracket starts at taxable income 58,523"),
    (2026, 116_750): (10, "the British Columbia 10.5% bracket starts at taxable income 115,648"),
    (2026, 141_500): (10, "the British Columbia 14.7% rate starts above 140,430"),
    (2026, 182_500): (10, "the federal 29% bracket starts at taxable income 181,440"),
    (2026, 191_500): (10, "the British Columbia 16.8% bracket starts at taxable income 190,405"),
}
# (tax year, salary): why a forward difference cannot be compared at the salary itself.
EDGES: dict[tuple[int, int], str] = {
    (2025, 2_000): "the EI band starts: the rate at the edge is the lower band's (0)",
    (2026, 2_000): "the EI band starts: the rate at the edge is the lower band's (0)",
    (2025, 3_500): "the CPP exemption ends: the rate at the edge is the lower band's",
    (2026, 3_500): "the CPP exemption ends: the rate at the edge is the lower band's",
    (2026, 26_750): "BC428 line 80 turns positive 3 dollars up, at 26,752.96",
}

_SERVICE = build_tax_computation()


@cache
def _worksheets(year: int, salary: int) -> dict[str, tuple[Worksheet, ...]]:
    return _SERVICE.compute(
        TaxCalculationRequest(BRITISH_COLUMBIA, year, (Artifact(EMPLOYMENT_INCOME, D(salary)),))
    )


def _deductions(year: int, salary: int) -> Decimal:
    worksheets = _worksheets(year, salary)
    kinds = bundled_kinds()
    return sum(
        (worksheets[form][0].get(kinds.kind(kind)).value for form, kind in DEDUCTIONS), D("0")
    )


def _marginal_rate(year: int, salary: int) -> Decimal:
    value = _worksheets(year, salary)[RETURN][0].get(bundled_kinds().kind(MARGINAL)).value
    assert isinstance(value, Decimal)
    return value


def _step(year: int, salary: int) -> int:
    narrow = NARROW_STEPS.get((year, salary))
    return narrow[0] if narrow else STEP


def _disagreement(year: int, salary: int) -> str | None:
    step = _step(year, salary)
    extra_run = (_deductions(year, salary + step) - _deductions(year, salary)) / step
    rate = _marginal_rate(year, salary)
    if abs(rate - extra_run) <= TOLERANCE:
        return None
    return f"{year} ${salary}: rate {rate}, extra run over ${step} {extra_run}"


@pytest.mark.parametrize(
    ("year", "salary"),
    [
        pytest.param(year, salary, id=f"{year}-{salary}")
        for year in (2025, 2026)
        for salary in CHOSEN
        if (year, salary) not in EDGES
    ],
)
def test_the_marginal_rate_is_the_extra_dollar_change_in_the_take_home_deductions(
    year: int, salary: int
) -> None:
    assert _disagreement(year, salary) is None


@pytest.mark.parametrize("year", [2025, 2026])
def test_the_marginal_rate_agrees_with_an_extra_run_at_every_250_dollars_to_400000(
    year: int,
) -> None:
    disagreements = [
        text
        for salary in SWEEP
        if (year, salary) not in EDGES and (text := _disagreement(year, salary)) is not None
    ]

    assert disagreements == []


@pytest.mark.parametrize(("year", "salary"), sorted(set(NARROW_STEPS) | set(EDGES)))
def test_the_rate_changes_inside_the_100_dollar_run_of_a_listed_salary(
    year: int, salary: int
) -> None:
    # A listed salary is a break: the rate at the end of the $100 run is not the rate at the start.
    assert _marginal_rate(year, salary + STEP) != _marginal_rate(year, salary)


def test_every_listed_salary_is_a_salary_of_the_sweeps() -> None:
    listed = {salary for _year, salary in set(NARROW_STEPS) | set(EDGES)}

    assert listed <= set(SWEEP) | set(CHOSEN)
