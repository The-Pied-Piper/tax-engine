"""The Quebec marginal rate agrees with an extra run of the engine, for 2025 and 2026.

The marginal rate (`ca-qc/marginal_tax_rate`) is the change in the take-home deductions per extra
dollar of salary: 5005-R line 43500 "Total payable" plus TP-1 line 450 (both in the return's
`ca-qc/total_payable`), the QPP base contribution (Schedule 8 line 25), the QPP enhanced
contribution (line 12 of Part 3), the QPP2 contribution (line 22), the EI premium of T2204 line 16
and the QPIP premium (5005-R line 91), for a salary-only filer. The return calculates it with the
rates of the forms, and runs nothing twice. This test is the independent check: it runs the real
engine at a salary and at the salary plus a step, and compares the change in those deductions per
dollar with the rate the return calculated at the salary.

The step is $100. The EI band of T2204 line 16 ($2,000 to $2,033) and the QPIP threshold ($2,000,
below which line 91 is 0) are narrower than that, so the salaries inside or just under them use a
smaller step ($10, and $1 at $1,999, where a step of $10 would cross $2,000). A step smaller than
$10 or $100 is not used elsewhere, since the cent rounding of the forms' lines (about a cent for
each of the tax lines) moves a forward difference by more than the tolerance when the step is $10
or less. The other narrow bands (the start of the federal and the Quebec tax, the start and the
maximum of the prescription drug insurance premium, the maximum of the deduction for workers) are
in the sweep at salaries just under their start, where $100 does not reach them. A salary whose
run still crosses a break in the rate is listed in `KNOWN_EXCEPTIONS` with the reason; the list is
short and each entry is a salary where the forward difference is not the derivative.
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
QUEBEC = JurisdictionCode("CA-QC")
RETURN = "ca-qc/return"
MARGINAL = "ca-qc/marginal_tax_rate"
TOLERANCE = D("0.001")
# The take-home deductions, as the manifest's `take_home` block names them.
DEDUCTIONS = (
    ("ca-qc/return", "ca-qc/total_payable"),
    ("ca/schedule_8", "ca/schedule_8_cpp_base_contributions_on_return"),
    ("ca/schedule_8", "ca/cpp_part_3_line_12"),
    ("ca/schedule_8", "ca/cpp_part_3_line_22"),
    ("ca/t2204", "ca/t2204_line_16"),
    ("ca-qc/ppip_premium", "ca-qc/ppip_premiums_paid"),
)

SALARIES = (
    1_000,
    1_250,
    1_500,
    1_750,
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
    20_000,
    21_000,
    22_000,
    23_500,
    25_000,
    27_000,
    29_000,
    31_000,
    33_000,
    36_000,
    40_000,
    45_000,
    50_000,
    52_000,
    55_000,
    57_000,
    60_000,
    65_000,
    70_000,
    71_000,
    75_000,
    80_000,
    85_000,
    90_000,
    97_900,
    100_000,
    110_000,
    114_000,
    120_000,
    128_000,
    150_000,
    175_000,
    190_000,
    250_000,
    300_000,
    400_000,
)
# A smaller step near a narrow band, so the extra run does not cross the band's end.
NARROW_BAND_STEPS = {2_001: 10, 2_020: 5}
# (tax year, salary): the forward difference is not the derivative there. Each reason is a break in
# the rate inside the run.
KNOWN_EXCEPTIONS: dict[tuple[int, int], str] = {
    (
        2025,
        1_999,
    ): "line 91 is 0 under $2,000 of insurable earnings and $9.88 (0.494%) from $2,000: a jump, "
    "not a rate",
    (
        2026,
        1_999,
    ): "line 91 is 0 under $2,000 of insurable earnings and $8.60 (0.430%) from $2,000: a jump, "
    "not a rate",
}

CASES = [
    pytest.param(year, salary, id=f"{year}-{salary}")
    for year in (2025, 2026)
    for salary in SALARIES
    if (year, salary) not in KNOWN_EXCEPTIONS
]


def _deductions(year: int, salary: Decimal) -> Decimal:
    worksheets = build_tax_computation().compute(
        TaxCalculationRequest(QUEBEC, year, (Artifact(EMPLOYMENT_INCOME, salary),))
    )
    kinds = bundled_kinds()
    return sum(
        (worksheets[form][0].get(kinds.kind(kind)).value for form, kind in DEDUCTIONS), D("0")
    )


def _marginal_rate(year: int, salary: Decimal) -> Decimal:
    worksheets = build_tax_computation().compute(
        TaxCalculationRequest(QUEBEC, year, (Artifact(EMPLOYMENT_INCOME, salary),))
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


def test_every_known_exception_is_a_salary_of_the_sweep() -> None:
    assert {salary for _year, salary in KNOWN_EXCEPTIONS} <= set(SALARIES)
