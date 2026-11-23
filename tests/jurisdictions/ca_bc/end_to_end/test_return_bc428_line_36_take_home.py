"""A salary-only $70,000 British Columbia run is unchanged by the line 36 maximum.

Line 36, the pension income amount, now passes through a `core/at_most` against the printed
maximum ($1,000); a salary-only caller leaves it out, the input reads it as blank, line 36 passes
the blank on, and the take-home does not move: 54,217.74 for 2025 and 54,348.15 for 2026
(carried-forward, provisional datasets). British Columbia has no 2026 manifest, so 2026 reads the
2025 manifest and each dataset by its exact year.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine import build_tax_computation
from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.registrations import artifact_kinds

D = Decimal
BRITISH_COLUMBIA = JurisdictionCode("CA-BC")
LINE_36 = "ca-bc/bc428_pension_income_amount_line_36"


@pytest.mark.parametrize(("year", "take_home"), [(2025, "54217.74"), (2026, "54348.15")])
def test_the_70000_salary_only_take_home_is_unchanged(year: int, take_home: str) -> None:
    kinds = artifact_kinds()
    worksheets = build_tax_computation().compute(
        TaxCalculationRequest(BRITISH_COLUMBIA, year, (Artifact(EMPLOYMENT_INCOME, D("70000")),))
    )
    (summary,) = worksheets["ca-bc/return"]
    (schedule_8,) = worksheets["ca/schedule_8"]
    (t2204,) = worksheets["ca/t2204"]
    (bc428,) = worksheets["ca-bc/bc428"]
    cpp = sum(
        (
            schedule_8.get(kinds.kind(name)).value
            for name in (
                "ca/schedule_8_cpp_base_contributions_on_return",
                "ca/schedule_8_cpp_enhanced_contributions_on_return",
            )
        ),
        D("0"),
    )
    ei = t2204.get(kinds.kind("ca/t2204_premiums_deducted")).value
    total_tax = summary.get(kinds.kind("ca/refund_or_balance_owing")).value

    assert D("70000") - cpp - ei - total_tax == D(take_home)
    assert bc428.get(kinds.kind(LINE_36)).is_blank
