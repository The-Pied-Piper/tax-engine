"""T1 General 2025 (5006-R, Ontario) line 139 / line 41700 "Federal tax less credits", from the
salary alone.

Line 41700 is "Line 139 and line 41700: Line 134 minus line 138 (if negative, enter "0")" (T1
General 5006-R, CRA 5006-R-25E). Line 134 is
`ca/federal_tax` (line 40600); line 138 is `ca/credits_against_federal_tax` (line 41600, "Add lines
135 to 137"). The line prints "(if negative, enter "0")", so it is one
`core/subtract_not_below_zero`, rounded half-up to the cent with the shared `ca/cent_rounding`
dataset, and produces `ca/federal_tax_less_credits`, a non-negative kind.

The take-home filer has no credits against federal tax (basic credits only), so line 41600 is 0.00
at any salary and line 41700 equals line 134. The floor at 0 is not reachable with the real parts,
since line 138 is always 0 here.

The real parts are composed beside a test-local header: the salary, the real Schedule 8 and T2204
parts, the real T1 taxable-income lines and inputs, lines 30000, 84, 31260, 96, 98, 101, 106, 33500,
33800, 35000, 76, 40400, 125, 42900, 128, 130 and 132, lines 40600 and 41600 with the input of line
40600, and the part under test. The form declaration of line 41700 is test-local: its one export is
line 41700.

The salary is the only required input. Ontario resident, single filer, salary the only income, tax
withheld 0, basic credits only, as the take-home calculator states them.
"""

from __future__ import annotations

from decimal import Decimal
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
LINE_134 = "ca/federal_tax"
LINE_138 = "ca/credits_against_federal_tax"
LINE_139 = "ca/federal_tax_less_credits"
# The real parts composed beside the test's header: the salary, the real Schedule 8 and T2204
# parts, the real T1 taxable-income lines and inputs, lines 30000, 76, 84, 31260, 96, 98, 101, 106,
# 33500, 33800, 35000, 40400, 125, 42900, 128, 130 and 132, lines 40600 and 41600 with the input of
# line 40600, and the part under test.
PARTS = (
    "salary.yaml",
    *(part.name for part in sorted(TAKE_HOME.rglob("schedule_8*.yaml"))),
    *(part.name for part in sorted(TAKE_HOME.rglob("t2204*.yaml"))),
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
    "t1_tax_and_credits_line_76.yaml",
    "t1_tax_and_credits_line_31260.yaml",
    "t1_tax_and_credits_line_84.yaml",
    "t1_tax_and_credits_line_96.yaml",
    "t1_tax_and_credits_line_98.yaml",
    "t1_tax_and_credits_line_101.yaml",
    "t1_tax_and_credits_line_106.yaml",
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
)
HEADER = dedent("""\
    jurisdiction: CA-ON
    version: 1
    valid_from_tax_year: 2025
    outputs:
      - ca/employment_income
    capabilities: []
    """)
# The T1 tax and credits declaration, test-local: its one export is line 41700, the line under test.
T1_TAX_AND_CREDITS = dedent(f"""\
    form:
      name: {FORM}
      required: true
      exports:
        - {LINE_139}
    """)


def _sheet(take_home_service: TakeHomeService, salary: str) -> Worksheet:
    """The tax and credits sheet, with lines 134, 138 and 139 on it."""
    worksheets = take_home_service(HEADER, T1_TAX_AND_CREDITS, *PARTS).compute(
        ONTARIO, 2025, Artifact(EMPLOYMENT_INCOME, D(salary))
    )
    (sheet,) = worksheets[FORM]
    return sheet


@pytest.mark.parametrize(
    ("salary", "expected"),
    [
        # $70,000: 7,585.64 less 0.00.
        ("70000", "7585.64"),
        # $20,000: 158.09 less 0.00.
        ("20000", "158.09"),
        # $200,000: 39,467.74 less 0.00.
        ("200000", "39467.74"),
        # $10,000: line 134 is 0, so the line is 0.
        ("10000", "0.00"),
    ],
)
def test_line_41700_is_line_134_less_line_138_which_is_zero(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    sheet = _sheet(take_home_service, salary)
    kinds = bundled_kinds()

    line_139 = sheet.get(kinds.kind(LINE_139)).value
    assert line_139 == D(expected)
    assert line_139 == sheet.get(kinds.kind(LINE_134)).value
    assert sheet.get(kinds.kind(LINE_138)).value == D("0.00")
    assert line_139.as_tuple().exponent == -2


def test_line_41700_names_line_134_line_138_and_its_rounding_in_the_trace(
    take_home_service: TakeHomeService,
) -> None:
    sheet = _sheet(take_home_service, "70000")

    assert (
        "Line 40600 (CA$7585.64) less line 41600 (CA$0.00), not below 0, gives CA$7585.64 "
        "(rounded to the nearest cent)."
    ) in EnglishTraceRenderer().render_all(sheet.trace, sheet)


def test_the_41700_kind_is_registered_and_non_negative() -> None:
    kind = bundled_kinds().kind(LINE_139)

    assert kind.identifier == LINE_139
    assert non_negative(kind) is True
