"""AB428 (2025 and 2026) line 17, the age amount, over the optional year of birth.

Form text (Form AB428, CRA 5009-C, .txt): "Line 17 and line 58080: Age amount (if you were born in
1960 or earlier) (use Worksheet AB428) (maximum $6,221)". Worksheet AB428 (CRA 5009-D), "Line 58080
- Age amount": line 1 maximum 6,221.00; line 2 amount from line 23600; line 3 income threshold
46,308.00; line 4 line 2 minus line 3 (if negative, enter "0"); line 5 rate 15%; line 6 line 4 times
line 5; line 7 line 1 minus line 6 (if negative, enter "0"). A request that leaves the year out is
not born in 1960 or earlier: line 17 is 0.00. The cutoff year is 1960 for 2025 and 1961 for 2026
(age 65 on 31 December).

The test composes the real worksheet and line parts and the federal parts they read beside a test-
local header and form declaration, and types in the salary and, in some tests, the year of birth.
"""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal
from textwrap import dedent

import pytest

from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca.catalog.personal_amounts import BIRTH_YEAR
from tax_engine.jurisdictions.ca_ab.catalog import (
    AB428_AGE_AMOUNT_LINE_17,
    WORKSHEET_AB428_AGE_AMOUNT_NET_INCOME_LINE_2,
)
from tests.federal_forms import form_part_names
from tests.jurisdictions.ca_ab.conftest import TakeHomeService

D = Decimal
FORM_NAME = "ca-ab/ab428_credits"
PARTS = (
    *form_part_names(
        "schedule_8",
        "t2204",
        "t1_employment_income",
        "t1_taxable_income",
        "t1_lines_copied_by_provinces",
        "schedule_9",
    ),
    "ab428_line_17_worksheet_lines_1_to_3.yaml",
    "ab428_line_17_worksheet_lines_4_to_7.yaml",
    "ab428_line_17.yaml",
)
HEADER = dedent("""\
    jurisdiction: CA-AB
    version: 1
    valid_from_tax_year: 2025
    outputs: []
    capabilities: []
    """)
FORM = dedent("""\
    form:
      name: ca-ab/ab428_credits
      required: true
      exports:
        - ca-ab/worksheet_ab428_age_amount_net_income_line_2
        - ca-ab/ab428_age_amount_line_17
    """)
MAXIMUM = D("6221")
THRESHOLD = D("46308")


def _figures(
    take_home_service: TakeHomeService, year: int, salary: str, birth_year: int | None
) -> tuple[Decimal, Decimal]:
    given: tuple[Artifact[Decimal] | Artifact[int], ...] = (Artifact(EMPLOYMENT_INCOME, D(salary)),)
    if birth_year is not None:
        given = (*given, Artifact(BIRTH_YEAR, birth_year))
    worksheets = take_home_service(HEADER, FORM, *PARTS).compute(
        TaxCalculationRequest(JurisdictionCode("CA-AB"), year, given)
    )
    (sheet,) = worksheets[FORM_NAME]
    return (
        sheet.get(WORKSHEET_AB428_AGE_AMOUNT_NET_INCOME_LINE_2).value,
        sheet.get(AB428_AGE_AMOUNT_LINE_17).value,
    )


@pytest.mark.parametrize("year", [2025, 2026])
@pytest.mark.parametrize(
    ("salary", "expected"), [("20000", "6221.00"), ("46308", "6221.00"), ("100000", "0.00")]
)
def test_line_is_the_maximum_below_the_threshold_and_zero_far_above(
    take_home_service: TakeHomeService, year: int, salary: str, expected: str
) -> None:
    assert _figures(take_home_service, year, salary, 1950)[1] == D(expected)


@pytest.mark.parametrize("year", [2025, 2026])
def test_line_in_the_reduction_range_is_the_worksheet_arithmetic(
    take_home_service: TakeHomeService, year: int
) -> None:
    net_income, line = _figures(take_home_service, year, "60000", 1950)
    expected = (MAXIMUM - D("0.15") * (net_income - THRESHOLD)).quantize(
        D("0.01"), rounding=ROUND_HALF_UP
    )

    assert THRESHOLD < net_income < THRESHOLD + MAXIMUM / D("0.15")
    assert line == expected


@pytest.mark.parametrize("year", [2025, 2026])
def test_line_is_zero_when_the_year_is_left_out(
    take_home_service: TakeHomeService, year: int
) -> None:
    assert _figures(take_home_service, year, "20000", None)[1] == D("0.00")


@pytest.mark.parametrize(
    ("year", "birth_year", "expected"),
    [
        (2025, 1960, "6221.00"),
        (2025, 1961, "0.00"),
        (2026, 1961, "6221.00"),
        (2026, 1962, "0.00"),
    ],
)
def test_the_cutoff_year_moves_with_the_tax_year(
    take_home_service: TakeHomeService, year: int, birth_year: int, expected: str
) -> None:
    assert _figures(take_home_service, year, "20000", birth_year)[1] == D(expected)
