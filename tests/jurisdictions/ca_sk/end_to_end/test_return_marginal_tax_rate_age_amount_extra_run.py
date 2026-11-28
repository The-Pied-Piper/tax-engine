"""The marginal rate of an aged filer agrees with an extra run of the engine.

Same check as `test_return_marginal_tax_rate_extra_run.py`, with an aged filer (no CPP, so
the net income is the salary): the change in T1 line 43500 plus the EI premium (T2204 line 16) per
further dollar over a run of $100 against the rate the return calculated. The salaries are in
Saskatchewan's age amount range (over the threshold of 43,066 and 43,927, under the end of the
amount at 81,633 and 83,267) and beyond it, and are chosen so that the run of $100 crosses none of
the breaks (the federal age threshold at 45,522 and 46,432, the Saskatchewan column at 53,463 and
54,532, the federal bracket at 57,375 and 58,523, the EI maximum at 65,700 and 68,900, the end of
the age amount).
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine import build_tax_computation
from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca.catalog.personal_amounts import BIRTH_YEAR
from tests.kinds import bundled_kinds

D = Decimal
SASKATCHEWAN = JurisdictionCode("CA-SK")
RETURN = "ca-sk/return"
MARGINAL = "ca-sk/marginal_tax_rate"
TOLERANCE = D("0.001")
# Born 1950 in 2025 and 1955 in 2026: no CPP months in either year (born 1955 turns 70 in 2025).
AGED = {2025: 1950, 2026: 1955}
DEDUCTIONS = (
    ("ca/t1_tax_and_credits", "ca/total_payable"),
    ("ca/t2204", "ca/t2204_line_16"),
)
CASES = [
    pytest.param(year, salary, id=f"{year}-{salary}")
    for year, salaries in (
        (2025, (40_000, 44_000, 50_000, 56_000, 60_000, 64_000, 70_000, 80_000, 90_000)),
        (2026, (40_000, 44_500, 50_000, 56_000, 62_000, 66_000, 70_000, 80_000, 90_000)),
    )
    for salary in salaries
]


def _sheet(year: int, salary: Decimal, form: str) -> Worksheet:
    worksheets = build_tax_computation().compute(
        TaxCalculationRequest(
            SASKATCHEWAN,
            year,
            (Artifact(EMPLOYMENT_INCOME, salary), Artifact(BIRTH_YEAR, AGED[year])),
        )
    )
    return worksheets[form][0]


def _deductions(year: int, salary: Decimal) -> Decimal:
    kinds = bundled_kinds()
    return sum(
        (_sheet(year, salary, form).get(kinds.kind(kind)).value for form, kind in DEDUCTIONS),
        D("0"),
    )


@pytest.mark.parametrize(("year", "salary"), CASES)
def test_born_1955_the_marginal_rate_is_the_extra_dollar_change_in_the_deductions(
    year: int, salary: int
) -> None:
    extra_run = (_deductions(year, D(salary + 100)) - _deductions(year, D(salary))) / 100
    rate = _sheet(year, D(salary), RETURN).get(bundled_kinds().kind(MARGINAL)).value

    assert abs(rate - extra_run) <= TOLERANCE
