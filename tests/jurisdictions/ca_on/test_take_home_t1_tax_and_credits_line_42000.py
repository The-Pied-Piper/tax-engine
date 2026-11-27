"""T1 General 2025 (5006-R, Ontario) line 142 / line 42000 "Net federal tax", from the
salary alone.

Line 42000 is "Line 142 and line 42000: Add lines 139 to 141. Net federal tax" (T1 General
5006-R, CRA 5006-R-25E). Line 139 is
`ca/federal_tax_less_credits` (line 41700, same form). Lines 140 (41500) and 141 (41800) are absent
for the take-home filer and are left out, so line 42000 is one `core/sum` over line 139 only,
rounded half-up to the cent with the shared `ca/cent_rounding` dataset, and produces
`ca/net_federal_tax`, a non-negative kind. It equals line 41700 at any salary.

The real parts are composed beside a test-local header: the salary, the real Schedule 8 and T2204
parts, the real T1 taxable-income lines and inputs, lines 30000, 84, 31260, 96, 98, 101, 106, 33500,
33800, 35000, 76, 40400, 125, 42900, 128, 130 and 132, lines 40600, 41600 and 41700 with the input
of line 40600, and the part under test. The form declaration of line 42000 is test-local: its one
export is line 42000.

The salary is the only required input. Ontario resident, single filer, salary the only income, tax
withheld 0, basic credits only, as the take-home calculator states them.
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
from tests.federal_forms import form_part_names
from tests.jurisdictions.ca_on.conftest import TakeHomeService
from tests.kinds import bundled_kinds, non_negative

D = Decimal
ONTARIO = JurisdictionCode("CA-ON")
FORM = "ca/t1_tax_and_credits"
LINE_139 = "ca/federal_tax_less_credits"
LINE_142 = "ca/net_federal_tax"
# The real parts composed beside the test's header: the salary, the real Schedule 8 and T2204
# parts, the real T1 taxable-income lines and inputs, lines 30000, 76, 31260, 84, 96, 98, 101, 106,
# 33500, 33800, 35000, 125, 40400, 42900, 128, 130 and 132, the input of line 40600, lines 40600 and
# 41600, line 41700 and the part under test.
PARTS = (
    *form_part_names("t1_lines_copied_by_provinces"),
    *form_part_names("schedule_8"),
    *form_part_names("t2204"),
    *form_part_names("t1_taxable_income", "t1_employment_income"),
    "t1_tax_and_credits_line_30000.yaml",
    "t1_tax_and_credits_line_76.yaml",
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
    "t1_tax_and_credits_line_33800.yaml",
    "t1_tax_and_credits_line_35000.yaml",
    "t1_tax_and_credits_line_125.yaml",
    "t1_tax_and_credits_line_40400.yaml",
    "t1_tax_and_credits_line_42900.yaml",
    "t1_tax_and_credits_line_128.yaml",
    "t1_tax_and_credits_line_40500_inputs.yaml",
    "t1_tax_and_credits_line_130.yaml",
    "t1_tax_and_credits_line_132.yaml",
    "t1_tax_and_credits_line_40600_inputs.yaml",
    "t1_tax_and_credits_line_40600.yaml",
    "t1_tax_and_credits_line_41600.yaml",
    "t1_tax_and_credits_line_41700.yaml",
    "t1_tax_and_credits_line_42000.yaml",
)
HEADER = dedent("""\
    jurisdiction: CA-ON
    version: 1
    valid_from_tax_year: 2025
    outputs: []
    capabilities: []
    """)
# The T1 tax and credits declaration, test-local: its one export is line 42000, the line under test.
T1_TAX_AND_CREDITS = dedent(f"""\
    form:
      name: {FORM}
      required: true
      exports:
        - {LINE_142}
    """)


def _sheet(take_home_service: TakeHomeService, salary: str) -> Worksheet:
    """The tax and credits sheet, with lines 139 and 142 on it."""
    worksheets = take_home_service(HEADER, T1_TAX_AND_CREDITS, *PARTS).compute(
        TaxCalculationRequest(ONTARIO, 2025, (Artifact(EMPLOYMENT_INCOME, D(salary)),))
    )
    (sheet,) = worksheets[FORM]
    return sheet


@pytest.mark.parametrize(
    ("salary", "expected"),
    [
        # $70,000: line 139 is 7,585.64.
        ("70000", "7585.64"),
        # $10,000: line 139 is 0, so the line is 0.
        ("10000", "0.00"),
    ],
)
def test_line_42000_is_line_139_alone(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    sheet = _sheet(take_home_service, salary)
    kinds = bundled_kinds()

    line_142 = sheet.get(kinds.kind(LINE_142)).value
    assert line_142 == D(expected)
    assert line_142 == sheet.get(kinds.kind(LINE_139)).value
    assert line_142.as_tuple().exponent == -2


def test_line_42000_names_line_139_and_its_rounding_in_the_trace(
    take_home_service: TakeHomeService,
) -> None:
    sheet = _sheet(take_home_service, "70000")

    assert (
        "Line 41700 (CA$7585.64) gives CA$7585.64 (rounded to the nearest cent)."
    ) in EnglishTraceRenderer().render_all(sheet.trace, sheet)


def test_the_42000_kind_is_registered_and_non_negative() -> None:
    kind = bundled_kinds().kind(LINE_142)

    assert kind.identifier == LINE_142
    assert non_negative(kind) is True
