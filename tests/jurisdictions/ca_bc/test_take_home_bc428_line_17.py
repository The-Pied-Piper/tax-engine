"""BC428 (2025 and 2026) line 17, the age amount, over the optional year of birth.

Form text (Form BC428, CRA 5010-C, .txt): "Line 17 and line 58080: Age amount (if you were born in
1960 or earlier) (use Worksheet BC428) (maximum $5,799)". Worksheet BC428 (CRA 5010-D), "Line 58080
- Age amount": line 1 maximum 5,799.00; line 2 amount from line 23600; line 3 income threshold
43,169.00; line 4 line 2 minus line 3 (if negative, enter "0"); line 5 rate 15%; line 6 line 4 times
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
from tax_engine.jurisdictions.ca_bc.catalog import (
    BC428_AGE_AMOUNT_LINE_17,
    WORKSHEET_BC428_AGE_AMOUNT_NET_INCOME_LINE_2,
)
from tests.federal_forms import form_part_names
from tests.jurisdictions.ca_bc.conftest import TakeHomeService

D = Decimal
FORM_NAME = "ca-bc/bc428"
PARTS = (
    *form_part_names(
        "schedule_8",
        "t2204",
        "t1_employment_income",
        "t1_taxable_income",
        "t1_lines_copied_by_provinces",
        "schedule_9",
    ),
    "bc428_line_17_worksheet_lines_1_to_3.yaml",
    "bc428_line_17_worksheet_lines_4_to_7.yaml",
    "bc428_line_17.yaml",
)
HEADER = dedent("""\
    jurisdiction: CA-BC
    version: 1
    valid_from_tax_year: 2025
    outputs: []
    capabilities: []
    """)
FORM = dedent("""\
    form:
      name: ca-bc/bc428
      required: true
      exports:
        - ca-bc/worksheet_bc428_age_amount_net_income_line_2
        - ca-bc/bc428_age_amount_line_17
    """)
MAXIMUMS = {2025: D("5799"), 2026: D("5927")}
THRESHOLDS = {2025: D("43169"), 2026: D("44119")}


def _figures(
    take_home_service: TakeHomeService, year: int, salary: str, birth_year: int | None
) -> tuple[Decimal, Decimal]:
    given: tuple[Artifact[Decimal] | Artifact[int], ...] = (Artifact(EMPLOYMENT_INCOME, D(salary)),)
    if birth_year is not None:
        given = (*given, Artifact(BIRTH_YEAR, birth_year))
    worksheets = take_home_service(HEADER, FORM, *PARTS).compute(
        TaxCalculationRequest(JurisdictionCode("CA-BC"), year, given)
    )
    (sheet,) = worksheets[FORM_NAME]
    return (
        sheet.get(WORKSHEET_BC428_AGE_AMOUNT_NET_INCOME_LINE_2).value,
        sheet.get(BC428_AGE_AMOUNT_LINE_17).value,
    )


@pytest.mark.parametrize(
    ("year", "salary", "expected"),
    [
        (2025, "20000", "5799.00"),
        (2025, "43169", "5799.00"),
        (2025, "100000", "0.00"),
        (2026, "20000", "5927.00"),
        (2026, "44119", "5927.00"),
        (2026, "100000", "0.00"),
    ],
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
    maximum, threshold = MAXIMUMS[year], THRESHOLDS[year]
    expected = (maximum - D("0.15") * (net_income - threshold)).quantize(
        D("0.01"), rounding=ROUND_HALF_UP
    )

    assert threshold < net_income < threshold + maximum / D("0.15")
    assert line == expected


@pytest.mark.parametrize("year", [2025, 2026])
def test_line_is_zero_when_the_year_is_left_out(
    take_home_service: TakeHomeService, year: int
) -> None:
    assert _figures(take_home_service, year, "20000", None)[1] == D("0.00")


@pytest.mark.parametrize(
    ("year", "birth_year", "expected"),
    [
        (2025, 1960, "5799.00"),
        (2025, 1961, "0.00"),
        (2026, 1961, "5927.00"),
        (2026, 1962, "0.00"),
    ],
)
def test_the_cutoff_year_moves_with_the_tax_year(
    take_home_service: TakeHomeService, year: int, birth_year: int, expected: str
) -> None:
    assert _figures(take_home_service, year, "20000", birth_year)[1] == D(expected)
