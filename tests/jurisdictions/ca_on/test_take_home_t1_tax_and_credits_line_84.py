"""T1 General 2025 (5006-R, Ontario) Step 5 Part B line 84 "Add lines 77 to 83. =", from the salary
alone.

Line 84 is "Add lines 77 to 83." (T1 General 5006-R, CRA 5006-R-25E, confirmed in
docs/cra-forms-2025/5006-r-25e.txt). Line 77 is the basic personal amount, line 30000
(`ca/basic_personal_amount`), read directly as a real part. Lines 78 to 83 are 0 for the
take-home filer (salary the only income, single, basic credits only), so they are left out.
Line 84 is therefore one `core/sum` over line 77 alone, rounded half-up to the cent with the
shared `ca/cent_rounding` dataset, and produces
`ca/credit_amounts_line_84`, a non-negative kind.

The T1 side is the real `ca/t1_taxable_income` form (its header part and the real lines 15000,
23300 read from the real Schedule 8, 23400, 23600, 23600 signed, 26000 and the optional inputs
parts), and line 30000 is the real part, so line 23600 comes from the salary through the real lines.
The form header of line 84 is test-local: it declares `ca/credit_amounts_line_84` as its one export.

The salary is the only input the caller gives. Ontario resident, single filer, salary the only
income, tax withheld 0, basic credits only, as the take-home calculator states them.

Line 84 is pinned as a figure for each salary and equal to line 30000 (the basic personal amount),
at a salary whose line 23600 is below the threshold, at a salary inside the taper, and at salaries
either side of the threshold. The trace names the line 30000 amount, the rounding and the
total, and the kind is pinned as registered and non-negative.
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
LINE_30000 = "ca/basic_personal_amount"
LINE_84 = "ca/credit_amounts_line_84"
# The real parts composed beside the test's header: the salary, the real Schedule 8, the real T1
# taxable-income lines and inputs, line 30000 and line 84.
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
    "t1_tax_and_credits_line_84.yaml",
)
HEADER = dedent("""\
    jurisdiction: CA-ON
    version: 1
    valid_from_tax_year: 2025
    outputs:
      - ca/employment_income
    capabilities: []
    """)
# The T1 tax and credits declaration, test-local: its one export is line 84, the line under test.
T1_TAX_AND_CREDITS = dedent(f"""\
    form:
      name: {FORM}
      required: true
      exports:
        - {LINE_84}
    """)


def _sheet(take_home_service: TakeHomeService, salary: str) -> Worksheet:
    """The tax and credits sheet, with line 30000 and line 84 on it."""
    worksheets = take_home_service(HEADER, T1_TAX_AND_CREDITS, *PARTS).compute(
        ONTARIO, 2025, Artifact(EMPLOYMENT_INCOME, D(salary))
    )
    (sheet,) = worksheets[FORM]
    return sheet


@pytest.mark.parametrize(
    ("salary", "expected"),
    [
        # Line 23600 below the threshold: the maximum, 16,129.00.
        ("20000", "16129.00"),
        # Line 23600 of 69,335.00 is below the threshold: the maximum, 16,129.00.
        ("70000", "16129.00"),
        # Line 23600 of 198,926.00 is on the taper: 15,685.73.
        ("200000", "15685.73"),
    ],
)
def test_line_84_is_line_30000_with_no_other_credit_amounts(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    sheet = _sheet(take_home_service, salary)
    kinds = bundled_kinds()

    line_84 = sheet.get(kinds.kind(LINE_84)).value
    assert line_84 == D(expected)
    assert line_84 == sheet.get(kinds.kind(LINE_30000)).value
    assert line_84.as_tuple().exponent == -2


@pytest.mark.parametrize(
    ("salary", "expected"),
    [
        # Line 23600 of 177,883.00, one dollar over the threshold: 16,128.98.
        ("178957", "16128.98"),
        # Line 23600 of 253,413.00, one dollar under the top of the taper: 14,538.02.
        ("254487", "14538.02"),
        # Line 23600 of 253,414.00 or more: the base, 14,538.00.
        ("254488", "14538.00"),
    ],
)
def test_line_84_is_line_30000_at_the_taper_boundaries(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    sheet = _sheet(take_home_service, salary)
    kinds = bundled_kinds()

    assert sheet.get(kinds.kind(LINE_84)).value == D(expected)
    assert sheet.get(kinds.kind(LINE_84)).value == sheet.get(kinds.kind(LINE_30000)).value


def test_line_84_names_line_30000_and_its_rounding_in_the_trace(
    take_home_service: TakeHomeService,
) -> None:
    sheet = _sheet(take_home_service, "70000")
    kinds = bundled_kinds()
    output = kinds.kind(LINE_84)
    part = kinds.kind(LINE_30000)

    assert (
        f"{output.label}: {part.label} 16129.00 = 16129.00 (half-up to 0.01)"
    ) in EnglishTraceRenderer().render_all(sheet.trace)


def test_the_line_84_kind_is_registered_and_non_negative() -> None:
    kind = bundled_kinds().kind(LINE_84)

    assert kind.identifier == LINE_84
    assert non_negative(kind) is True
