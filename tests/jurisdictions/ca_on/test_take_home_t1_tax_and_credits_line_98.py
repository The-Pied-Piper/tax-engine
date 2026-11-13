"""T1 General 2025 (5006-R, Ontario) Step 5 Part B line 98 "Add lines 85, 96, and 97. =", from the
salary alone.

Line 98 is "Add lines 85, 96, and 97." (T1 General 5006-R, CRA 5006-R-25E, confirmed). Line 85 is a
copy of line 84 (`ca/credit_amounts_line_84`),
so it is not a step of its own and line 84 is read directly. Line 96 is
`ca/credits_subtotal_line_96` (the CPP, EI and Canada employment amounts). Line 97 is 0 for the
take-home filer and is left out.
Line 98 is therefore one `core/sum` over line 84 and line 96, rounded half-up to the cent with the
shared `ca/cent_rounding` dataset, and produces `ca/credit_amounts_line_98`, a non-negative kind.

The real parts are composed beside a test-local header: the salary, the real Schedule 8 and T2204
parts, the real T1 taxable-income lines and inputs (line 23600 feeds line 30000), line 30000, line
84, line 31260, line 96 and the part under test. The form declaration of line 98 is test-local: its
one export is line 98.

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
LINE_84 = "ca/credit_amounts_line_84"
LINE_96 = "ca/credits_subtotal_line_96"
LINE_98 = "ca/credit_amounts_line_98"
# The real parts composed beside the test's header: the salary, the real Schedule 8 and T2204
# parts, the real T1 taxable-income lines and inputs, lines 30000, 84, 31260 and 96, and the part
# under test.
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
)
HEADER = dedent("""\
    jurisdiction: CA-ON
    version: 1
    valid_from_tax_year: 2025
    outputs:
      - ca/employment_income
    capabilities: []
    """)
# The T1 tax and credits declaration, test-local: its one export is line 98, the line under test.
T1_TAX_AND_CREDITS = dedent(f"""\
    form:
      name: {FORM}
      required: true
      exports:
        - {LINE_98}
    """)


def _sheet(take_home_service: TakeHomeService, salary: str) -> Worksheet:
    """The tax and credits sheet, with lines 84, 96 and 98 on it."""
    worksheets = take_home_service(HEADER, T1_TAX_AND_CREDITS, *PARTS).compute(
        ONTARIO, 2025, Artifact(EMPLOYMENT_INCOME, D(salary))
    )
    (sheet,) = worksheets[FORM]
    return sheet


@pytest.mark.parametrize(
    ("salary", "expected"),
    [
        # $70,000: 16,129.00 (line 84, the maximum) + 5,840.23 (line 96, 3,291.75 + 1,077.48 +
        # 1,471.00).
        ("70000", "21969.23"),
        # $20,000: 16,129.00 + 2,615.75 (816.75 + 328.00 + 1,471.00).
        ("20000", "18744.75"),
        # $200,000: 15,685.73 (line 84, on the taper) + 5,904.58 (3,356.10 + 1,077.48 + 1,471.00).
        ("200000", "21590.31"),
    ],
)
def test_line_98_is_line_84_plus_line_96(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    sheet = _sheet(take_home_service, salary)
    kinds = bundled_kinds()

    line_98 = sheet.get(kinds.kind(LINE_98)).value
    assert line_98 == D(expected)
    assert line_98 == sheet.get(kinds.kind(LINE_84)).value + sheet.get(kinds.kind(LINE_96)).value
    assert line_98.as_tuple().exponent == -2


def test_line_98_names_lines_84_and_96_and_its_rounding_in_the_trace(
    take_home_service: TakeHomeService,
) -> None:
    sheet = _sheet(take_home_service, "70000")

    assert (
        "Line 84 (CA$16129.00) plus line 96 (CA$5840.23) gives CA$21969.23 "
        "(rounded to the nearest cent)."
    ) in EnglishTraceRenderer().render_all(sheet.trace, sheet)


def test_the_line_98_kind_is_registered_and_non_negative() -> None:
    kind = bundled_kinds().kind(LINE_98)

    assert kind.identifier == LINE_98
    assert non_negative(kind) is True
