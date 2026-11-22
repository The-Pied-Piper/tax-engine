"""T1 General 2025 (5006-R, Ontario) Step 5 Part B line 106 "Add lines 101 to 105.", from the
salary alone.

Line 106 is "Add lines 101 to 105." (T1 General 5006-R, CRA 5006-R-25E, confirmed). Line 101 is
`ca/credit_amounts_subtotal`. Line 102 (line 31900, student loan interest) is a copy of line 31900,
which the T1 lines copied by provinces form owns as an optional input (0 when blank) and exports,
so it is a `core/record_total` (`ca/student_loan_interest_line_102`). Lines 103 to 105 are not
built and are left out. Line 106 is one `core/sum` over lines 101 and 102, rounded half-up to the
cent with the shared `ca/cent_rounding` dataset, and produces `ca/credit_amounts_line_106`, a
non-negative kind.

The real parts are composed beside a test-local header: the salary, the real Schedule 8 and T2204
parts, the real T1 taxable-income lines and inputs (line 23600 feeds line 30000), line 30000, line
84, line 31260, line 96, line 98, line 101 and the part under test. The form declaration of line
106 is test-local: its one export is line 106.

The salary is the only input the caller gives, except line 31900 where a test gives it. Ontario
resident, single filer, salary the only income, tax withheld 0, basic credits only, as the
take-home calculator states them."""

from __future__ import annotations

from decimal import Decimal
from textwrap import dedent

import pytest

from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca.catalog.non_refundable_credits import STUDENT_LOAN_INTEREST
from tests.federal_forms import form_part_names
from tests.jurisdictions.ca_on.conftest import TakeHomeService
from tests.kinds import bundled_kinds, non_negative

D = Decimal
ONTARIO = JurisdictionCode("CA-ON")
FORM = "ca/t1_tax_and_credits"
LINE_101 = "ca/credit_amounts_subtotal"
LINE_106 = "ca/credit_amounts_line_106"
# The real parts composed beside the test's header: the salary, the real Schedule 8 and T2204
# parts, the real T1 taxable-income lines and inputs, lines 30000, 84, 31260, 96 and 98, and the
# part under test.
PARTS = (
    *form_part_names("t1_lines_copied_by_provinces"),
    *form_part_names("schedule_8"),
    *form_part_names("t2204"),
    *form_part_names("t1_taxable_income", "t1_employment_income"),
    "t1_tax_and_credits_line_30000.yaml",
    "t1_tax_and_credits_line_31260.yaml",
    "t1_tax_and_credits_line_84.yaml",
    "t1_tax_and_credits_line_96.yaml",
    "t1_tax_and_credits_line_98.yaml",
    "t1_tax_and_credits_line_101.yaml",
    "t1_tax_and_credits_line_106.yaml",
)
HEADER = dedent("""\
    jurisdiction: CA-ON
    version: 1
    valid_from_tax_year: 2025
    outputs: []
    capabilities: []
    """)
# The T1 tax and credits declaration, test-local: its one export is line 106, the line under test.
T1_TAX_AND_CREDITS = dedent(f"""\
    form:
      name: {FORM}
      required: true
      exports:
        - {LINE_106}
    """)


def _sheet(take_home_service: TakeHomeService, salary: str, *given: Artifact[Decimal]) -> Worksheet:
    """The tax and credits sheet, with lines 101 and 106 on it."""
    worksheets = take_home_service(HEADER, T1_TAX_AND_CREDITS, *PARTS).compute(
        ONTARIO, 2025, Artifact(EMPLOYMENT_INCOME, D(salary)), *given
    )
    (sheet,) = worksheets[FORM]
    return sheet


@pytest.mark.parametrize(
    ("salary", "expected"),
    [
        # $70,000: line 101 alone (16,129.00 + 5,840.23), lines 102 to 105 being 0.
        ("70000", "21969.23"),
        # $20,000: line 101 alone (16,129.00 + 2,615.75).
        ("20000", "18744.75"),
    ],
)
def test_line_106_is_line_101(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    sheet = _sheet(take_home_service, salary)
    kinds = bundled_kinds()

    line_106 = sheet.get(kinds.kind(LINE_106)).value
    assert line_106 == D(expected)
    assert line_106 == sheet.get(kinds.kind(LINE_101)).value
    assert line_106.as_tuple().exponent == -2


def test_line_106_names_line_101_and_its_rounding_in_the_trace(
    take_home_service: TakeHomeService,
) -> None:
    sheet = _sheet(take_home_service, "70000")
    assert (
        "Line 101 (CA$21969.23) plus line 31900 (CA$0.00) gives CA$21969.23 "
        "(rounded to the nearest cent)."
    ) in EnglishTraceRenderer().render_all(sheet.trace, sheet)


def test_the_line_106_kind_is_registered_and_non_negative() -> None:
    kind = bundled_kinds().kind(LINE_106)

    assert kind.identifier == LINE_106
    assert non_negative(kind) is True


def test_line_106_adds_line_102_the_student_loan_interest(
    take_home_service: TakeHomeService,
) -> None:
    # $70,000: line 101 is 21,969.23; line 31900 of 300.00 is line 102.
    sheet = _sheet(take_home_service, "70000", Artifact(STUDENT_LOAN_INTEREST, D("300")))
    kinds = bundled_kinds()

    assert sheet.get(kinds.kind("ca/student_loan_interest_line_102")).value == D("300.00")
    assert sheet.get(kinds.kind(LINE_106)).value == D("22269.23")
    assert (
        "Line 101 (CA$21969.23) plus line 31900 (CA$300.00) gives CA$22269.23 "
        "(rounded to the nearest cent)."
    ) in EnglishTraceRenderer().render_all(sheet.trace, sheet)
