"""The marginal tax rate of a Quebec filer with no QPP months, through the Quebec return (2026).

A filer not yet 18 in any month of 2026 (born 2009 or later) has Schedule 8 line A = 0 and pays no
QPP, so a further dollar of salary is charged none. The return used to raise at $0 and at $2,000.
A filer with QPP months is unchanged: the no-QPP rate is the lower of the two wherever QPP applies.
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
SALARIES = ["0", "2000", "2033", "20000", "70000"]


def _marginal(birth_year: int, salary: str) -> Decimal:
    worksheets = build_tax_computation().compute(
        TaxCalculationRequest(
            JurisdictionCode("CA-QC"),
            2026,
            (Artifact(EMPLOYMENT_INCOME, D(salary)), Artifact(BIRTH_YEAR, birth_year)),
        )
    )
    (summary,) = worksheets["ca-qc/return"]
    value = summary.get(bundled_kinds().kind("ca-qc/marginal_tax_rate")).value
    assert isinstance(value, Decimal)
    return value


@pytest.mark.parametrize("salary", SALARIES)
def test_the_return_runs_for_a_filer_born_in_2010(salary: str) -> None:
    assert _marginal(2010, salary) >= D("0")


@pytest.mark.parametrize("salary", ["0", "2000", "2033"])
def test_below_the_qpp_exemption_the_rate_is_the_same_with_or_without_qpp_months(
    salary: str,
) -> None:
    assert _marginal(2010, salary) == _marginal(1980, salary)


@pytest.mark.parametrize("salary", ["20000", "70000"])
def test_a_filer_with_qpp_months_has_qpp_in_the_marginal_rate(salary: str) -> None:
    assert _marginal(1980, salary) > _marginal(2010, salary)
