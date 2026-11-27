"""T1 General 2025 (5006-R, Ontario) line 113 / line 33500 "Line 106 plus line 112", from the
salary alone.

Line 33500 is "Line 106 plus line 112" (T1 General 5006-R, CRA 5006-R-25E, confirmed). Line 106 is
`ca/credit_amounts_line_106`. Line 112 (line 33200, medical expenses: line 110 plus line 111) is
`ca/medical_claim`, built from the medical expenses lines 107 to 110 (line 111, other dependants,
is not built). Line 33500 is one `core/sum` over lines 106 and 112, rounded half-up to the cent
with the shared `ca/cent_rounding` dataset, and produces `ca/non_refundable_credit_amounts`, a
non-negative kind.

The real parts are composed beside a test-local header: the salary, the real Schedule 8 and T2204
parts, the real T1 taxable-income lines and inputs (line 23600 feeds line 30000), line 30000, line
84, line 31260, line 96, line 98, line 101, line 106, lines 107 to 110 and 33200 and the part under
test. The form declaration of line 33500 is test-local: its one export is line 33500.

The salary is the only input the caller gives, except the medical expenses where a test gives
them. Ontario resident, single filer, salary the only
income, tax withheld 0, basic credits only, as the take-home calculator states them.
"""

from __future__ import annotations

from decimal import Decimal
from textwrap import dedent

import pytest

from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca.catalog.personal_amounts import MEDICAL_EXPENSES
from tests.federal_forms import form_part_names
from tests.jurisdictions.ca_on.conftest import TakeHomeService
from tests.kinds import bundled_kinds, non_negative

D = Decimal
ONTARIO = JurisdictionCode("CA-ON")
FORM = "ca/t1_tax_and_credits"
LINE_106 = "ca/credit_amounts_line_106"
LINE_33500 = "ca/non_refundable_credit_amounts"
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
    "t1_tax_and_credits_line_78_worksheet_lines_1_to_3.yaml",
    "t1_tax_and_credits_line_78_worksheet_lines_4_to_7.yaml",
    "t1_tax_and_credits_line_78.yaml",
    "t1_tax_and_credits_line_84.yaml",
    "t1_tax_and_credits_line_96.yaml",
    "t1_tax_and_credits_line_98.yaml",
    "t1_tax_and_credits_line_101.yaml",
    "t1_tax_and_credits_line_106.yaml",
    "t1_tax_and_credits_line_107.yaml",
    "t1_tax_and_credits_line_108.yaml",
    "t1_tax_and_credits_line_109.yaml",
    "t1_tax_and_credits_line_110.yaml",
    "t1_tax_and_credits_line_111.yaml",
    "t1_tax_and_credits_line_33200.yaml",
    "t1_tax_and_credits_line_33500.yaml",
)
HEADER = dedent("""\
    jurisdiction: CA-ON
    version: 1
    valid_from_tax_year: 2025
    outputs: []
    capabilities: []
    """)
# The T1 tax and credits declaration, test-local: its one export is line 33500, the line under test.
T1_TAX_AND_CREDITS = dedent(f"""\
    form:
      name: {FORM}
      required: true
      exports:
        - {LINE_33500}
    """)


def _sheet(take_home_service: TakeHomeService, salary: str, *given: Artifact[Decimal]) -> Worksheet:
    """The tax and credits sheet, with lines 106 and 33500 on it."""
    worksheets = take_home_service(HEADER, T1_TAX_AND_CREDITS, *PARTS).compute(
        TaxCalculationRequest(ONTARIO, 2025, (Artifact(EMPLOYMENT_INCOME, D(salary)), *given))
    )
    (sheet,) = worksheets[FORM]
    return sheet


@pytest.mark.parametrize(
    ("salary", "expected"),
    [
        # $70,000: line 106 alone (16,129.00 + 5,840.23), line 112 being 0.
        ("70000", "21969.23"),
        # $20,000: line 106 alone (16,129.00 + 2,615.75).
        ("20000", "18744.75"),
    ],
)
def test_line_33500_is_line_106(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    sheet = _sheet(take_home_service, salary)
    kinds = bundled_kinds()

    line_33500 = sheet.get(kinds.kind(LINE_33500)).value
    assert line_33500 == D(expected)
    assert line_33500 == sheet.get(kinds.kind(LINE_106)).value
    assert line_33500.as_tuple().exponent == -2


def test_line_33500_names_line_106_and_its_rounding_in_the_trace(
    take_home_service: TakeHomeService,
) -> None:
    sheet = _sheet(take_home_service, "70000")

    assert (
        "Line 106 (CA$21969.23) plus line 33200 (CA$0.00) gives CA$21969.23 "
        "(rounded to the nearest cent)."
    ) in EnglishTraceRenderer().render_all(sheet.trace, sheet)


def test_the_line_33500_kind_is_registered_and_non_negative() -> None:
    kind = bundled_kinds().kind(LINE_33500)

    assert kind.identifier == LINE_33500
    assert non_negative(kind) is True


def test_line_33500_adds_line_112_the_medical_expenses_over_the_threshold(
    take_home_service: TakeHomeService,
) -> None:
    # $70,000: line 106 is 21,969.23; medical expenses of 5,000.00 less line 109 (2,080.05, 3% of
    # net income 69,335.00) are 2,919.95, so line 33500 is 24,889.18.
    sheet = _sheet(take_home_service, "70000", Artifact(MEDICAL_EXPENSES, D("5000")))

    assert sheet.get(bundled_kinds().kind(LINE_33500)).value == D("24889.18")
    assert (
        "Line 106 (CA$21969.23) plus line 33200 (CA$2919.95) gives CA$24889.18 "
        "(rounded to the nearest cent)."
    ) in EnglishTraceRenderer().render_all(sheet.trace, sheet)
