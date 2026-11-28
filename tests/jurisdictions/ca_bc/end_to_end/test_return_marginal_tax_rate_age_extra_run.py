"""The marginal rate of a British Columbia filer born in 1955 agrees with an extra run.

The same independent check as `test_return_marginal_tax_rate_extra_run.py` (the change in T1 line
43500 "Total payable", the CPP base, enhanced and CPP2 contributions and the EI premium per further
dollar of salary, against the rate the return calculates), for a filer who claims the age amount,
so the fall of the age amount over its threshold (43,169 in 2025, 44,119 in 2026, until the credit
is 0 at a net income of about 81,829 and 83,632) is in the rate, with the federal fall over its own
threshold (45,522 and 46,432) beside it. In 2026 a filer born in 1955 pays no CPP, so the salary is
the net income. The step is $100 everywhere: the
salaries sit below, in and above the range, and no $100 run crosses a break (the age threshold, the
point where the credit reaches 0, a bracket edge, the CPP and EI maximums); the edges themselves
are pinned to the cent in `test_return_marginal_tax_rate_age.py`.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine import build_tax_computation
from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca.catalog.personal_amounts import BIRTH_YEAR
from tests.kinds import bundled_kinds

D = Decimal
BRITISH_COLUMBIA = JurisdictionCode("CA-BC")
RETURN = "ca-bc/return"
MARGINAL = "ca-bc/marginal_tax_rate"
TOLERANCE = D("0.001")
BORN = 1955
DEDUCTIONS = (
    ("ca/t1_tax_and_credits", "ca/total_payable"),
    ("ca/schedule_8", "ca/schedule_8_cpp_base_contributions_on_return"),
    ("ca/schedule_8", "ca/cpp_part_3_line_12"),
    ("ca/schedule_8", "ca/cpp_part_3_line_22"),
    ("ca/t2204", "ca/t2204_line_16"),
)

SALARIES = {
    2025: (
        40_000,
        43_000,
        43_700,
        45_000,
        47_000,
        50_000,
        55_000,
        57_000,
        60_000,
        65_000,
        70_000,
        75_000,
        80_000,
        82_000,
        82_800,
        83_000,
        90_000,
    ),
    2026: (
        40_000,
        43_000,
        44_200,
        45_000,
        47_000,
        50_000,
        55_000,
        58_000,
        60_000,
        65_000,
        68_000,
        70_000,
        80_000,
        83_000,
        83_500,
        84_000,
        90_000,
    ),
}
CASES = [
    pytest.param(year, salary, id=f"{year}-{salary}")
    for year, salaries in SALARIES.items()
    for salary in salaries
]


def _deductions(year: int, salary: Decimal) -> Decimal:
    worksheets = build_tax_computation().compute(
        TaxCalculationRequest(
            BRITISH_COLUMBIA,
            year,
            (Artifact(EMPLOYMENT_INCOME, salary), Artifact(BIRTH_YEAR, BORN)),
        )
    )
    kinds = bundled_kinds()
    return sum(
        (worksheets[form][0].get(kinds.kind(kind)).value for form, kind in DEDUCTIONS), D("0")
    )


def _marginal_rate(year: int, salary: Decimal) -> Decimal:
    worksheets = build_tax_computation().compute(
        TaxCalculationRequest(
            BRITISH_COLUMBIA,
            year,
            (Artifact(EMPLOYMENT_INCOME, salary), Artifact(BIRTH_YEAR, BORN)),
        )
    )
    value = worksheets[RETURN][0].get(bundled_kinds().kind(MARGINAL)).value
    assert isinstance(value, Decimal)
    return value


@pytest.mark.parametrize(("year", "salary"), CASES)
def test_the_marginal_rate_is_the_extra_dollar_change_in_the_deductions_of_a_filer_born_1955(
    year: int, salary: int
) -> None:
    step = 100
    extra_run = (_deductions(year, D(salary + step)) - _deductions(year, D(salary))) / step

    assert abs(_marginal_rate(year, D(salary)) - extra_run) <= TOLERANCE
