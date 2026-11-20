"""5005-R (2025) Step 5 Part A as one chain: line 71 to line 77, federal tax on taxable income.

Form text (CRA 5005-R Step 5 Part A, https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5005-r/5005-r-25e.txt):
"Use the amount from line 26000 to complete the appropriate column below." Column 1 is "Line 26000
is $57,375 or less"; the other columns print "more than $57,375 but not more than $114,750",
"more than $114,750 but not more than $177,882", "more than $177,882 but not more than $253,414"
and "more than $253,414". Every column prints line 71 "Amount from line 26000", line 72, line 73
"Line 71 minus line 72 (cannot be negative)", line 74 "Rate", line 75 "Line 73 multiplied by the
percentage from line 74", line 76 and line 77 "Line 75 plus line 76 Federal tax on taxable income".

The chain runs the real parts (Steps 3 and 4 included) with a test-local form declaration that
exports line 77. The three salaries are the take-home salaries; 100,000, 150,000, 200,000 and
300,000 reach columns 2, 3, 4 and 5, which none of the three salaries does for columns 3 and 5. The
expected figures of the three salaries are the hand figures of the ticket; the others are computed
here from the printed columns (not a CRA example).
"""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

import pytest

from tax_engine.jurisdictions.ca_qc.catalog import (
    FEDERAL_BRACKET_COLUMN_RATE_LINE_74,
    FEDERAL_BRACKET_LOWER_BOUND_LINE_72,
    FEDERAL_EXCESS_TIMES_COLUMN_RATE_LINE_75,
    FEDERAL_TAX_AT_COLUMN_START_LINE_76,
    FEDERAL_TAX_ON_TAXABLE_INCOME_LINE_77,
    FEDERAL_TAXABLE_INCOME_LINE_71,
    FEDERAL_TAXABLE_INCOME_OVER_LOWER_BOUND_LINE_73,
    TAXABLE_INCOME,
)
from tests.jurisdictions.ca_qc.conftest import TakeHomeService
from tests.jurisdictions.ca_qc.federal_tax_support import COLUMNS, sheets

D = Decimal
ALL_LINES = (71, 72, 73, 74, 75, 76, 77)
EXPORT = "ca-qc/federal_tax_on_taxable_income_line_77"


@pytest.mark.parametrize(
    ("salary", "column", "figures"),
    [
        # Lines 71 to 77, as the ticket's hand figures give them.
        ("20000", 1, ("19835.00", "0.00", "19835.00", "0.145", "2876.08", "0.00", "2876.08")),
        (
            "70000",
            2,
            ("69335.00", "57375.00", "11960.00", "0.205", "2451.80", "8319.38", "10771.18"),
        ),
        (
            "200000",
            4,
            ("198926.00", "177882.00", "21044.00", "0.29", "6102.76", "36495.57", "42598.33"),
        ),
    ],
)
def test_the_part_a_lines_of_a_salary_only_filer(
    take_home_service: TakeHomeService, salary: str, column: int, figures: tuple[str, ...]
) -> None:
    _, sheet = sheets(take_home_service, salary, EXPORT, *ALL_LINES)

    kinds = (
        FEDERAL_TAXABLE_INCOME_LINE_71,
        FEDERAL_BRACKET_LOWER_BOUND_LINE_72,
        FEDERAL_TAXABLE_INCOME_OVER_LOWER_BOUND_LINE_73,
        FEDERAL_BRACKET_COLUMN_RATE_LINE_74,
        FEDERAL_EXCESS_TIMES_COLUMN_RATE_LINE_75,
        FEDERAL_TAX_AT_COLUMN_START_LINE_76,
        FEDERAL_TAX_ON_TAXABLE_INCOME_LINE_77,
    )
    assert [sheet.get(kind).value for kind in kinds] == [D(figure) for figure in figures]
    lower, rate, constant = COLUMNS[column - 1]
    assert (D(figures[1]), D(figures[3]), D(figures[5])) == (lower, rate, constant)


def _printed_column(line_26000: Decimal) -> int:
    """The column (1 to 5) the form says to use: a base at a limit is in the lower column."""
    return 1 + sum(1 for lower, _, _ in COLUMNS[1:] if line_26000 > lower)


def _printed_line_77(line_26000: Decimal, column: int) -> Decimal:
    lower, rate, constant = COLUMNS[column - 1]
    line_75 = (rate * (line_26000 - lower)).quantize(D("0.01"), rounding=ROUND_HALF_UP)
    return line_75 + constant


@pytest.mark.parametrize(
    ("salary", "column"),
    [("100000", 2), ("150000", 3), ("200000", 4), ("300000", 5)],
)
def test_each_column_from_two_to_five_gives_the_printed_federal_tax(
    take_home_service: TakeHomeService, salary: str, column: int
) -> None:
    t1, sheet = sheets(take_home_service, salary, EXPORT, *ALL_LINES)
    line_26000 = t1.get(TAXABLE_INCOME).value

    assert _printed_column(line_26000) == column
    assert sheet.get(FEDERAL_TAXABLE_INCOME_LINE_71).value == line_26000
    assert sheet.get(FEDERAL_TAX_ON_TAXABLE_INCOME_LINE_77).value == _printed_line_77(
        line_26000, column
    )


@pytest.mark.parametrize(
    ("salary", "line_26000", "line_75", "line_77"),
    [
        # A base at a column limit is in the lower column: 14.5% of 57,375.00 is 8,319.375, printed
        # 8,319.38, on column 1's constant of 0.00.
        ("57919.19", "57375.00", "8319.38", "8319.38"),
        # A cent over it is in column 2: 20.5% of 0.01 rounds to 0.00, on 8,319.38.
        ("57919.20", "57375.01", "0.00", "8319.38"),
        # 114,750.00 is the top of column 2: 20.5% of 57,375.00 is 11,761.875, rounded to 11,761.88
        # before line 76 (8,319.38) is added, so 20,081.26.
        ("115824", "114750.00", "11761.88", "20081.26"),
        # 177,882.00 is the top of column 3; 253,414.00 the top of column 4.
        ("178956", "177882.00", "16414.32", "36495.57"),
        ("254488", "253414.00", "21904.28", "58399.85"),
    ],
)
def test_a_base_at_a_column_limit_is_in_the_lower_column(
    take_home_service: TakeHomeService, salary: str, line_26000: str, line_75: str, line_77: str
) -> None:
    t1, sheet = sheets(take_home_service, salary, EXPORT, *ALL_LINES)

    assert t1.get(TAXABLE_INCOME).value == D(line_26000)
    assert sheet.get(FEDERAL_EXCESS_TIMES_COLUMN_RATE_LINE_75).value == D(line_75)
    assert sheet.get(FEDERAL_TAX_ON_TAXABLE_INCOME_LINE_77).value == D(line_77)
