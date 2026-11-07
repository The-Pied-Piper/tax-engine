"""T1 General 2025 (5006-R, Ontario) Step 5 Part A line 76 "Federal tax on taxable income", from the
salary alone.

Line 76 is "Line 74 plus line 75 Federal tax on taxable income" (T1 General 5006-R, CRA 5006-R-25E,
confirmed in docs/cra-forms-2025/5006-r-25e.txt, lines 426-482). Part A starts with "Use the amount
from line 26000 to complete the appropriate column below." Line 70 is "Amount from line 26000", and
the form says "Use column 1 if the amount from line 26000 is $57,375 or less", "Use column 2 if the
amount from line 26000 is more than $57,375 but not more than $114,750", and so on up to column 5
("more than $253,414").

The take-home filer has the amount from line 26000 as the one figure of Part A, so the step is two
parts of the form. Line 70 is a `core/record_total` over the T1 taxable-income record list
`ca/t1_taxable_income.taxable_income` (the engine lets one form read another form's exports only as
record lists), and the new kind `ca/federal_tax_taxable_income_line_70` is non-negative. Line 76 is
a `core/progressive_tax` over the dataset `ca/brackets` 2025, which rounds once, half-up to the
cent, and produces `ca/federal_basic_tax`. The brackets start at 0, 57,375, 114,750, 177,882 and
253,414 with rates 14.5%, 20.5%, 26%, 29% and 33%; the printed line 75 constants are the tax at
each bracket start.

The T1 side is the real `ca/t1_taxable_income` form: its header part and the real lines 15000,
23300 (deductions, read from the real Schedule 8), 23400, 23600, 23600 signed, 26000 and the
optional inputs parts, so line 26000 comes from the salary through the real lines. The form header
of line 76 is test-local: it declares `ca/federal_basic_tax` as its one export.

The salary is the only input the caller gives. Ontario resident, single filer, salary the only
income, tax withheld 0, basic credits only, as the take-home calculator states them.

Line 76 is pinned as a figure for each salary, and checked against the printed column formula
(lower bound, rate and constant of Part A) for one salary in each of the five columns. Line 26000
steps by 0.99 a dollar of salary near 57,375, and no salary gives exactly 57,375.00, so the column
1 and column 2 boundary is tested at the two salaries either side of it. Line 70 is pinned at
70,000, and the two kinds are pinned as registered and non-negative.
"""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal
from textwrap import dedent

import pytest

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tests.jurisdictions.ca_on.conftest import TAKE_HOME, TakeHomeService
from tests.kinds import bundled_kinds, non_negative

D = Decimal
ONTARIO = JurisdictionCode("CA-ON")
FORM = "ca/t1_tax_and_credits"
T1_FORM = "ca/t1_taxable_income"
LINE_70 = "ca/federal_tax_taxable_income_line_70"
LINE_76 = "ca/federal_basic_tax"
TAXABLE_INCOME = "ca/taxable_income"
# The real parts composed beside the test's header: the salary, the real Schedule 8, and the real
# T1 taxable-income lines and inputs, so line 26000 is read from the salary through the real lines.
PARTS = (
    "salary.yaml",
    *(part.name for part in sorted(TAKE_HOME.rglob("schedule_8*.yaml"))),
    "t1_taxable_income_inputs.yaml",
    "t1_taxable_income_line_15000.yaml",
    "t1_taxable_income_line_23300.yaml",
    "t1_taxable_income_line_23400.yaml",
    "t1_taxable_income_line_23600.yaml",
    "t1_taxable_income_line_23600_signed.yaml",
    "t1_taxable_income_line_25700_inputs.yaml",
    "t1_taxable_income_line_26000.yaml",
    "t1_taxable_income.yaml",
    "t1_taxable_income_line_10400_inputs.yaml",
    "t1_tax_and_credits_line_76.yaml",
)
HEADER = dedent("""\
    jurisdiction: CA-ON
    version: 1
    valid_from_tax_year: 2025
    outputs:
      - ca/employment_income
    capabilities: []
    """)
# The T1 tax and credits declaration, test-local: its one export is line 76, the only line composed
# here.
T1_TAX_AND_CREDITS = dedent(f"""\
    form:
      name: {FORM}
      required: true
      exports:
        - {LINE_76}
    """)
# Part A columns of 5006-R (lines 71, 73 and 75): the lower bound of line 70, the rate and the
# constant (the printed tax at the bound). Column 1 is the first; line 70 of 57,375.00 or less is in
# it, and the bound of each later column is not included in it.
COLUMNS = (
    (D("0"), D("0.145"), D("0.00")),
    (D("57375"), D("0.205"), D("8319.38")),
    (D("114750"), D("0.26"), D("20081.25")),
    (D("177882"), D("0.29"), D("36495.57")),
    (D("253414"), D("0.33"), D("58399.85")),
)


def _sheets(take_home_service: TakeHomeService, salary: str) -> tuple[Worksheet, Worksheet]:
    """The T1 taxable-income sheet (line 26000 is read from it) and the tax and credits sheet."""
    worksheets = take_home_service(HEADER, T1_TAX_AND_CREDITS, *PARTS).compute(
        ONTARIO, 2025, Artifact(EMPLOYMENT_INCOME, D(salary))
    )
    (t1,) = worksheets[T1_FORM]
    (sheet,) = worksheets[FORM]
    return t1, sheet


def _column_of(line_26000: Decimal) -> int:
    """The Part A column (0 for column 1) the form says to use for line 26000."""
    return sum(1 for lower, _, _ in COLUMNS[1:] if line_26000 > lower)


def _printed_formula(line_26000: Decimal, column: int) -> Decimal:
    """Line 76 as the printed column gives it: line 75 plus line 74 (rate times line 70 less the
    column's lower bound), rounded half-up to the cent."""
    lower, rate, constant = COLUMNS[column]
    return (constant + rate * (line_26000 - lower)).quantize(D("0.01"), rounding=ROUND_HALF_UP)


@pytest.mark.parametrize(
    ("salary", "expected"),
    [
        # Column 1: 19,835.00 is 14.5% of the whole amount, 2,876.075 rounded half-up.
        ("20000", "2876.08"),
        # Column 2: 8,319.38 plus 20.5% of 11,960.00 above 57,375.00.
        ("70000", "10771.18"),
        # Column 4: 36,495.57 plus 29% of 21,044.00 above 177,882.00.
        ("200000", "42598.33"),
    ],
)
def test_line_76_is_the_federal_tax_on_taxable_income(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    _, sheet = _sheets(take_home_service, salary)

    assert sheet.get(bundled_kinds().kind(LINE_76)).value == D(expected)


@pytest.mark.parametrize(
    ("salary", "column"),
    [
        # Line 26000 of these salaries is 19,835.00, 59,435.00, 128,926.00, 198,926.00 and
        # 298,926.00: one salary in each of the five columns.
        ("20000", 0),
        ("60000", 1),
        ("130000", 2),
        ("200000", 3),
        ("300000", 4),
    ],
)
def test_line_76_is_the_printed_column_formula_for_each_column(
    take_home_service: TakeHomeService, salary: str, column: int
) -> None:
    t1, sheet = _sheets(take_home_service, salary)
    line_26000 = t1.get(bundled_kinds().kind(TAXABLE_INCOME)).value

    assert _column_of(line_26000) == column
    assert sheet.get(bundled_kinds().kind(LINE_76)).value == _printed_formula(line_26000, column)


@pytest.mark.parametrize(
    ("salary", "line_26000", "expected"),
    [
        # Line 26000 of 57,374.81 is in column 1: 14.5% of it is 8,319.347, rounded to 8,319.35.
        ("57919", "57374.81", "8319.35"),
        # Line 26000 of 57,375.80 is in column 2: 8,319.38 plus 20.5% of 0.80 is 8,319.544,
        # which rounds to 8,319.54.
        ("57920", "57375.80", "8319.54"),
    ],
)
def test_line_76_at_the_57375_column_boundary(
    take_home_service: TakeHomeService, salary: str, line_26000: str, expected: str
) -> None:
    t1, sheet = _sheets(take_home_service, salary)

    assert t1.get(bundled_kinds().kind(TAXABLE_INCOME)).value == D(line_26000)
    assert sheet.get(bundled_kinds().kind(LINE_76)).value == D(expected)


def test_line_70_is_the_line_26000_amount_at_70000(take_home_service: TakeHomeService) -> None:
    _, sheet = _sheets(take_home_service, "70000")

    assert sheet.get(bundled_kinds().kind(LINE_70)).value == D("69335.00")


def test_the_line_70_kind_is_registered_and_non_negative() -> None:
    # Non-negative: line 70 is the amount from line 26000, which the form reads as an amount to
    # place in a column, never as a negative figure.
    kind = bundled_kinds().kind(LINE_70)

    assert kind.identifier == LINE_70
    assert non_negative(kind) is True


def test_the_line_76_kind_is_registered_and_non_negative() -> None:
    kind = bundled_kinds().kind(LINE_76)

    assert kind.identifier == LINE_76
    assert non_negative(kind) is True
