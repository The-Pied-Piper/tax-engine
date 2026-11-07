"""T1 General 2025 (5006-R, Ontario) line 118 / line 35000 "Add lines 115 to 117. Total federal
non-refundable tax credits", from the salary alone.

Line 35000 is "Add lines 115 to 117" (T1 General 5006-R, CRA 5006-R-25E, confirmed in
docs/cra-forms-2025/5006-r-25e.txt). Line 115 is line 33800 (`ca/credit_amounts_at_credit_rate`).
Line 116 (line 34900, donations and gifts) is 0 for a filer with no donations, and line 117 (line
34990, the top-up tax credit) is 0 because the top-up only applies above 8,319.38 of line 33800,
which a salary-only line 33800 never reaches, so both are left out. Line 35000 is therefore one
`core/sum` over line 33800 only, rounded half-up to the cent with the shared `ca/cent_rounding`
dataset, and produces `ca/non_refundable_tax_credits`, a non-negative kind.

The real parts are composed beside a test-local header: the salary, the real Schedule 8 and T2204
parts, the real T1 taxable-income lines and inputs (line 23600 feeds line 30000), line 30000, line
84, line 31260, line 96, line 98, line 101, line 106, line 33500, line 33800 and the part under
test. The form declaration of line 35000 is test-local: its one export is line 35000.

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
LINE_33800 = "ca/credit_amounts_at_credit_rate"
LINE_35000 = "ca/non_refundable_tax_credits"
# The real parts composed beside the test's header: the salary, the real Schedule 8 and T2204
# parts, the real T1 taxable-income lines and inputs, lines 30000, 84, 31260, 96, 98, 101, 106,
# 33500 and 33800, and the part under test.
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
)
HEADER = dedent("""\
    jurisdiction: CA-ON
    version: 1
    valid_from_tax_year: 2025
    outputs:
      - ca/employment_income
    capabilities: []
    """)
# The T1 tax and credits declaration, test-local: its one export is line 35000, the line under test.
T1_TAX_AND_CREDITS = dedent(f"""\
    form:
      name: {FORM}
      required: true
      exports:
        - {LINE_35000}
    """)


def _sheet(take_home_service: TakeHomeService, salary: str) -> Worksheet:
    """The tax and credits sheet, with lines 33800 and 35000 on it."""
    worksheets = take_home_service(HEADER, T1_TAX_AND_CREDITS, *PARTS).compute(
        ONTARIO, 2025, Artifact(EMPLOYMENT_INCOME, D(salary))
    )
    (sheet,) = worksheets[FORM]
    return sheet


@pytest.mark.parametrize(
    ("salary", "expected"),
    [
        # $70,000: line 33800 alone (14.5% of 21,969.23), lines 34900 and 34990 being 0.
        ("70000", "3185.54"),
        # $20,000: line 33800 alone (14.5% of 18,744.75).
        ("20000", "2717.99"),
        # $200,000: line 33800 alone (14.5% of 21,590.31), on the taper.
        ("200000", "3130.59"),
    ],
)
def test_line_35000_is_line_33800(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    sheet = _sheet(take_home_service, salary)
    kinds = bundled_kinds()

    line_35000 = sheet.get(kinds.kind(LINE_35000)).value
    assert line_35000 == D(expected)
    assert line_35000 == sheet.get(kinds.kind(LINE_33800)).value
    assert line_35000.as_tuple().exponent == -2


def test_line_35000_names_line_33800_and_its_rounding_in_the_trace(
    take_home_service: TakeHomeService,
) -> None:
    sheet = _sheet(take_home_service, "70000")
    kinds = bundled_kinds()
    output = kinds.kind(LINE_35000)
    line_33800 = kinds.kind(LINE_33800)

    assert (
        f"{output.label}: {line_33800.label} 3185.54 = 3185.54 (half-up to 0.01)"
    ) in EnglishTraceRenderer().render_all(sheet.trace)


def test_the_line_35000_kind_is_registered_and_non_negative() -> None:
    kind = bundled_kinds().kind(LINE_35000)

    assert kind.identifier == LINE_35000
    assert non_negative(kind) is True
