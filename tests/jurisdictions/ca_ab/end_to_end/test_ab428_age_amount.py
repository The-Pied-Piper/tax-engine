"""AB428 (2025 and 2026) line 17, the age amount, over the optional year of birth.

Form text (Form AB428, CRA 5009-C, .txt): "Line 17 and line 58080: Age amount (if you were born in
1960 or earlier) (use Worksheet AB428) (maximum $6,221)". Worksheet AB428 (CRA 5009-D), "Line 58080
- Age amount": line 1 maximum 6,221.00; line 2 amount from line 23600; line 3 income threshold
46,308.00; line 4 line 2 minus line 3 (if negative, enter "0"); line 5 rate 15%; line 6 line 4 times
line 5; line 7 line 1 minus line 6 (if negative, enter "0"). A request that leaves the year out is
not born in 1960 or earlier: line 17 is 0.00. The cutoff year is 1960 for 2025 and 1961 for 2026
(age 65 on 31 December). The real Alberta manifest is composed end to end through the registered
engine.
"""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

import pytest

from tax_engine import build_tax_computation
from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca.catalog.personal_amounts import BIRTH_YEAR
from tax_engine.registrations import artifact_kinds

D = Decimal
FORM = "ca-ab/ab428_credits"
LINE_2 = "ca-ab/worksheet_ab428_age_amount_net_income_line_2"
LINE = "ca-ab/ab428_age_amount_line_17"
MAXIMUM = D("6221")
THRESHOLD = D("46308")


def _figure(sheet: Worksheet, name: str) -> Decimal:
    kind = artifact_kinds().kind(name)
    assert isinstance(kind, AmountKind)
    return sheet.get(kind).value


def _sheet(year: int, salary: str, birth_year: int | None) -> Worksheet:
    given: tuple[Artifact[Decimal] | Artifact[int], ...] = (Artifact(EMPLOYMENT_INCOME, D(salary)),)
    if birth_year is not None:
        given = (*given, Artifact(BIRTH_YEAR, birth_year))
    worksheets = build_tax_computation().compute(
        TaxCalculationRequest(JurisdictionCode("CA-AB"), year, given)
    )
    (sheet,) = worksheets[FORM]
    return sheet


@pytest.mark.parametrize("year", [2025, 2026])
@pytest.mark.parametrize(
    ("salary", "expected"), [("20000", "6221.00"), ("46308", "6221.00"), ("100000", "0.00")]
)
def test_line_is_the_maximum_below_the_threshold_and_zero_far_above(
    year: int, salary: str, expected: str
) -> None:
    assert _figure(_sheet(year, salary, 1950), LINE) == D(expected)


@pytest.mark.parametrize("year", [2025, 2026])
def test_line_in_the_reduction_range_is_the_worksheet_arithmetic(year: int) -> None:
    sheet = _sheet(year, "60000", 1950)
    net_income = _figure(sheet, LINE_2)
    expected = (MAXIMUM - D("0.15") * (net_income - THRESHOLD)).quantize(
        D("0.01"), rounding=ROUND_HALF_UP
    )

    assert THRESHOLD < net_income < THRESHOLD + MAXIMUM / D("0.15")
    assert _figure(sheet, LINE) == expected


@pytest.mark.parametrize("year", [2025, 2026])
def test_line_is_zero_when_the_year_is_left_out(year: int) -> None:
    assert _figure(_sheet(year, "20000", None), LINE) == D("0.00")


@pytest.mark.parametrize(
    ("year", "birth_year", "expected"),
    [
        (2025, 1960, "6221.00"),
        (2025, 1961, "0.00"),
        (2026, 1961, "6221.00"),
        (2026, 1962, "0.00"),
    ],
)
def test_the_cutoff_year_moves_with_the_tax_year(year: int, birth_year: int, expected: str) -> None:
    assert _figure(_sheet(year, "20000", birth_year), LINE) == D(expected)
