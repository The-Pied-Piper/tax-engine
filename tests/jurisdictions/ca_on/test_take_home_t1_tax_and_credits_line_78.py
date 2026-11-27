"""T1 General 2025 (5006-R) line 78 and line 30100, the age amount, over the optional year of birth
(`ca/birth_year`, the T1's input, entered once).

Form text (T1 5006-R): "Line 78 and line 30100: Age amount (if you were born in 1960 or earlier)
(use Federal Worksheet) (maximum $9,028)". Federal Worksheet 5000-D1 (CRA 5000-D1-25E), "Line 30100
- Age amount": line 1 maximum 9,028.00; line 2 amount from line 23600; line 3 income threshold
45,522.00; line 4 line 2 minus line 3 (if negative, enter "0"); line 5 rate 15%; line 6 line 4 times
line 5; line 7 line 1 minus line 6 (if negative, enter "0"). A request that leaves the year out is
not born in 1960 or earlier: line 78 is 0.00 and line 84 is unchanged.
"""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal
from textwrap import dedent

import pytest

from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca.catalog.personal_amounts import BIRTH_YEAR
from tests.federal_forms import form_part_names
from tests.jurisdictions.ca_on.conftest import TakeHomeService
from tests.kinds import bundled_kinds

D = Decimal
ONTARIO = JurisdictionCode("CA-ON")
FORM = "ca/t1_tax_and_credits"
LINE_2 = "ca/age_net_income"
LINE_78 = "ca/age_amount"
LINE_84 = "ca/credit_amounts_line_84"
LINE_30000 = "ca/basic_personal_amount"
PARTS = (
    *form_part_names("t1_lines_copied_by_provinces"),
    *form_part_names("schedule_8"),
    *form_part_names("t1_taxable_income", "t1_employment_income"),
    "t1_tax_and_credits_line_30000.yaml",
    "t1_tax_and_credits_line_78_worksheet_lines_1_to_3.yaml",
    "t1_tax_and_credits_line_78_worksheet_lines_4_to_7.yaml",
    "t1_tax_and_credits_line_78.yaml",
    "t1_tax_and_credits_line_84.yaml",
)
HEADER = dedent("""\
    jurisdiction: CA-ON
    version: 1
    valid_from_tax_year: 2025
    outputs: []
    capabilities: []
    """)
T1_TAX_AND_CREDITS = dedent(f"""\
    form:
      name: {FORM}
      required: true
      exports:
        - {LINE_78}
        - {LINE_84}
    """)
BORN = (Artifact(BIRTH_YEAR, 1960),)


def _sheet(
    service: TakeHomeService, salary: str, given: tuple[Artifact[int], ...], year: int = 2025
) -> Worksheet:
    worksheets = service(HEADER, T1_TAX_AND_CREDITS, *PARTS).compute(
        TaxCalculationRequest(ONTARIO, year, (Artifact(EMPLOYMENT_INCOME, D(salary)), *given))
    )
    (sheet,) = worksheets[FORM]
    return sheet


def _value(sheet: Worksheet, identifier: str) -> Decimal:
    value = sheet.get(bundled_kinds().kind(identifier)).value
    assert isinstance(value, Decimal)
    return value


def _cent(amount: Decimal) -> Decimal:
    return amount.quantize(D("0.01"), rounding=ROUND_HALF_UP)


@pytest.mark.parametrize(
    ("salary", "expected"), [("20000", "9028.00"), ("45522", "9028.00"), ("200000", "0.00")]
)
def test_line_78_at_or_below_the_threshold_is_the_maximum_and_far_above_it_is_zero(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    assert _value(_sheet(take_home_service, salary, BORN), LINE_78) == D(expected)


def test_line_78_in_the_reduction_range_is_the_worksheet_arithmetic(
    take_home_service: TakeHomeService,
) -> None:
    sheet = _sheet(take_home_service, "70000", BORN)
    net_income = _value(sheet, LINE_2)

    assert D("45522") < net_income < D("105709")
    assert _value(sheet, LINE_78) == _cent(D("9028") - D("0.15") * (net_income - D("45522")))


def test_line_84_adds_line_78_to_line_30000(take_home_service: TakeHomeService) -> None:
    sheet = _sheet(take_home_service, "70000", BORN)

    assert _value(sheet, LINE_84) == _value(sheet, LINE_30000) + _value(sheet, LINE_78)
    assert _value(sheet, LINE_78) > 0


@pytest.mark.parametrize("year", [1961, 1990])
def test_line_78_is_zero_when_born_after_1960(
    take_home_service: TakeHomeService, year: int
) -> None:
    sheet = _sheet(take_home_service, "40000", (Artifact(BIRTH_YEAR, year),))

    assert _value(sheet, LINE_78) == D("0.00")


def test_a_blank_year_leaves_line_78_at_zero_and_line_84_unchanged(
    take_home_service: TakeHomeService,
) -> None:
    sheet = _sheet(take_home_service, "40000", ())

    assert _value(sheet, LINE_78) == D("0.00")
    assert _value(sheet, LINE_84) == _value(sheet, LINE_30000)


@pytest.mark.parametrize(("year", "claimed"), [(1961, True), (1962, False)])
def test_the_2026_cutoff_is_born_in_1961_or_earlier_with_the_indexed_figures(
    take_home_service: TakeHomeService, year: int, claimed: bool
) -> None:
    sheet = _sheet(take_home_service, "20000", (Artifact(BIRTH_YEAR, year),), 2026)

    assert _value(sheet, LINE_78) == (D("9209.00") if claimed else D("0.00"))
