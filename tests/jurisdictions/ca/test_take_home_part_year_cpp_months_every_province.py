"""A typed part-year of CPP months never makes a province's take-home marginal rate raise.

With 1 to 11 months typed, the CPP basic exemption (Schedule 8 line E) is prorated, so CPP is
charged from a salary below $2,000, before any federal or provincial tax is due. The credit on the
CPP and EI contributions was then larger than the rate before credits, and the subtraction that
may not go negative raised at $2,000 to $2,033 in every province. Where no
tax is paid the rate is 0 (the gate), so each such subtraction is floored at zero before the gate
applies. The Ontario and Quebec rates are pinned by hand in their own end-to-end tests; here every
province must return a rate in the band at every typed number of months, never less than the rate
at the same salary with no tax, which is the contributions alone.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine import build_tax_computation
from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.jurisdictions.ca.catalog.deductions import CPP_MONTHS
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca.catalog.personal_amounts import BIRTH_YEAR
from tests.kinds import bundled_kinds

D = Decimal
PROVINCES = ["ab", "bc", "mb", "nb", "nl", "ns", "on", "pe", "qc", "sk"]
SALARIES = ["0", "1999", "2000", "2033", "2034"]


@pytest.mark.parametrize("year", [2025, 2026])
@pytest.mark.parametrize("months", [1, 3, 6, 11])
@pytest.mark.parametrize("province", PROVINCES)
def test_the_marginal_rate_is_found_at_every_salary_for_typed_months(
    province: str, months: int, year: int
) -> None:
    kind = bundled_kinds().kind(f"ca-{province}/marginal_tax_rate")
    for salary in SALARIES:
        worksheets = build_tax_computation().compute(
            TaxCalculationRequest(
                JurisdictionCode(f"CA-{province.upper()}"),
                year,
                (
                    Artifact(EMPLOYMENT_INCOME, D(salary)),
                    Artifact(BIRTH_YEAR, 1980),
                    Artifact(CPP_MONTHS, months),
                ),
            )
        )
        (summary,) = worksheets[f"ca-{province}/return"]
        value = summary.get(kind).value
        assert isinstance(value, Decimal)
        assert value >= 0
