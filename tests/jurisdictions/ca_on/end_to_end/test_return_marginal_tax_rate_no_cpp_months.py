"""The marginal tax rate of a filer with no CPP months, through the real Ontario return (2026).

Schedule 8 line A is 0 when the filer is not yet 18 in any month of 2026 (born 2009 or later) or
was 70 or older all of 2026 (born 1955 or earlier). The filer pays no CPP, so a further dollar of
salary is charged no CPP: only the EI of T2204 line 16 and the income tax are left. The return used
to raise at $0 and $2,000 to $2,033 and to count CPP at every other salary.

Hand-computed, 2026, salary only, no CPP: $2,000 is the first dollar of EI insurable earnings
(T2204 line 7 band), taken in full: 1. At $20,000 EI is 1.63%. Born 1955 the age amount covers
the income, so no income tax: 0.0163.
Born 2010 federal tax is paid on the whole dollar (no CPP is deducted) at 14%, less the credit on
the EI premium (14% x 1.63%), plus the EI itself: 0.14 - 0.002282 + 0.0163 = 0.1540 (Ontario tax
has not started). Born 2010 at $70,000 EI has stopped (maximum
$68,900): federal 20.5% plus Ontario 9.15%, each on the whole dollar since no CPP is deducted:
0.2965.
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
# (birth year, salary, rate). Born 1955 at $70,000 is left out: the age amount is still partly
# allowed there and its fall adds to the rate (checked against an extra run in
# `test_return_marginal_tax_rate_age_amount_extra_run.py`).
CASES = [
    (year, salary, rate)
    for year in (1955, 2010)
    for salary, rate in (("0", "0"), ("2000", "1"), ("2033", "1"))
] + [
    (1955, "20000", "0.0163"),
    (2010, "20000", "0.1540"),
    (2010, "70000", "0.2965"),
]


def _marginal(birth_year: int, salary: str) -> Decimal:
    worksheets = build_tax_computation().compute(
        TaxCalculationRequest(
            JurisdictionCode("CA-ON"),
            2026,
            (Artifact(EMPLOYMENT_INCOME, D(salary)), Artifact(BIRTH_YEAR, birth_year)),
        )
    )
    (summary,) = worksheets["ca-on/return"]
    value = summary.get(bundled_kinds().kind("ca-on/marginal_tax_rate")).value
    assert isinstance(value, Decimal)
    return value


@pytest.mark.parametrize(("birth_year", "salary", "rate"), CASES)
def test_the_marginal_rate_of_a_filer_with_no_cpp_months_has_no_cpp_in_it(
    birth_year: int, salary: str, rate: str
) -> None:
    assert _marginal(birth_year, salary).quantize(D("0.0001")) == D(rate)


@pytest.mark.parametrize("salary", ["20000", "70000"])
def test_a_filer_with_cpp_months_still_has_cpp_in_the_marginal_rate(salary: str) -> None:
    assert _marginal(1980, salary) > _marginal(2010, salary)
