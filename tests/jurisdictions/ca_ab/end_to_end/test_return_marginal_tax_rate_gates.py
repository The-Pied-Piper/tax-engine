"""The two gates of the Alberta marginal rate open at the zero-tax boundaries, both years.

The federal part (`ca-ab/marginal_federal_rate`, gated in the federal form on T1 line 42900 "Basic
federal tax") and the Alberta part (`ca-ab/alberta_marginal_rate`, gated on AB428 line 68) are each
0 while their own tax is 0.00 and count from the first cent of tax. The boundaries were measured by
running the real return cent by cent: the part is 0 one cent below and counts at the cent pinned.
The 2025 Alberta line 68 is not monotone just under its boundary because of cent rounding: it is
0.01 from 23,931.13 to 23,931.21, 0.00 from 23,931.22 to 23,931.24 and 0.01 from 23,931.25 on, so
the cents pinned there are a closed and an open point, not the first salary with tax.

The Alberta part is 0 while the Alberta tax is 0 even though the federal part already counts; the
federal part is 0 below its own boundary.
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
FEDERAL_PART = "ca-ab/marginal_federal_rate"
ALBERTA_PART = "ca-ab/alberta_marginal_rate"

# Year, salary, whether the federal part counts, whether the Alberta part counts.
BOUNDARIES = [
    (2025, "18820.26", False, False),
    (2025, "18820.27", True, False),
    (2025, "23931.12", True, False),
    (2025, "23931.13", True, True),
    (2025, "23931.21", True, True),
    (2025, "23931.22", True, False),
    (2025, "23931.24", True, False),
    (2025, "23931.25", True, True),
    (2026, "19200.17", False, False),
    (2026, "19200.18", True, False),
    (2026, "24411.17", True, False),
    (2026, "24411.18", True, True),
]


def _part(year: int, salary: str, name: str) -> Decimal:
    worksheets = build_tax_computation().compute(
        TaxCalculationRequest(ALBERTA, year, (Artifact(EMPLOYMENT_INCOME, D(salary)),))
    )
    (summary,) = worksheets["ca-ab/return"]
    value = summary.get(bundled_kinds().kind(name)).value
    assert isinstance(value, Decimal)
    return value


@pytest.mark.parametrize(("year", "salary", "federal", "alberta"), BOUNDARIES)
def test_each_part_counts_only_where_its_own_tax_is_above_zero(
    year: int, salary: str, federal: bool, alberta: bool
) -> None:
    assert (_part(year, salary, FEDERAL_PART) > 0) is federal
    assert (_part(year, salary, ALBERTA_PART) > 0) is alberta
