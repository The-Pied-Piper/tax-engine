"""PE428 (2025) line 76, the age reduction for self, over the optional year of birth.

Form text (Form PE428, CRA 5002-C): "Line 76 and line 63380: Age reduction for self (if you were born
in 1960 or earlier) Claim $250". Line 76 is $250.00 when born in 1960 or earlier and 0.00
otherwise (a blank year is not born in 1960 or earlier); line 81 adds it.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import pytest

from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca.catalog.personal_amounts import BIRTH_YEAR
from tests.jurisdictions.ca_pe.conftest import TakeHomeService
from tests.jurisdictions.ca_pe.credits_support import (
    CHAIN_81,
    FORM_NAME,
    HEADER,
    form,
    value,
)

D = Decimal
LINE_76 = "ca-pe/pe428_age_reduction_for_self_line_76"
LINE_81 = "ca-pe/pe428_low_income_reductions_total_line_81"
EXPORTS = (
    "ca-pe/pe428_tax_line_67",
    "ca-pe/pe428_net_income_line_68",
    "ca-pe/pe428_uccb_repayment_line_69",
    "ca-pe/pe428_family_income_line_70",
    "ca-pe/pe428_uccb_income_line_71",
    "ca-pe/pe428_adjusted_family_income_line_72",
    "ca-pe/low_income_reduction_basic",
    LINE_76,
    LINE_81,
)


def _sheet(take_home_service: TakeHomeService, year: int | None) -> Any:
    service = take_home_service(HEADER, form(*EXPORTS), *CHAIN_81)
    given: list[Artifact[Any]] = [Artifact(EMPLOYMENT_INCOME, D("20000"))]
    if year is not None:
        given.append(Artifact(BIRTH_YEAR, year))
    (sheet,) = service.compute(
        TaxCalculationRequest(JurisdictionCode("CA-PE"), 2025, tuple(given))
    )[FORM_NAME]
    return sheet


@pytest.mark.parametrize(
    ("year", "line_76", "line_81"),
    [
        (1960, "250.00", "600.00"),
        (1930, "250.00", "600.00"),
        (1961, "0.00", "350.00"),
        (None, "0.00", "350.00"),
    ],
)
def test_line_76_and_the_sum_on_line_81(
    take_home_service: TakeHomeService, year: int | None, line_76: str, line_81: str
) -> None:
    sheet = _sheet(take_home_service, year)

    assert value(sheet, LINE_76) == D(line_76)
    assert value(sheet, LINE_81) == D(line_81)
