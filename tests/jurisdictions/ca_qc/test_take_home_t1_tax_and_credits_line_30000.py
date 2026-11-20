"""5005-R (2025) line 78 and line 30000 "Basic personal amount", from the salary alone.

Form text (CRA 5005-R Step 5 Part B, https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5005-r/5005-r-25e.txt):
"Line 78 and line 30000: If the amount on line 23600 is $177,882 or less, enter $16,129. If the
amount on line 23600 is $253,414 or more, enter $14,538. Otherwise, use the Federal Worksheet to
calculate the amount to enter. (maximum $16,129)". Federal Worksheet 5000-D1 (CRA 5000-D1-25E),
"Line 30000 - Basic personal amount": line 3 "Amount from line 23600 of your return", line 10
"Line 2 minus line 9 (if negative, enter "0")" and line 11 "Line 1 plus line 10 Enter this amount on
line 30000 of your return. (maximum $16,129)". Lines 1, 2 and 4 to 11 are one ca/tapered_amount step
over the shared dataset `ca/basic_personal_amount` (14,538, 1,591, 177,882 and 75,532), the division
kept exact and rounded once, half-up to the cent.

The parts are the real ones: the Step 3 chain to line 23600 and the real form declaration. The
expected figures are computed here from the printed worksheet lines with exact fractions (hand
figures, not a CRA example). Line 23600 is the salary less 1,074.00 once the salary is high enough
for the QPP maximum, so salaries 178,957 and 254,488 give 177,883.00 and 253,414.00.
"""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal
from fractions import Fraction

import pytest

from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.jurisdictions.ca_qc.catalog import BASIC_PERSONAL_AMOUNT, NET_INCOME
from tests.jurisdictions.ca_qc.basic_personal_amount_support import sheets
from tests.jurisdictions.ca_qc.conftest import TakeHomeService
from tests.kinds import non_negative

D = Decimal
# The printed figures of worksheet 5000-D1 for line 30000, as the form states them.
BASE = Fraction(14538)
SUPPLEMENT = Fraction(1591)
THRESHOLD = Fraction(177882)
RANGE = Fraction(75532)


def _printed_worksheet(line_3: Decimal) -> Decimal:
    """Line 30000 as worksheet 5000-D1 gives it for a line 23600 between the thresholds: line 1 plus
    line 10, where line 10 is line 2 less line 7 times line 8, never below 0, rounded half-up to the
    cent."""
    line_5 = Fraction(line_3) - THRESHOLD
    line_7 = line_5 / RANGE
    line_9 = line_7 * SUPPLEMENT
    line_10 = max(SUPPLEMENT - line_9, Fraction(0))
    line_11 = BASE + line_10
    return (D(line_11.numerator) / D(line_11.denominator)).quantize(
        D("0.01"), rounding=ROUND_HALF_UP
    )


@pytest.mark.parametrize(
    ("salary", "expected"),
    [
        # Line 23600 of 19,835.00 and of 69,335.00 is at or below 177,882: the printed 16,129.
        ("20000", "16129.00"),
        ("70000", "16129.00"),
        # Line 23600 of 198,926.00: 1,591.00 less 1,591.00 times 21,044.00 over 75,532.00 (443.27)
        # is 1,147.73, and 14,538.00 plus it is 15,685.73.
        ("200000", "15685.73"),
    ],
)
def test_line_78_is_the_basic_personal_amount(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    _, sheet = sheets(take_home_service, salary)

    assert sheet.get(BASIC_PERSONAL_AMOUNT).value == D(expected)


@pytest.mark.parametrize(
    ("salary", "line_23600", "expected"),
    [
        # At 177,882.00 exactly: "$177,882 or less", the printed 16,129.00.
        ("178956", "177882.00", "16129.00"),
        # One dollar over: 1,591.00 times 1.00 over 75,532.00 is 0.0211, so 16,128.98.
        ("178957", "177883.00", "16128.98"),
        # Exactly "$253,414 or more": 14,538.00.
        ("254488", "253414.00", "14538.00"),
        # Above it: still the printed 14,538.00.
        ("300000", "298926.00", "14538.00"),
    ],
)
def test_line_78_at_the_thresholds(
    take_home_service: TakeHomeService, salary: str, line_23600: str, expected: str
) -> None:
    t1, sheet = sheets(take_home_service, salary)

    assert t1.get(NET_INCOME).value == D(line_23600)
    assert sheet.get(BASIC_PERSONAL_AMOUNT).value == D(expected)


@pytest.mark.parametrize("salary", ["190000", "240000"])
def test_line_78_is_the_printed_worksheet_between_the_thresholds(
    take_home_service: TakeHomeService, salary: str
) -> None:
    t1, sheet = sheets(take_home_service, salary)
    line_3 = t1.get(NET_INCOME).value

    assert D("177882") < line_3 < D("253414")
    assert sheet.get(BASIC_PERSONAL_AMOUNT).value == _printed_worksheet(line_3)


@pytest.mark.parametrize(
    ("salary", "line_23600", "reduction", "expected"),
    [
        ("70000", "69335.00", "0.00", "16129.00"),
        ("200000", "198926.00", "443.27", "15685.73"),
    ],
)
def test_line_78_names_its_base_and_its_rounded_reduction_in_the_trace(
    take_home_service: TakeHomeService, salary: str, line_23600: str, reduction: str, expected: str
) -> None:
    _, sheet = sheets(take_home_service, salary)

    assert sheet.get(BASIC_PERSONAL_AMOUNT).value == D(expected)
    assert (
        f"14538.00 plus 1591.00, less {reduction} "
        '(the reduction for "Amount from line 23600 of your return" '
        f"(CA${line_23600}) over 177882.00, spread over a range of 75532.00), "
        f"not below 14538.00, gives CA${expected} (rounded to the nearest cent)."
    ) in EnglishTraceRenderer().render_all(sheet.trace, sheet)


def test_the_line_78_kind_is_non_negative() -> None:
    assert non_negative(BASIC_PERSONAL_AMOUNT) is True
