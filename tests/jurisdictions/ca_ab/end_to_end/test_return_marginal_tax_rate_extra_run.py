"""The Alberta marginal rate agrees with an extra run of the engine, for 2025 and 2026.

The marginal rate (`ca-ab/marginal_tax_rate`) is the change in the take-home deductions per extra
dollar of salary: T1 line 43500 "Total payable" plus the CPP base contribution (Schedule 8 line 25),
the CPP enhanced contribution (line 12 of Part 3), the CPP2 contribution (line 22) and the EI
premium of T2204 line 16, for a salary-only filer. The return calculates it with the rates of the
forms, and runs nothing twice. This test is the independent check: it runs the real engine at a
salary and at the salary plus a step, and compares the change in those deductions per dollar with
the rate the return calculated at the salary.

The step is $100. A salary whose run of $100 crosses a break in the rate (a bracket edge, the CPP
or EI limits, the zero-tax boundaries) is in `BREAK_STEPS` with a smaller step that stays inside
one band, and the reason. A rate is a slope with a real value inside each band, so with the smaller
step the engine and the extra run agree to the same tolerance. At a salary that is exactly the
start of a band ($2,000 of EI, the $3,500 CPP exemption) the published rate is the
lower band's, so the step is negative (the change from just below).

The sweep that found these salaries ran every $250 from $1,000 to $400,000 for both years (3,194
runs of the engine, each against its extra run): only the 15 salaries below disagreed with a step
of $100, and each agrees with the step given.
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
    19_000,
    21_000,
    23_000,
    26_000,
    31_000,
    36_000,
    45_000,
    50_000,
    55_000,
    58_000,
    65_000,
    70_000,
    75_000,
    80_000,
    100_000,
    120_000,
    140_000,
    160_000,
    175_000,
    190_000,
    200_000,
    230_000,
    250_000,
    300_000,
    350_000,
    400_000,
)
# (tax year, salary): (step, reason). A negative step is the change from just below the salary.
BREAK_STEPS: dict[tuple[int, int], tuple[int, str]] = {
    (2025, 1_999): (1, "the EI premium starts above $2,000"),
    (2026, 1_999): (1, "the EI premium starts above $2,000"),
    (2025, 2_001): (10, "just above the EI start; a step of $100 would pass the $2,033 maximum"),
    (2026, 2_001): (10, "just above the EI start; a step of $100 would pass the $2,033 maximum"),
    (2025, 2_020): (10, "EI reaches its maximum at about $2,033"),
    (2026, 2_020): (10, "EI reaches its maximum at about $2,033"),
    (2025, 2_000): (-10, "exactly where the EI premium starts; the rate is the lower band's"),
    (2026, 2_000): (-10, "exactly where the EI premium starts; the rate is the lower band's"),
    (2025, 3_500): (-10, "exactly where CPP contributions start (the $3,500 exemption)"),
    (2026, 3_500): (-10, "exactly where CPP contributions start (the $3,500 exemption)"),
    (2025, 18_750): (10, "federal tax starts at $18,820.27, inside a step of $100"),
    (2025, 60_500): (10, "taxable income passes the $60,000 edge of the Alberta 8% bracket"),
    (2026, 59_000): (10, "taxable income passes the federal 14% bracket edge of $58,523"),
    (2026, 61_750): (10, "taxable income passes the $61,200 edge of the Alberta 8% bracket"),
    (2025, 71_250): (10, "the CPP base stops at the $71,300 maximum pensionable earnings"),
    (2025, 115_750): (10, "taxable income passes the federal 20.5% bracket edge of $114,750"),
    (2025, 152_250): (10, "taxable income passes the $151,234 edge of the Alberta 10% bracket"),
    (2025, 182_500): (10, "taxable income passes the $181,481 edge of the Alberta 12% bracket"),
    (2026, 182_500): (10, "taxable income passes the federal 26% bracket edge of $181,440"),
    (2025, 243_000): (10, "taxable income passes the $241,974 edge of the Alberta 13% bracket"),
    (2025, 364_000): (10, "taxable income passes the $362,961 edge of the Alberta 14% bracket"),
}

CASES = [
    pytest.param(year, salary, id=f"{year}-{salary}")
    for year in (2025, 2026)
    for salary in sorted({*SALARIES, *(s for y, s in BREAK_STEPS if y == year)})
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
    step, _reason = BREAK_STEPS.get((year, salary), (100, ""))
    if step > 0:
        extra_run = (_deductions(year, D(salary + step)) - _deductions(year, D(salary))) / step
    else:
        extra_run = (_deductions(year, D(salary)) - _deductions(year, D(salary + step))) / -step

    assert abs(_marginal_rate(year, D(salary)) - extra_run) <= TOLERANCE


def test_every_break_step_is_for_a_tax_year_of_the_sweep() -> None:
    assert {year for year, _salary in BREAK_STEPS} == {2025, 2026}
