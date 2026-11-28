"""The Ontario marginal rate of a filer born 1955 agrees with an extra run of the engine.

The age amount (ON428 line 10 and T1 line 30100) falls by 15% of the net income over its threshold,
which is tax at the credit rate on each further dollar. The marginal rate calculates that fall from
the forms' rates (`test_return_marginal_tax_rate_age_amount.py` pins the Ontario part by hand). This
test is the independent check, like `test_return_marginal_tax_rate_extra_run.py`: it runs the real
engine for a filer born 1955 at a salary and at the salary plus $100, and compares the change in
the take-home deductions per dollar with the rate the return calculated at the salary, for 2025 and
2026, with the age amounts of both the federal and the Ontario forms falling.

The sweep stays $100 or more away from the salaries where an age amount reaches 0 (about $88,900 in
2025 and $89,500 in 2026 for Ontario; the federal amount falls to 0 further up), and from the
salaries where it starts to fall, so the forward difference is the derivative.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine import build_tax_computation
from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.application.models.calculation_result import TaxCalculationResult
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca.catalog.personal_amounts import BIRTH_YEAR
from tests.kinds import bundled_kinds

D = Decimal
ONTARIO = JurisdictionCode("CA-ON")
RETURN = "ca-on/return"
MARGINAL = "ca-on/marginal_tax_rate"
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

# Under, inside and over the age amount's fall, away from its start and its end.
SALARIES = (
    30_000,
    40_000,
    44_000,
    50_000,
    55_000,
    60_000,
    65_000,
    70_000,
    75_000,
    80_000,
    85_000,
    95_000,
    100_000,
    110_000,
    120_000,
)

CASES = [
    pytest.param(year, birth_year, salary, id=f"{year}-{birth_year}-{salary}")
    for year in (2025, 2026)
    for birth_year in (1955, 1980)
    for salary in SALARIES
]


def _computed(year: int, birth_year: int, salary: Decimal) -> TaxCalculationResult:
    return build_tax_computation().compute(
        TaxCalculationRequest(
            ONTARIO,
            year,
            (Artifact(EMPLOYMENT_INCOME, salary), Artifact(BIRTH_YEAR, birth_year)),
        )
    )


def _deductions(year: int, birth_year: int, salary: Decimal) -> Decimal:
    worksheets = _computed(year, birth_year, salary)
    kinds = bundled_kinds()
    return sum(
        (worksheets[form][0].get(kinds.kind(kind)).value for form, kind in DEDUCTIONS), D("0")
    )


def _marginal_rate(year: int, birth_year: int, salary: Decimal) -> Decimal:
    value = _computed(year, birth_year, salary)[RETURN][0].get(bundled_kinds().kind(MARGINAL)).value
    assert isinstance(value, Decimal)
    return value


@pytest.mark.parametrize(("year", "birth_year", "salary"), CASES)
def test_the_marginal_rate_with_an_age_amount_is_the_extra_dollar_change_in_the_deductions(
    year: int, birth_year: int, salary: int
) -> None:
    extra_run = (
        _deductions(year, birth_year, D(salary + STEP)) - _deductions(year, birth_year, D(salary))
    ) / STEP

    assert abs(_marginal_rate(year, birth_year, D(salary)) - extra_run) <= TOLERANCE
