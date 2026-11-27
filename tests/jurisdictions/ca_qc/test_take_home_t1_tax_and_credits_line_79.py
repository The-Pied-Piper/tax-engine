"""5005-R (2025) line 79 and line 30100 "Age amount", from the salary and the year of birth.

Form text (CRA 5005-R page 5, https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5005-r/5005-r-25e.txt):
"Line 79 and line 30100: Age amount (if you were born in 1960 or earlier) (use Federal Worksheet)
(maximum $9,028)". Federal Worksheet 5000-D1 (CRA 5000-D1-25E), "Line 30100 - Age amount": line 1
maximum 9,028.00, line 2 the amount from line 23600, line 3 income threshold 45,522.00, line 4
line 2 less line 3 (not below 0), line 5 rate 15%, line 6 line 4 times the rate, line 7 line 1 less
line 6
(not below 0). The expected figures are computed here from the printed worksheet lines (hand
figures, not a CRA example). A blank year of birth leaves line 79 at 0.00 and line 85 as it was.
"""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

import pytest

from tax_engine.jurisdictions.ca_qc.catalog import (
    AGE_AMOUNT_LINE_79,
    CREDIT_AMOUNTS_LINE_85,
    NET_INCOME,
)
from tests.jurisdictions.ca_qc.basic_personal_amount_support import sheets
from tests.jurisdictions.ca_qc.conftest import TakeHomeService
from tests.kinds import non_negative

D = Decimal
MAXIMUM = D("9028.00")
THRESHOLD = D("45522.00")
RATE = D("0.15")


def _printed_worksheet(line_2: Decimal) -> Decimal:
    line_4 = max(line_2 - THRESHOLD, D(0))
    line_7 = max(MAXIMUM - line_4 * RATE, D(0))
    return line_7.quantize(D("0.01"), rounding=ROUND_HALF_UP)


@pytest.mark.parametrize("salary", ["20000", "70000", "200000"])
@pytest.mark.parametrize("year", [1925, 1960])
def test_line_79_is_the_worksheet_amount_when_born_in_1960_or_earlier(
    take_home_service: TakeHomeService, salary: str, year: int
) -> None:
    t1, sheet = sheets(take_home_service, salary, birth_year=year)

    expected = _printed_worksheet(t1.get(NET_INCOME).value)
    assert sheet.get(AGE_AMOUNT_LINE_79).value == expected


@pytest.mark.parametrize(
    ("salary", "expected"),
    [
        # Line 23600 of 19,835.00 is under 45,522.00: the printed maximum.
        ("20000", "9028.00"),
        # Line 23600 of 69,335.00: 9,028.00 less 15% of 23,813.00 (3,571.95).
        ("70000", "5456.05"),
        # Line 23600 of 198,926.00 is over 105,709.00: nothing.
        ("200000", "0.00"),
    ],
)
def test_line_79_at_each_salary_for_a_filer_born_in_1960(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    _, sheet = sheets(take_home_service, salary, birth_year=1960)

    assert sheet.get(AGE_AMOUNT_LINE_79).value == D(expected)


@pytest.mark.parametrize("year", [None, 1961, 1990, 2007])
def test_line_79_is_0_and_line_85_is_unchanged_without_a_birth_year_in_1960_or_earlier(
    take_home_service: TakeHomeService, year: int | None
) -> None:
    _, sheet = sheets(take_home_service, "70000", birth_year=year)

    assert sheet.get(AGE_AMOUNT_LINE_79).value == D("0.00")
    assert sheet.get(CREDIT_AMOUNTS_LINE_85).value == D("16129.00")


def test_line_85_adds_the_age_amount(take_home_service: TakeHomeService) -> None:
    _, sheet = sheets(take_home_service, "70000", birth_year=1960)

    assert sheet.get(CREDIT_AMOUNTS_LINE_85).value == D("21585.05")


def test_the_age_amount_kind_is_non_negative() -> None:
    assert non_negative(AGE_AMOUNT_LINE_79) is True
