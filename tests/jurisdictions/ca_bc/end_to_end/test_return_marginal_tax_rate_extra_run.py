"""The British Columbia marginal rate agrees with an extra run of the engine, for 2025 and 2026.

The marginal rate (`ca-bc/marginal_tax_rate`) is the change in the take-home deductions per extra
dollar of salary: T1 line 43500 "Total payable" plus the CPP base contribution (Schedule 8 line
25), the CPP enhanced contribution (line 12 of Part 3), the CPP2 contribution (line 22) and the EI
premium of T2204 line 16, for a salary-only filer. The return calculates it with the rates of the
forms and runs nothing twice. This test is the independent check: it runs the real engine at a
salary and at the salary plus a step, and compares the change in those deductions per dollar with
the rate the return calculated at the salary.

One sweep runs for each tax year (Umar, 24 Nov 2026: test each province's marginal rate against a
double run of the engine like Ontario's): a list of chosen salaries (the same list as the Ontario
check, and the salaries around British Columbia's own breaks) together with every $250 from $1,000
to $400,000.

The step is $100. A salary whose $100 run crosses a break in the rate (a bracket edge, the salary
where a tax first turns positive, the CPP and EI maximums) is run again with a smaller step that
stays inside one band, listed in `NARROW_BAND_STEPS` with the break it avoids: $10, or $50 where
the cent rounding of the forms' lines (about a cent for each tax line) moves a $10 difference by
more than the tolerance, and $1 under the EI band of T2204 line 16 ($2,000 to $2,033). A step of
$10 or less is used nowhere else, for the same reason. A salary that is itself the edge of a band
is in `KNOWN_EXCEPTIONS` with the reason: the rate at an exact edge is the lower band's, while a
forward difference is the upper band's (the CPP exemption of $3,500, the EI band start of $2,000),
and a salary three dollars under the salary where BC428 line 80 turns positive (2026, $26,753)
cannot be stepped without the cent rounding; the salaries around each (the chosen list and
`test_return_marginal_tax_rate_gates.py`) pin them. Every other salary agrees within the tolerance.
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
BRITISH_COLUMBIA = JurisdictionCode("CA-BC")
RETURN = "ca-bc/return"
MARGINAL = "ca-bc/marginal_tax_rate"
TOLERANCE = D("0.001")
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
SALARIES = tuple(sorted(set(CHOSEN) | set(range(1_000, 400_001, 250))))
# (tax year, salary): a smaller step near a narrow band, so the extra run does not cross the
# band's end. Each is followed by the break the $100 run would cross.
NARROW_BAND_STEPS = {
    # The EI band of T2204 line 16 ($2,000 to $2,033) is narrower than $100.
    (2025, 1_999): 1,
    (2025, 2_001): 10,
    (2025, 2_020): 10,
    (2026, 1_999): 1,
    (2026, 2_001): 10,
    (2026, 2_020): 10,
    # T1 line 42900 turns positive at 18,820.27: the federal part opens.
    (2025, 18_750): 10,
    # BC428 line 80 turns positive at 25,551.25: the British Columbia part opens.
    (2025, 25_500): 10,
    # CPP2 starts at 71,300; the CPP base and enhanced rates end.
    (2025, 71_250): 10,
    # The federal 26% bracket starts at a taxable income of 114,750.
    (2025, 115_750): 10,
    # The British Columbia 7.7% bracket ends at a taxable income of 50,363.
    (2026, 50_750): 10,
    # The federal 20.5% bracket starts at a taxable income of 58,523.
    (2026, 59_000): 50,
    # The British Columbia 10.5% bracket ends at a taxable income of 115,648.
    (2026, 116_750): 10,
    # The British Columbia 12.29% bracket ends at a taxable income of 140,430.
    (2026, 141_500): 10,
    # The federal 29% bracket starts at a taxable income of 181,440.
    (2026, 182_500): 10,
    # The British Columbia 14.7% bracket ends at a taxable income of 190,405.
    (2026, 191_500): 10,
}
# (tax year, salary): the forward difference is not the derivative there. Each reason is the edge
# of a band at the salary, or a break inside the smallest run that avoids the cent rounding.
KNOWN_EXCEPTIONS: dict[tuple[int, int], str] = {
    (2025, 2_000): "the EI band starts: the rate at the edge is the lower band's (0)",
    (2026, 2_000): "the EI band starts: the rate at the edge is the lower band's (0)",
    (2025, 3_500): "the CPP exemption ends: the rate at the edge is the lower band's",
    (2026, 3_500): "the CPP exemption ends: the rate at the edge is the lower band's",
    (2026, 26_750): "BC428 line 80 turns positive 3 dollars up, at a salary of 26,752.96",
}

CASES = [
    pytest.param(year, salary, id=f"{year}-{salary}")
    for year in (2025, 2026)
    for salary in SALARIES
    if (year, salary) not in KNOWN_EXCEPTIONS
]


def _deductions(year: int, salary: Decimal) -> Decimal:
    worksheets = build_tax_computation().compute(
        TaxCalculationRequest(BRITISH_COLUMBIA, year, (Artifact(EMPLOYMENT_INCOME, salary),))
    )
    kinds = bundled_kinds()
    return sum(
        (worksheets[form][0].get(kinds.kind(kind)).value for form, kind in DEDUCTIONS), D("0")
    )


def _marginal_rate(year: int, salary: Decimal) -> Decimal:
    worksheets = build_tax_computation().compute(
        TaxCalculationRequest(BRITISH_COLUMBIA, year, (Artifact(EMPLOYMENT_INCOME, salary),))
    )
    value = worksheets[RETURN][0].get(bundled_kinds().kind(MARGINAL)).value
    assert isinstance(value, Decimal)
    return value


@pytest.mark.parametrize(("year", "salary"), CASES)
def test_the_marginal_rate_is_the_extra_dollar_change_in_the_take_home_deductions(
    year: int, salary: int
) -> None:
    step = NARROW_BAND_STEPS.get((year, salary), 100)
    extra_run = (_deductions(year, D(salary + step)) - _deductions(year, D(salary))) / step

    assert abs(_marginal_rate(year, D(salary)) - extra_run) <= TOLERANCE


def test_every_known_exception_is_a_salary_of_the_sweep() -> None:
    assert {salary for _year, salary in KNOWN_EXCEPTIONS} <= set(SALARIES)


def test_every_narrow_band_step_is_a_salary_of_the_sweep() -> None:
    assert {salary for _year, salary in NARROW_BAND_STEPS} <= set(SALARIES)
