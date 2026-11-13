"""T1 General 2025 (5006-R, Ontario) Step 5 Part A lines 70 to 76, "Federal tax on taxable income",
from the salary alone.

Line 76 is "Line 74 plus line 75 Federal tax on taxable income" (T1 General 5006-R, CRA 5006-R-25E).
Part A starts with "Use the amount
from line 26000 to complete the appropriate column below." Line 70 is "Amount from line 26000", and
the form says "Use column 1 if the amount from line 26000 is $57,375 or less", "Use column 2 if the
amount from line 26000 is more than $57,375 but not more than $114,750", and so on up to column 5
("more than $253,414").

The take-home filer has the amount from line 26000 as the one figure of Part A, so the step is one
part of the form, `t1_tax_and_credits_line_76.yaml`, with one capability per printed line:

- line 70: `core/record_total` over the T1 taxable-income record list
  `ca/t1_taxable_income.taxable_income` (the engine lets one form read another form's exports only
  as record lists);
- line 71: `core/bracket_column_lower_bound` over the `ca/brackets` 2025 dataset;
- line 72: `core/subtract_not_below_zero`, line 70 less line 71, rounded by `ca/cent_rounding`;
- line 73: `core/bracket_column_rate` (the column's rate, 14.5% to 33%);
- line 74: `core/multiply_by_rate`, line 72 times line 73, rounded half-up to the cent by
  `ca/cent_rounding`;
- line 75: `core/bracket_column_tax_at_start` (the printed constant of the column: 0.00, 8,319.38,
  20,081.25, 36,495.57 and 58,399.85, carried as printed by `ca/brackets`);
- line 76: `core/sum` of line 74 and line 75, rounded by `ca/cent_rounding`, output
  `ca/federal_tax_on_taxable_income_line_76`.

Line 74 is rounded to the cent before line 75 is added, as the form's dollars-and-cents box does.
At a line 26000 of 114,750.00, line 74 is 11,761.875, printed 11,761.88, and line 76 is 20,081.26
(the printed 8,319.38 plus 11,761.88), not 20,081.25.

The T1 side is the real `ca/t1_taxable_income` form: its header part and the real lines 15000,
23300 (deductions, read from the real Schedule 8), 23400, 23600, 23600 signed, 26000 and the
optional inputs parts, so line 26000 comes from the salary through the real lines. The form header
of line 76 is test-local: it declares `ca/federal_tax_on_taxable_income_line_76` as its one export.

The salary is the only input the caller gives. Ontario resident, single filer, salary the only
income, tax withheld 0, basic credits only, as the take-home calculator states them.

Line 26000 is not a fixed share of the salary (70,000 gives 69,335.00 and 200,000 gives 198,926.00),
and the salaries that give each bracket start exactly were found by search with the real engine:
57,919.19 gives 57,375.00, 115,824 gives 114,750.00, 178,956 gives 177,882.00 and 254,488 gives
253,414.00. The line 76 tests use them, and the salaries a cent or a dollar either side, so every
start is tested at its threshold and on either side of it.

Line 70 is pinned at 70,000, and every line 70 to 76 kind is pinned as registered and non-negative.
"""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal
from textwrap import dedent

import pytest

from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
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
LINE_71 = "ca/federal_bracket_lower_bound_line_71"
LINE_72 = "ca/federal_taxable_income_over_lower_bound_line_72"
LINE_73 = "ca/federal_bracket_column_rate_line_73"
LINE_74 = "ca/federal_excess_times_column_rate_line_74"
LINE_75 = "ca/federal_tax_at_column_start_line_75"
LINE_76 = "ca/federal_tax_on_taxable_income_line_76"
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
CENT = D("0.01")


def _sheets(take_home_service: TakeHomeService, salary: str) -> tuple[Worksheet, Worksheet]:
    """The T1 taxable-income sheet (line 26000 is read from it) and the tax and credits sheet."""
    worksheets = take_home_service(HEADER, T1_TAX_AND_CREDITS, *PARTS).compute(
        ONTARIO, 2025, Artifact(EMPLOYMENT_INCOME, D(salary))
    )
    (t1,) = worksheets[T1_FORM]
    (sheet,) = worksheets[FORM]
    return t1, sheet


def _value(sheet: Worksheet, identifier: str) -> Decimal:
    value = sheet.get(bundled_kinds().kind(identifier)).value
    assert isinstance(value, Decimal)
    return value


def _column_of(line_26000: Decimal) -> int:
    """The Part A column (0 for column 1) the form says to use for line 26000."""
    return sum(1 for lower, _, _ in COLUMNS[1:] if line_26000 > lower)


def _printed_formula(line_26000: Decimal, column: int) -> Decimal:
    """Line 76 as the printed column gives it, line by line: line 74 is the rate times line 70 less
    the column's lower bound, rounded half-up to the cent; line 76 is line 74 plus line 75."""
    lower, rate, constant = COLUMNS[column]
    line_74 = (rate * (line_26000 - lower)).quantize(CENT, rounding=ROUND_HALF_UP)
    return constant + line_74


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

    assert _value(sheet, LINE_76) == D(expected)


def test_lines_71_to_75_at_a_70000_salary_are_the_printed_column_figures(
    take_home_service: TakeHomeService,
) -> None:
    # Line 26000 is 69,335.00, in column 2: the lower bound, the excess over it, the rate, line 74
    # (20.5% of 11,960.00 is exactly 2,451.80) and the printed constant of the column.
    t1, sheet = _sheets(take_home_service, "70000")

    assert t1.get(bundled_kinds().kind(TAXABLE_INCOME)).value == D("69335.00")
    assert _value(sheet, LINE_70) == D("69335.00")
    assert _value(sheet, LINE_71) == D("57375.00")
    assert _value(sheet, LINE_72) == D("11960.00")
    assert _value(sheet, LINE_73) == D("0.205")
    assert _value(sheet, LINE_74) == D("2451.80")
    assert _value(sheet, LINE_75) == D("8319.38")
    assert _value(sheet, LINE_76) == D("10771.18")


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
    assert _value(sheet, LINE_76) == _printed_formula(line_26000, column)


def test_line_74_at_114750_is_rounded_to_the_cent_before_line_75_is_added(
    take_home_service: TakeHomeService,
) -> None:
    # Line 26000 of 114,750.00 is the top of column 2 ("not more than $114,750"). Line 72 is
    # 57,375.00, and line 74 is 20.5% of it, 11,761.875, a dollars-and-cents box: 11,761.88. Line 75
    # is column 2's printed 8,319.38, so line 76 is 20,081.26.
    t1, sheet = _sheets(take_home_service, "115824")

    assert t1.get(bundled_kinds().kind(TAXABLE_INCOME)).value == D("114750.00")
    assert _value(sheet, LINE_72) == D("57375.00")
    assert _value(sheet, LINE_74) == D("11761.88")
    assert _value(sheet, LINE_75) == D("8319.38")
    assert _value(sheet, LINE_76) == D("20081.26")


@pytest.mark.parametrize(
    ("salary", "line_26000", "line_74", "expected"),
    [
        # Line 26000 of 57,375.00 is the top of column 1 ("or less"): line 74 is 14.5% of
        # 57,375.00, 8,319.375, rounded half-up to 8,319.38, and column 1's constant is 0.00.
        ("57919.19", "57375.00", "8319.38", "8319.38"),
        # A cent below: 14.5% of 57,374.99 is 8,319.37355, to 8,319.37.
        ("57919.18", "57374.99", "8319.37", "8319.37"),
        # A cent above: column 2, where 20.5% of 0.01 is 0.00205, to 0.00, on 8,319.38.
        ("57919.20", "57375.01", "0.00", "8319.38"),
        # A dollar below the top of column 2: 20.5% of 57,374.00 is 11,761.67, and line 76 is
        # 8,319.38 plus 11,761.67 = 20,081.05.
        ("115823", "114749.00", "11761.67", "20081.05"),
        # A dollar above it: column 3, whose constant is 20,081.25; line 74 is 26% of 1.00, 0.26.
        ("115825", "114751.00", "0.26", "20081.51"),
        # Line 26000 of 177,882.00 is the top of column 3: 26% of 63,132.00 is 16,414.32, and
        # line 76 is 20,081.25 plus 16,414.32 = 36,495.57, the column 4 constant.
        ("178956", "177882.00", "16414.32", "36495.57"),
        # A dollar below: 26% of 63,131.00 is 16,414.06, and line 76 is 36,495.31.
        ("178955", "177881.00", "16414.06", "36495.31"),
        # A dollar above: column 4, whose constant is 36,495.57; line 74 is 29% of 1.00, 0.29.
        ("178957", "177883.00", "0.29", "36495.86"),
        # Line 26000 of 253,414.00 is the top of column 4: 29% of 75,532.00 is 21,904.28, and
        # line 76 is 36,495.57 plus 21,904.28 = 58,399.85, the column 5 constant.
        ("254488", "253414.00", "21904.28", "58399.85"),
        # A dollar below: 29% of 75,531.00 is 21,903.99, and line 76 is 58,399.56.
        ("254487", "253413.00", "21903.99", "58399.56"),
        # A dollar above: column 5, whose constant is 58,399.85; line 74 is 33% of 1.00, 0.33.
        ("254489", "253415.00", "0.33", "58400.18"),
    ],
)
def test_line_76_at_each_bracket_start_and_either_side(
    take_home_service: TakeHomeService, salary: str, line_26000: str, line_74: str, expected: str
) -> None:
    t1, sheet = _sheets(take_home_service, salary)

    assert t1.get(bundled_kinds().kind(TAXABLE_INCOME)).value == D(line_26000)
    assert _value(sheet, LINE_74) == D(line_74)
    assert _value(sheet, LINE_75) == COLUMNS[_column_of(D(line_26000))][2]
    assert _value(sheet, LINE_76) == D(expected)


@pytest.mark.parametrize(
    "identifier",
    [LINE_70, LINE_71, LINE_72, LINE_73, LINE_74, LINE_75, LINE_76],
)
def test_the_part_a_kinds_are_registered_and_non_negative(identifier: str) -> None:
    kind = bundled_kinds().kind(identifier)

    assert kind.identifier == identifier
    assert non_negative(kind) is True


def test_line_76_names_lines_74_and_75_and_its_rounding_in_the_trace(
    take_home_service: TakeHomeService,
) -> None:
    _, sheet = _sheets(take_home_service, "70000")

    assert (
        "Line 74 (CA$2451.80) plus line 75 (CA$8319.38) gives CA$10771.18 "
        "(rounded to the nearest cent)."
    ) in EnglishTraceRenderer().render_all(sheet.trace, sheet)
