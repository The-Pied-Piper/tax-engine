"""The whole Ontario return runs for tax years 2025 and 2026, salary the only input.

The bundled Ontario manifest is shared by both years, and the engine reads each dataset family's
file for the exact tax year of the request (an absent year is never carried forward). A dataset
family added for one year only therefore passes every per-dataset test and then refuses every
request for the other year. These tests run the real bundled return for both years, so a family
missing for either year fails the suite, by year and salary.

The 2026 datasets are provisional (the 2026 forms are not yet published); the 2026 take-home
figures are the project's validation figures. Take-home is the salary less CPP (base and enhanced),
EI and T1 line 167 (refund or balance owing), as the other end-to-end take-home tests compute it.
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
from tests.kinds import bundled_kinds

D = Decimal
ONTARIO = JurisdictionCode("CA-ON")
RETURN = "ca-on/return"
MARGINAL_RATE = "ca-on/marginal_tax_rate"

YEARS = [2025, 2026]
SALARIES = ["0", "100", "2000", "20000", "70000", "275000"]


def _worksheets(year: int, salary: str) -> dict[str, tuple[Worksheet, ...]]:
    # No fixture: the bundled Ontario manifest, as the calculator loads it, salary the only input.
    return build_tax_computation().compute(
        TaxCalculationRequest(ONTARIO, year, (Artifact(EMPLOYMENT_INCOME, D(salary)),))
    )


def _take_home(year: int, salary: str) -> Decimal:
    kinds = bundled_kinds()
    worksheets = _worksheets(year, salary)
    (schedule_8,) = worksheets["ca/schedule_8"]
    (t2204,) = worksheets["ca/t2204"]
    (summary,) = worksheets[RETURN]
    cpp = (
        schedule_8.get(kinds.kind("ca/schedule_8_cpp_base_contributions_on_return")).value
        + schedule_8.get(kinds.kind("ca/schedule_8_cpp_enhanced_contributions_on_return")).value
    )
    ei = t2204.get(kinds.kind("ca/t2204_premiums_deducted")).value
    line_167 = summary.get(kinds.kind("ca/refund_or_balance_owing")).value
    take_home = D(salary) - cpp - ei - line_167
    assert isinstance(take_home, Decimal)
    return take_home


@pytest.mark.parametrize(
    ("year", "salary", "take_home"),
    [
        (2025, "70000", "53468.68"),
        (2025, "20000", "20165.16"),
        (2025, "275000", "167749.14"),
        (2026, "70000", "53786.25"),
        (2026, "20000", "20253.76"),
        (2026, "275000", "168519.20"),
    ],
)
def test_the_validation_take_home_figures(year: int, salary: str, take_home: str) -> None:
    assert _take_home(year, salary) == D(take_home)


@pytest.mark.parametrize("year", YEARS)
@pytest.mark.parametrize("salary", SALARIES)
def test_every_dataset_exists_for_the_year_and_the_return_carries_the_marginal_rate(
    year: int, salary: str
) -> None:
    kinds = bundled_kinds()
    (summary,) = _worksheets(year, salary)[RETURN]

    marginal = summary.get(kinds.kind(MARGINAL_RATE)).value
    assert isinstance(marginal, Decimal)
    assert D("0") <= marginal <= D("1")


@pytest.mark.parametrize("year", YEARS)
def test_no_tax_and_no_rates_at_a_salary_of_0(year: int) -> None:
    kinds = bundled_kinds()
    (summary,) = _worksheets(year, "0")[RETURN]

    assert summary.get(kinds.kind(MARGINAL_RATE)).value == D("0")
    assert _take_home(year, "0") == D("0")
