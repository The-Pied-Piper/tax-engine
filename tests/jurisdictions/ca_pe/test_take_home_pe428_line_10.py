"""PE428 (2025) line 10, the age amount, over the optional year of birth (`ca/birth_year`).

Form text (Form PE428, CRA 5002-C): "Line 10 and line 58080: Age amount (if you were born in 1960 or
earlier) (use Worksheet PE428) (maximum $6,510)". Worksheet PE428 (CRA 5002-D), "Line 58080 - Age
amount": line 1 maximum 6,510.00; line 2 amount from line 23600; line 3 income threshold 36,600.00;
line 4 line 2 minus line 3 (if negative, enter "0"); line 5 rate 15%; line 6 line 4 times line 5;
line 7 line 1 minus line 6 (if negative, enter "0"). A request that leaves the year out is not born
in 1960 or earlier: line 10 is 0.00. Built as Nova Scotia's line 10 is.
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
from tax_engine.jurisdictions.ca_pe.catalog import PE428_AGE_AMOUNT_LINE_10
from tests.jurisdictions.ca_pe.conftest import TakeHomeService
from tests.jurisdictions.ca_pe.credits_support import FEDERAL_PARTS, FORM_NAME, HEADER, form, value
from tests.jurisdictions.ca_pe.support import prince_edward_island_kinds

D = Decimal
PARTS = (
    *FEDERAL_PARTS,
    "pe428_line_10_input.yaml",
    "pe428_line_10_worksheet_lines_2_to_3.yaml",
    "pe428_line_10_worksheet_lines_4_to_7.yaml",
    "pe428_line_10.yaml",
)
LINE_2 = "ca-pe/worksheet_pe428_age_amount_net_income_line_2"
LINE_10 = "ca-pe/pe428_age_amount_line_10"


def _sheet(take_home_service: TakeHomeService, salary: str, year: int | None) -> Any:
    service = take_home_service(HEADER, form(LINE_2, LINE_10), *PARTS)
    given: list[Artifact[Any]] = [Artifact(EMPLOYMENT_INCOME, D(salary))]
    if year is not None:
        given.append(Artifact(BIRTH_YEAR, year))
    (sheet,) = service.compute(
        TaxCalculationRequest(JurisdictionCode("CA-PE"), 2025, tuple(given))
    )[FORM_NAME]
    return sheet


@pytest.mark.parametrize(
    ("salary", "expected"), [("20000", "6510.00"), ("36600", "6510.00"), ("90000", "0.00")]
)
def test_line_10_born_in_1960_or_earlier(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    assert value(_sheet(take_home_service, salary, 1960), LINE_10) == D(expected)


def test_line_10_in_the_reduction_range_is_the_worksheet_arithmetic(
    take_home_service: TakeHomeService,
) -> None:
    sheet = _sheet(take_home_service, "50000", 1950)
    net_income = value(sheet, LINE_2)
    expected = (D("6510") - D("0.15") * (net_income - D("36600"))).quantize(D("0.01"))

    assert D("36600") < net_income < D("80000")
    assert value(sheet, LINE_10) == expected


@pytest.mark.parametrize("year", [None, 1961, 1990])
def test_line_10_is_zero_when_the_year_is_left_out_or_after_1960(
    take_home_service: TakeHomeService, year: int | None
) -> None:
    assert value(_sheet(take_home_service, "20000", year), LINE_10) == D("0.00")


def test_the_line_kind_is_the_registered_one() -> None:
    assert prince_edward_island_kinds().kind(LINE_10) is PE428_AGE_AMOUNT_LINE_10
