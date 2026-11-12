"""T1 General 2025 (5006-R, Ontario) line 125 "Add lines 122 to 124.", from the salary alone.

Line 125 is "Add lines 122 to 124" (T1 General 5006-R, CRA 5006-R-25E, confirmed in
docs/cra-forms-2025/5006-r-25e.txt). Line 122 is "Amount from line 35000"
(`ca/non_refundable_tax_credits`), a pure copy with no step. Line 123 (line 40425, the federal
dividend tax credit) and line 124 (line 40427, the minimum tax carryover) are 0 for a filer with no
dividends and no minimum tax carryover, so both are left out. Line 125 is therefore one `core/sum`
over line 35000 only, rounded half-up to the cent with the shared `ca/cent_rounding` dataset, and
produces `ca/credits_against_basic_federal_tax`, a non-negative kind.

The real parts are composed beside a test-local header: the salary, the real Schedule 8 and T2204
parts, the real T1 taxable-income lines and inputs (line 23600 feeds line 30000), line 30000, line
84, line 31260, line 96, line 98, line 101, line 106, line 33500, line 33800, line 35000 and the
part under test. The form declaration of line 125 is test-local: its one export is line 125.

The salary is the only input the caller gives. Ontario resident, single filer, salary the only
income, tax withheld 0, basic credits only, as the take-home calculator states them.
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
LINE_35000 = "ca/non_refundable_tax_credits"
LINE_125 = "ca/credits_against_basic_federal_tax"
# The real parts composed beside the test's header: the salary, the real Schedule 8 and T2204
# parts, the real T1 taxable-income lines and inputs, lines 30000, 84, 31260, 96, 98, 101, 106,
# 33500, 33800 and 35000, and the part under test.
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
)
HEADER = dedent("""\
    jurisdiction: CA-ON
    version: 1
    valid_from_tax_year: 2025
    outputs:
      - ca/employment_income
    capabilities: []
    """)
# The T1 tax and credits declaration, test-local: its one export is line 125, the line under test.
T1_TAX_AND_CREDITS = dedent(f"""\
    form:
      name: {FORM}
      required: true
      exports:
        - {LINE_125}
    """)


def _sheet(take_home_service: TakeHomeService, salary: str) -> Worksheet:
    """The tax and credits sheet, with lines 35000 and 125 on it."""
    worksheets = take_home_service(HEADER, T1_TAX_AND_CREDITS, *PARTS).compute(
        ONTARIO, 2025, Artifact(EMPLOYMENT_INCOME, D(salary))
    )
    (sheet,) = worksheets[FORM]
    return sheet


@pytest.mark.parametrize(
    ("salary", "expected"),
    [
        # $70,000: line 35000 alone, lines 123 and 124 being 0.
        ("70000", "3185.54"),
        # $20,000: line 35000 alone.
        ("20000", "2717.99"),
        # $200,000: line 35000 alone, on the taper.
        ("200000", "3130.59"),
    ],
)
def test_line_125_is_line_35000(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    sheet = _sheet(take_home_service, salary)
    kinds = bundled_kinds()

    line_125 = sheet.get(kinds.kind(LINE_125)).value
    assert line_125 == D(expected)
    assert line_125 == sheet.get(kinds.kind(LINE_35000)).value
    assert line_125.as_tuple().exponent == -2


def test_line_125_names_line_35000_and_its_rounding_in_the_trace(
    take_home_service: TakeHomeService,
) -> None:
    sheet = _sheet(take_home_service, "70000")
    assert (
        "Line 35000 (CA$3185.54) gives CA$3185.54 (rounded to the nearest cent)."
    ) in EnglishTraceRenderer().render_all(sheet.trace, sheet)


def test_the_line_125_kind_is_registered_and_non_negative() -> None:
    kind = bundled_kinds().kind(LINE_125)

    assert kind.identifier == LINE_125
    assert non_negative(kind) is True
