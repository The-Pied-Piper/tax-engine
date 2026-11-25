"""The Alberta marginal rate agrees with an extra run of the engine, for 2025 and 2026.

The marginal rate (`ca-ab/marginal_tax_rate`) is the change in the take-home deductions per extra
dollar of salary: T1 line 43500 "Total payable" plus the CPP base contribution (Schedule 8 line 25),
the CPP enhanced contribution (line 12 of Part 3), the CPP2 contribution (line 22) and the EI
premium of T2204 line 16, for a salary-only filer. The return calculates it with the rates of the
forms, and runs nothing twice. This test is the independent check: it runs the real engine at a
salary and at the salary plus a step, and compares the change in those deductions per dollar with
the rate the return calculated at the salary.

The step is $100 (and $1 or $10 at the salaries inside the EI band of T2204 line 16, $2,000 to
$2,033). A sweep of every $250 from $1,000 to $400,000 in both years agreed everywhere except at the
salaries in `KNOWN_EXCEPTIONS`: there the run of $100 crosses a break in the rate, so the forward
difference is not the derivative. Each is listed with its break and run again with a step that stays
inside the band (`SMALLER_STEPS`), at which the rate agrees. A step below $10 is not used where a
break is not near: the cent rounding of the forms' lines moves a forward difference by more than the
tolerance. The salaries that sit exactly on the edge of a band ($2,000, $3,500, $71,300, $81,200)
are pinned by value in `test_return_marginal_tax_rate_values.py`: a CPP band reads its own rate
from its lower edge and 0 from its upper edge (the CPP rates are on at $3,500, and at $71,300 the
CPP2 rate is on while the base and first additional rates are 0), the EI rate is 0 at $2,000, and
any run goes into the next band. The list is not exhaustive: a sweep from another
offset meets other band edges (the federal brackets near $57,900, $178,900 and $254,400, the EI
maximum near $65,700, the CPP2 start near $81,200 in 2025 and $85,000 in 2026), each a break of the
same kind.
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
ALBERTA = JurisdictionCode("CA-AB")
RETURN = "ca-ab/return"
MARGINAL = "ca-ab/marginal_tax_rate"
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
    5_000,
    8_000,
    10_000,
    15_000,
    18_750,
    19_000,
    19_150,
    19_300,
    21_000,
    23_000,
    23_900,
    23_960,
    24_400,
    24_430,
    26_000,
    31_000,
    36_000,
    45_000,
    50_000,
    55_000,
    58_000,
    59_000,
    60_500,
    61_750,
    65_000,
    70_000,
    71_250,
    75_000,
    80_000,
    100_000,
    115_750,
    120_000,
    140_000,
    152_250,
    155_350,
    160_000,
    175_000,
    182_500,
    186_200,
    190_000,
    200_000,
    230_000,
    243_000,
    247_900,
    250_000,
    300_000,
    350_000,
    364_000,
    371_300,
    400_000,
)
# A smaller step inside the EI band of T2204 line 16, so the extra run does not cross its ends.
NARROW_BAND_STEPS = {1_999: 1, 2_001: 10, 2_020: 10}
# (tax year, salary): the break inside the run of $100, where the forward difference is not the
# derivative. The same salary has a smaller step in `SMALLER_STEPS`, inside the band, where the rate
# agrees.
KNOWN_EXCEPTIONS: dict[tuple[int, int], str] = {
    (2025, 18_750): "federal tax (T1 line 42900) first above zero, at $18,820.27",
    (2025, 23_900): "Alberta tax (AB428 line 68) first above zero, at $23,931.13",
    (2025, 60_500): "taxable income passes $60,000, the end of the Alberta 8% bracket",
    (2025, 71_250): "the CPP base stops at the maximum pensionable earnings, $71,300",
    (2025, 115_750): "federal bracket ends at taxable income $114,750 (salary about $115,800)",
    (2025, 152_250): "taxable income passes $151,234, the end of the Alberta 10% bracket",
    (2025, 182_500): "taxable income passes $181,481, the end of the Alberta 12% bracket",
    (2025, 243_000): "taxable income passes $241,974, the end of the Alberta 13% bracket",
    (2025, 364_000): "taxable income passes $362,961, the end of the Alberta 14% bracket",
    (2026, 19_150): "federal tax (T1 line 42900) first above zero, at $19,200.18",
    (2026, 24_400): "Alberta tax (AB428 line 68) first above zero, at $24,411.18",
    (2026, 59_000): "federal bracket ends at taxable income $58,523 (salary about $59,050)",
    (2026, 61_750): "taxable income passes $61,200, the end of the Alberta 8% bracket",
    (2026, 182_500): "federal bracket ends at taxable income $181,440 (salary about $182,500)",
    (2026, 155_350): "taxable income passes $154,259, the end of the Alberta 10% bracket",
    (2026, 186_200): "taxable income passes $185,111, the end of the Alberta 12% bracket",
    (2026, 247_900): "taxable income passes $246,813, the end of the Alberta 13% bracket",
    (2026, 371_300): "taxable income passes $370,220, the end of the Alberta 14% bracket",
}
SMALLER_STEPS = {
    (2025, 18_750): 10,
    (2025, 23_900): 25,
    (2025, 60_500): 10,
    (2025, 71_250): 10,
    (2025, 115_750): 10,
    (2025, 152_250): 10,
    (2025, 182_500): 10,
    (2025, 243_000): 10,
    (2025, 364_000): 10,
    (2026, 19_150): 10,
    (2026, 24_400): 10,
    (2026, 59_000): 10,
    (2026, 61_750): 10,
    (2026, 182_500): 10,
    (2026, 155_350): 10,
    (2026, 186_200): 10,
    (2026, 247_900): 10,
    (2026, 371_300): 10,
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
        TaxCalculationRequest(ALBERTA, year, (Artifact(EMPLOYMENT_INCOME, salary),))
    )
    kinds = bundled_kinds()
    return sum(
        (worksheets[form][0].get(kinds.kind(kind)).value for form, kind in DEDUCTIONS), D("0")
    )


def _marginal_rate(year: int, salary: Decimal) -> Decimal:
    worksheets = build_tax_computation().compute(
        TaxCalculationRequest(ALBERTA, year, (Artifact(EMPLOYMENT_INCOME, salary),))
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
