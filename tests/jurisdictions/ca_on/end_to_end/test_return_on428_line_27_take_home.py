"""A salary-only $70,000 Ontario run is unchanged by the line 27 maximum.

Line 27, the pension income amount, now passes through a `core/at_most` against the printed
maximum ($1,762); a salary-only caller leaves it out, it reads 0, and the take-home does not move:
53,468.68 for 2025 (also pinned in `test_return_marginal_tax_rate.py`) and 53,786.25 for 2026
(carried-forward, provisional datasets). The 2026 run needs the 2026 maximum dataset: Ontario has no
2026 manifest, so 2026 reads the 2025 manifest and each dataset by its exact year.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine import build_tax_computation
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tests.kinds import bundled_kinds

D = Decimal
ONTARIO = JurisdictionCode("CA-ON")


@pytest.mark.parametrize(("year", "take_home"), [(2025, "53468.68"), (2026, "53786.25")])
def test_the_70000_salary_only_take_home_is_unchanged(year: int, take_home: str) -> None:
    kinds = bundled_kinds()
    worksheets = build_tax_computation().compute(
        ONTARIO, year, Artifact(EMPLOYMENT_INCOME, D("70000"))
    )
    (summary,) = worksheets["ca-on/return"]
    (schedule_8,) = worksheets["ca/schedule_8"]
    (t2204,) = worksheets["ca/t2204"]
    (on428,) = worksheets["ca-on/on428"]
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
    assert on428.get(kinds.kind("ca-on/on428_pension_income_amount_line_27")).value == D("0")
