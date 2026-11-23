"""T1 General 2025 (5006-R, Alberta) line 48200 "Total credits", with line 47900 blank.

5006-R-25E: "Line 166 and line 48200: Add lines 150 to 165. Total credits". Line 48200 is a
`core/sum` of the EI overpayment (line 45000), the Canada workers benefit (line 45300) and the
provincial or territorial credits (line 47900), rounded to the cent by `ca/cent_rounding`. No
Alberta form supplies line 47900, so it is blank for the Alberta take-home filer and the sum reads
it as 0, with its own "left blank, taken as 0" row in the trace.

The test composes the real salary, Schedule 8, T1 taxable income, T2204 and Schedule 6 parts and
the real T1 line 47900 and line 48200 parts. The header and the form's export of line 48200 are
test-local. The salary is the only input. Alberta resident, single filer, salary the only income,
tax withheld 0, basic credits only. Figures are the Ontario ones (the federal credits do not depend
on the province): 0.00 at $70,000 and 1,633.00 (the Canada workers benefit) at $20,000.
"""

from __future__ import annotations

from decimal import Decimal
from textwrap import dedent

import pytest

from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.trace import BlankFallbackLine
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tests.federal_forms import form_part_names
from tests.jurisdictions.ca_ab.conftest import TakeHomeService
from tests.kinds import bundled_kinds

D = Decimal
ALBERTA = JurisdictionCode("CA-AB")
FORM = "ca/t1_tax_and_credits"
LINE_47900 = "ca/provincial_credits_line_47900"
LINE_48200 = "ca/total_credits"
PARTS = (
    *form_part_names("schedule_8"),
    *form_part_names("t1_taxable_income", "t1_employment_income", "t1_lines_copied_by_provinces"),
    *form_part_names("t2204"),
    *form_part_names("schedule_6"),
    "t1_tax_and_credits_line_47900.yaml",
    "t1_tax_and_credits_line_48200.yaml",
)
HEADER = dedent("""\
    jurisdiction: CA-AB
    version: 1
    valid_from_tax_year: 2025
    outputs: []
    capabilities: []
    """)
# The T1 tax and credits declaration, test-local: its one export is line 48200, the only line
# composed here.
T1_TAX_AND_CREDITS = dedent(f"""\
    form:
      name: {FORM}
      required: true
      exports:
        - {LINE_48200}
    """)


def _sheet(take_home_service: TakeHomeService, salary: str) -> Worksheet:
    worksheets = take_home_service(HEADER, T1_TAX_AND_CREDITS, *PARTS).compute(
        TaxCalculationRequest(ALBERTA, 2025, (Artifact(EMPLOYMENT_INCOME, D(salary)),))
    )
    (sheet,) = worksheets[FORM]
    return sheet


@pytest.mark.parametrize(("salary", "total"), [("70000", "0.00"), ("20000", "1633.00")])
def test_albertas_blank_line_47900_is_taken_as_0_in_line_48200(
    take_home_service: TakeHomeService, salary: str, total: str
) -> None:
    sheet = _sheet(take_home_service, salary)
    kinds = bundled_kinds()

    assert sheet.get(kinds.kind(LINE_47900)).is_blank
    assert sheet.get(kinds.kind(LINE_48200)).value == D(total)
    assert sheet.get(kinds.kind(LINE_48200)).value.as_tuple().exponent == -2


def test_line_48200_prints_a_left_blank_row_for_the_blank_line_47900(
    take_home_service: TakeHomeService,
) -> None:
    sheet = _sheet(take_home_service, "70000")
    kind = bundled_kinds().kind(LINE_47900)

    (blank,) = [
        each for each in sheet.trace if isinstance(each, BlankFallbackLine) and each.kind is kind
    ]
    assert blank.fallback == 0
    rows = EnglishTraceRenderer().render_all(sheet.trace, sheet)
    assert any("Left blank, taken as" in row and "0.00" in row for row in rows)
