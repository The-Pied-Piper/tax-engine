"""T1 General 2025 (5006-R, Ontario) Step 5 Part B line 96, from the salary alone.

Line 96 is "Line 96: Add lines 86 to 95." (T1 General 5006-R, CRA 5006-R-25E, confirmed in
cra-docs/docs/cra-forms-2025/5006-r-25e.txt, line 548). The take-home filer has three of the lines
86 to 95:
line 86 (`ca/cpp_base_contributions_line_86`, the base CPP of Schedule 8 for T1 line 30800), line 88
(`ca/ei_premiums_line_88`, the EI premiums of T2204 line 16 for T1 line 31200) and line 92
(`ca/canada_employment_amount`, the Canada employment amount of T1 line 31260). The other lines
from 86 to 95 are 0 for this filer and are left out.

The part has three steps. Lines 86 and 88 are pure reads of other forms, so each is a
`core/record_total` over the record list the other form exports (the engine lets one form read
another form's exports only as record lists): the Schedule 8 record list
`ca/schedule_8.schedule_8_cpp_base_contributions_on_return` and the T2204 record list
`ca/t2204.t2204_line_16`. Line 96 is a `core/sum`, rounded to the cent, of the two new kinds and
the line 31260 amount. All three new kinds are non-negative amounts.

The real parts are composed beside a test-local header: the salary, the real Schedule 8 and T2204
parts (their headers export the two read kinds), the real line 10400 input, the real line 31260
part and the part under test. The form declaration of line 96 is test-local: its one export is
line 96.
"""

from __future__ import annotations

from decimal import Decimal
from textwrap import dedent
from typing import Any

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
SCHEDULE_8_FORM = "ca/schedule_8"
SCHEDULE_8_BASE = "ca/schedule_8_cpp_base_contributions_on_return"
T2204_FORM = "ca/t2204"
T2204_LINE_16 = "ca/t2204_line_16"
CANADA_EMPLOYMENT_AMOUNT = "ca/canada_employment_amount"
LINE_86 = "ca/cpp_base_contributions_line_86"
LINE_88 = "ca/ei_premiums_line_88"
LINE_96 = "ca/credits_subtotal_line_96"
# The real parts composed beside the test's header: the salary, the real Schedule 8 and T2204 parts
# (every part of each, so their on-return and line 16 kinds are produced as they are on the return),
# the real line 10400 input, the real line 31260 part, and the part under test.
PARTS = (
    "salary.yaml",
    *(part.name for part in sorted(TAKE_HOME.rglob("schedule_8*.yaml"))),
    *(part.name for part in sorted(TAKE_HOME.rglob("t2204*.yaml"))),
    "t1_taxable_income_line_10400_inputs.yaml",
    "t1_tax_and_credits_line_31260.yaml",
    "t1_tax_and_credits_line_96.yaml",
)
HEADER = dedent("""\
    jurisdiction: CA-ON
    version: 1
    valid_from_tax_year: 2025
    outputs:
      - ca/employment_income
    capabilities: []
    """)
# The T1 tax and credits declaration, test-local: its one export is line 96, the only line composed
# here as an export.
T1_TAX_AND_CREDITS = dedent(f"""\
    form:
      name: {FORM}
      required: true
      exports:
        - {LINE_96}
    """)


def _sheets(
    take_home_service: TakeHomeService, salary: str
) -> tuple[Worksheet, Worksheet, Worksheet]:
    """The tax and credits sheet, the Schedule 8 sheet and the T2204 sheet for `salary`."""
    worksheets = take_home_service(HEADER, T1_TAX_AND_CREDITS, *PARTS).compute(
        ONTARIO, 2025, Artifact(EMPLOYMENT_INCOME, D(salary))
    )
    (sheet,) = worksheets[FORM]
    (schedule_8,) = worksheets[SCHEDULE_8_FORM]
    (t2204,) = worksheets[T2204_FORM]
    return sheet, schedule_8, t2204


def _value(sheet: Worksheet, kind_identifier: str) -> Any:
    return sheet.get(bundled_kinds().kind(kind_identifier)).value


@pytest.mark.parametrize(
    ("salary", "expected"),
    [
        # $70,000: Schedule 8 base contributions are 3,291.75 (the cent-exact 4.95% of 66,500.00).
        ("70000", "3291.75"),
        # $200,000: the Schedule 8 base contributions are at the printed maximum, 3,356.10.
        ("200000", "3356.10"),
        # $20,000: 4.95% of 16,500.00, 816.75.
        ("20000", "816.75"),
    ],
)
def test_line_86_is_the_schedule_8_base_contributions(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    sheet, schedule_8, _ = _sheets(take_home_service, salary)

    assert _value(sheet, LINE_86) == D(expected)
    assert _value(schedule_8, SCHEDULE_8_BASE) == D(expected)


@pytest.mark.parametrize(
    ("salary", "expected"),
    [
        # $70,000 and $200,000: the T2204 line 16 is the 1,077.48 cap, the most the EI premium is.
        ("70000", "1077.48"),
        ("200000", "1077.48"),
        # $20,000: 1.64% of 20,000.00 is 328.00, below the cap.
        ("20000", "328.00"),
        # $1,000: under the EI exemption of $2,000, so T2204 line 16 is 0.
        ("1000", "0.00"),
    ],
)
def test_line_88_is_the_t2204_line_16(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    sheet, _, t2204 = _sheets(take_home_service, salary)

    assert _value(sheet, LINE_88) == D(expected)
    assert _value(t2204, T2204_LINE_16) == D(expected)


@pytest.mark.parametrize(
    ("salary", "expected"),
    [
        # $70,000: 3,291.75 + 1,077.48 + 1,471.00.
        ("70000", "5840.23"),
        # $200,000: 3,356.10 + 1,077.48 + 1,471.00.
        ("200000", "5904.58"),
        # $20,000: 816.75 + 328.00 + 1,471.00.
        ("20000", "2615.75"),
        # $1,000: 0 + 0 + 1,000.00, the Canada employment amount below the $1,471 cap being the
        # salary itself.
        ("1000", "1000.00"),
    ],
)
def test_line_96_is_the_sum_of_lines_86_to_95_for_the_take_home_filer(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    sheet, _, _ = _sheets(take_home_service, salary)

    assert _value(sheet, LINE_96) == D(expected)


@pytest.mark.parametrize("salary", ["1000", "20000", "70000", "200000"])
def test_line_96_is_line_86_plus_line_88_plus_the_canada_employment_amount(
    take_home_service: TakeHomeService, salary: str
) -> None:
    sheet, _, _ = _sheets(take_home_service, salary)

    assert _value(sheet, LINE_96) == (
        _value(sheet, LINE_86) + _value(sheet, LINE_88) + _value(sheet, CANADA_EMPLOYMENT_AMOUNT)
    )


@pytest.mark.parametrize("kind_identifier", [LINE_86, LINE_88, LINE_96])
def test_the_line_96_kinds_are_registered_and_non_negative(kind_identifier: str) -> None:
    # Non-negative: each is a CPP or EI amount, or the Canada employment amount, that the form
    # adds up, never a negative figure.
    kind = bundled_kinds().kind(kind_identifier)

    assert kind.identifier == kind_identifier
    assert non_negative(kind) is True


def test_line_96_names_its_three_parts_and_its_rounding_in_the_trace(
    take_home_service: TakeHomeService,
) -> None:
    sheet, _, _ = _sheets(take_home_service, "70000")

    assert (
        "Line 30800 (CA$3291.75) plus line 31200 (CA$1077.48) plus line 31260 (CA$1471.00) "
        "gives CA$5840.23 "
        "(rounded to the nearest cent)."
    ) in EnglishTraceRenderer().render_all(sheet.trace, sheet)
