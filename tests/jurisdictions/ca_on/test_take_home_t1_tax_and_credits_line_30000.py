"""T1 General 2025 (5006-R, Ontario) line 30000 "Basic personal amount", from the salary alone.

Line 30000 is calculated on worksheet 5000-D1 (CRA 5000-D1-25E, confirmed in
docs/cra-forms-2025/5000-d1-25e.txt, "Line 30000 - Basic personal amount"). The worksheet says:
"If the amount from line 23600 of your return is: - $177,882 or less, enter $16,129 on line 30000
of your return - $253,414 or more, enter $14,538 on line 30000 of your return. Otherwise, complete
the calculation below." Then: "Line 1: Base amount 14,538.00", "Line 2: Supplement amount 1,591.00",
"Line 3: Amount from line 23600 of your return", "Line 4: Income threshold 177,882.00", "Line 5:
Line 3 minus line 4", "Line 6: 75,532.00", "Line 7: Line 5 divided by line 6", "Line 8: 1,591.00",
"Line 9: Line 7 multiplied by line 8", "Line 10: Line 2 minus line 9 (if negative, enter "0")" and
"Line 11: Line 1 plus line 10 Enter this amount on line 30000 of your return. (maximum $16,129)".

The take-home filer has the amount from line 23600 as the one figure of the worksheet, so the step
is two parts of the form. Line 3 is a `core/record_total` over the T1 taxable-income record list
`ca/t1_taxable_income.net_income` (the engine lets one form read another form's exports only as
record lists), and the new kind `ca/basic_personal_amount_net_income_line_3` is non-negative. Line
30000 is a `ca/tapered_amount` over the dataset `ca/basic_personal_amount` 2025 (base 14,538,
supplement 1,591, threshold 177,882, range 75,532, rounded half-up to the cent) that consumes that
line 3 as its base and produces the existing kind `ca/basic_personal_amount`. The taper gives the
two printed shortcuts too: at or below the threshold it is base plus supplement (16,129), and at or
above threshold plus range (253,414) it is the base (14,538).

The T1 side is the real `ca/t1_taxable_income` form: its header part and the real lines 15000,
23300 (deductions, read from the real Schedule 8), 23400, 23600, 23600 signed, 26000 and the
optional inputs parts, so line 23600 comes from the salary through the real lines. The form header
of line 30000 is test-local: it declares `ca/basic_personal_amount` as its one export.

The salary is the only input the caller gives. Ontario resident, single filer, salary the only
income, tax withheld 0, basic credits only, as the take-home calculator states them.

Line 23600 is the salary less 1,074.00 once the salary is high enough for the CPP and EI maximums
(1 a dollar of salary), so salaries 178,956, 216,722 and 254,488 give line 23600 of exactly
177,882.00, 215,648.00 and 253,414.00, and the boundaries are tested exactly and one dollar inside
each side. Line 30000 is pinned as a figure for each salary and checked against the printed
worksheet (lines 5 to 11) for salaries between the two thresholds, computed independently of the
engine from exact fractions. Line 3 is pinned at 70,000, and the two kinds are pinned as
registered and non-negative.
"""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal
from fractions import Fraction
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
LINE_3 = "ca/basic_personal_amount_net_income_line_3"
LINE_30000 = "ca/basic_personal_amount"
NET_INCOME = "ca/net_income"
# The real parts composed beside the test's header: the salary, the real Schedule 8, and the real
# T1 taxable-income lines and inputs, so line 23600 is read from the salary through the real lines.
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
    "t1_tax_and_credits_line_30000.yaml",
)
HEADER = dedent("""\
    jurisdiction: CA-ON
    version: 1
    valid_from_tax_year: 2025
    outputs:
      - ca/employment_income
    capabilities: []
    """)
# The T1 tax and credits declaration, test-local: its one export is line 30000, the only line
# composed here.
T1_TAX_AND_CREDITS = dedent(f"""\
    form:
      name: {FORM}
      required: true
      exports:
        - {LINE_30000}
    """)
# The printed figures of worksheet 5000-D1 for line 30000, as the form states them.
BASE = Fraction(14538)
SUPPLEMENT = Fraction(1591)
THRESHOLD = Fraction(177882)
RANGE = Fraction(75532)


def _sheets(take_home_service: TakeHomeService, salary: str) -> tuple[Worksheet, Worksheet]:
    """The T1 taxable-income sheet (line 23600 is read from it) and the tax and credits sheet."""
    worksheets = take_home_service(HEADER, T1_TAX_AND_CREDITS, *PARTS).compute(
        ONTARIO, 2025, Artifact(EMPLOYMENT_INCOME, D(salary))
    )
    (t1,) = worksheets[T1_FORM]
    (sheet,) = worksheets[FORM]
    return t1, sheet


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
        # Line 23600 of 69,335.00 is below the threshold: the maximum, 16,129.00.
        ("70000", "16129.00"),
        # Line 23600 of 198,926.00: 1,591.00 less 1,591.00 times 21,044.00 over 75,532.00
        # (443.27) is 1,147.73, and 14,538.00 plus it is 15,685.73.
        ("200000", "15685.73"),
        # Line 23600 of 215,648.00 is the middle of the range: 14,538.00 plus half of 1,591.00.
        ("216722", "15333.50"),
        # Line 23600 of 300,000 less 1,074.00 is above 253,414.00: the base, 14,538.00.
        ("300000", "14538.00"),
    ],
)
def test_line_30000_is_the_basic_personal_amount(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    _, sheet = _sheets(take_home_service, salary)

    assert sheet.get(bundled_kinds().kind(LINE_30000)).value == D(expected)


@pytest.mark.parametrize(
    ("salary", "line_23600", "expected"),
    [
        # Exactly the threshold "$177,882 or less": 16,129.00.
        ("178956", "177882.00", "16129.00"),
        # One dollar over: 1,591.00 times 1.00 over 75,532.00 is 0.0211, so 16,128.98.
        ("178957", "177883.00", "16128.98"),
        # One dollar under "$253,414 or more": 14,538.00 plus 0.0211, so 14,538.02.
        ("254487", "253413.00", "14538.02"),
        # Exactly "$253,414 or more": 14,538.00.
        ("254488", "253414.00", "14538.00"),
    ],
)
def test_line_30000_at_the_thresholds(
    take_home_service: TakeHomeService, salary: str, line_23600: str, expected: str
) -> None:
    t1, sheet = _sheets(take_home_service, salary)

    assert t1.get(bundled_kinds().kind(NET_INCOME)).value == D(line_23600)
    assert sheet.get(bundled_kinds().kind(LINE_30000)).value == D(expected)


@pytest.mark.parametrize("salary", ["178957", "190000", "200000", "216722", "240000", "254487"])
def test_line_30000_is_the_printed_worksheet_between_the_thresholds(
    take_home_service: TakeHomeService, salary: str
) -> None:
    t1, sheet = _sheets(take_home_service, salary)
    line_3 = t1.get(bundled_kinds().kind(NET_INCOME)).value

    assert D("177882") < line_3 < D("253414")
    assert sheet.get(bundled_kinds().kind(LINE_30000)).value == _printed_worksheet(line_3)


def test_line_3_is_the_line_23600_amount_at_70000(take_home_service: TakeHomeService) -> None:
    _, sheet = _sheets(take_home_service, "70000")

    assert sheet.get(bundled_kinds().kind(LINE_3)).value == D("69335.00")


def test_the_line_3_kind_is_registered_and_non_negative() -> None:
    # Non-negative: line 3 is the amount from line 23600, which the worksheet reads as an amount
    # to compare with the threshold, never as a negative figure (line 23600 is not below "0").
    kind = bundled_kinds().kind(LINE_3)

    assert kind.identifier == LINE_3
    assert non_negative(kind) is True


def test_the_line_30000_kind_is_registered_and_non_negative() -> None:
    kind = bundled_kinds().kind(LINE_30000)

    assert kind.identifier == LINE_30000
    assert non_negative(kind) is True


def test_line_30000_names_line_3_and_the_range_in_the_trace(
    take_home_service: TakeHomeService,
) -> None:
    # The sentence as the tapered-amount renderer prints it today (the reduction as a fraction is
    # a known wording issue; update this pin where that is fixed).
    _, sheet = _sheets(take_home_service, "70000")
    kinds = bundled_kinds()

    assert (
        f"{kinds.kind(LINE_30000).label}: 14538 plus 1591 less 0 for {kinds.kind(LINE_3).label} "
        "69335.00 over 177882 (range 75532), not below 14538 (half-up to 0.01)"
    ) in EnglishTraceRenderer().render_all(sheet.trace)
