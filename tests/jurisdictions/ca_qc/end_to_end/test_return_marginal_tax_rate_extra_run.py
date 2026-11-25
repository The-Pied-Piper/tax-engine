"""The Quebec marginal rate agrees with an extra run of the engine, for 2025 and 2026.

The marginal rate (`ca-qc/marginal_tax_rate`) is the change in the take-home deductions per extra
dollar of salary: 5005-R line 43500 "Total payable" plus TP-1 line 450, less the refundable Quebec
abatement of line 44000 (together the return's `ca-qc/income_tax_after_abatement`), the QPP base
contribution (Schedule 8 line 25), the QPP enhanced contribution (line 12 of Part 3), the QPP2
contribution (line 22), the EI premium of T2204 line 16 and the QPIP premium (5005-R line 91), for a
salary-only filer. The return calculates it with the rates of the forms, and runs nothing twice. This test is the independent check: it runs the real
engine at a salary and at the salary plus a step, and compares the change in those deductions per
dollar with the rate the return calculated at the salary.

The step is $100. The EI band of T2204 line 16 (line 7, line 3 less $2,000, rises $1 for each $1
until it meets the premium: $2,026 for Quebec residents, T2204 note 3) and the QPIP threshold
($2,000, below which line 91 is 0) are narrower than that, so the salaries inside or just under
them use a smaller step ($10 at $2,001, $5 at $2,020). Elsewhere the step is $100: the cent
rounding of the forms' lines (about a cent for each of the tax lines) moves a forward difference
by more than the tolerance when the step is about $5 or less. A salary with a break in the rate a
few dollars to $99 above it (a bracket column, the QPP maximum, the start of a tax) uses the
largest step that stays under the break (`BREAK_STEPS`), found by a sweep every $250 from $1,000
to $400,000 in both years. A salary that is itself a band edge, where the published rate is the
lower band's, is listed in `KNOWN_EXCEPTIONS` with the reason; the list is short and each entry is
a salary where the forward difference is not the derivative.
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
    ("ca-qc/return", "ca-qc/income_tax_after_abatement"),
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
    2_000,
    2_001,
    2_020,
    3_000,
    3_500,
    5_000,
    8_000,
    10_000,
    12_000,
    15_000,
    17_000,
    19_000,
    19_250,
    20_000,
    20_250,
    21_000,
    22_000,
    23_500,
    25_000,
    26_500,
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
    56_250,
    57_000,
    59_000,
    60_000,
    65_000,
    70_000,
    71_000,
    71_250,
    75_000,
    80_000,
    85_000,
    90_000,
    97_900,
    100_000,
    110_000,
    111_250,
    114_000,
    115_750,
    120_000,
    128_000,
    132_000,
    134_750,
    150_000,
    175_000,
    182_500,
    190_000,
    250_000,
    300_000,
    400_000,
)
# A smaller step near a narrow band, so the extra run does not cross the band's end.
NARROW_BAND_STEPS = {2_001: 10, 2_020: 5}
# (tax year, salary): a salary with a break in the rate a few dollars to $99 above it, found by a
# sweep every $250 from $1,000 to $400,000 in both years. The step stays under the break, and the
# rate then agrees with the extra run. Each entry names its break: the start of a federal, Quebec
# or Schedule K bracket column, the QPP maximum, or the start of a tax.
BREAK_STEPS: dict[tuple[int, int], int] = {
    (2025, 26_500): 20,  # Schedule K line 48 reaches $5,000: column A (7.84%) ends, column B starts
    (2025, 71_250): 20,  # QPP base ends at the $71,300 maximum
    (2025, 115_750): 20,  # taxable income reaches the 5005-R $114,750 column
    (2025, 132_000): 50,  # TP-1 taxable income reaches the $129,590 Quebec column
    (2026, 19_250): 20,  # the federal tax starts (T1 line 42900 above 0)
    (2026, 20_250): 20,  # the Quebec tax starts (TP-1 line 432 above 0)
    (2026, 26_500): 20,  # Schedule K line 48 reaches $5,000
    (2026, 56_250): 20,  # taxable income reaches the Quebec second column
    (2026, 59_000): 20,  # taxable income reaches the 5005-R second column
    (2026, 111_250): 5,  # a break a few dollars above (the Quebec third column); the step is wide
    # enough that the cent rounding of the abatement stays under the tolerance
    (2026, 134_750): 50,  # TP-1 taxable income reaches the Quebec fourth column
    (2026, 182_500): 20,  # taxable income reaches the 5005-R fourth column
}
# (tax year, salary): the forward difference is not the derivative there. Each reason is a break in
# the rate inside the run.
KNOWN_EXCEPTIONS: dict[tuple[int, int], str] = {
    (2025, 1_999): "line 91 is 0 under $2,000 and $9.88 from $2,000: a jump, not a rate",
    (2025, 2_000): "an exact band edge: the published rate is the lower band's EI rate (0), the "
    "extra run is in the $1 for $1 band of T2204 line 7",
    (2026, 1_999): "line 91 is 0 under $2,000 and $8.60 from $2,000: a jump, not a rate",
    (2026, 2_000): "an exact band edge: the published rate is the lower band's EI rate (0), the "
    "extra run is in the $1 for $1 band of T2204 line 7",
    (2025, 3_500): "an exact band edge: the published rate is the lower band's (QPP 0%)",
    (2026, 3_500): "an exact band edge: the published rate is the lower band's (QPP 0%)",
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
    step = BREAK_STEPS.get((year, salary), NARROW_BAND_STEPS.get(salary, 100))
    extra_run = (_deductions(year, D(salary + step)) - _deductions(year, D(salary))) / step

    assert abs(_marginal_rate(year, D(salary)) - extra_run) <= TOLERANCE


def test_every_known_exception_is_a_salary_of_the_sweep() -> None:
    assert {salary for _year, salary in KNOWN_EXCEPTIONS} <= set(SALARIES)
