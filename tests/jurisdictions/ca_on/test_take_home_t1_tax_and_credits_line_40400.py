"""T1 General 2025 (5006-R, Ontario) Step 5 Part C line 121 (line 40400) "Federal tax with the tax
on split income", from the salary alone.

Line 121 is "Line 119 plus line 120" (T1 General 5006-R, CRA 5006-R-25E, confirmed in
docs/cra-forms-2025/5006-r-25e.txt). Line 119 is "Enter the amount from line 76", a pure copy of
line 76 (`ca/federal_tax_on_taxable_income_line_76`, read directly because it is the same form), so
it is no step.
Line 120 is the federal tax on split income (TOSI), 0 for the take-home filer (salary the only
income), so it is left out. Line 121 is therefore one `core/sum` over line 76 alone, rounded half-up
to the cent with the shared `ca/cent_rounding` dataset, and produces
`ca/federal_tax_with_split_income`, a non-negative kind.

The T1 side is the real `ca/t1_taxable_income` form (its header part and the real lines 15000,
23300 read from the real Schedule 8, 23400, 23600, 23600 signed, 26000 and the optional inputs
parts), and line 76 is the real part, so line 76 comes from the salary through the real lines. The
form header of line 121 is test-local: it declares `ca/federal_tax_with_split_income` as its one
export.

The salary is the only input the caller gives. Ontario resident, single filer, salary the only
income, tax withheld 0, basic credits only, as the take-home calculator states them.

Line 121 is pinned as a figure for each salary and equal to line 76, and at the two salaries either
side of the 57,375 column boundary of line 76 (57,919 and 57,920), where it is line 76 plus 0.
The trace names the line 76 amount, the rounding and the total, and the kind is pinned as
registered and non-negative.
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
LINE_76 = "ca/federal_tax_on_taxable_income_line_76"
LINE_121 = "ca/federal_tax_with_split_income"
# The real parts composed beside the test's header: the salary, the real Schedule 8, the real T1
# taxable-income lines and inputs, line 76 and line 121.
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
    "t1_tax_and_credits_line_76.yaml",
    "t1_tax_and_credits_line_40400.yaml",
)
HEADER = dedent("""\
    jurisdiction: CA-ON
    version: 1
    valid_from_tax_year: 2025
    outputs:
      - ca/employment_income
    capabilities: []
    """)
# The T1 tax and credits declaration, test-local: its one export is line 121, the line under test.
T1_TAX_AND_CREDITS = dedent(f"""\
    form:
      name: {FORM}
      required: true
      exports:
        - {LINE_121}
    """)


def _sheet(take_home_service: TakeHomeService, salary: str) -> Worksheet:
    """The tax and credits sheet, with line 76 and line 121 on it."""
    worksheets = take_home_service(HEADER, T1_TAX_AND_CREDITS, *PARTS).compute(
        ONTARIO, 2025, Artifact(EMPLOYMENT_INCOME, D(salary))
    )
    (sheet,) = worksheets[FORM]
    return sheet


@pytest.mark.parametrize(
    ("salary", "expected"),
    [
        # Column 1 of line 76: 14.5% of 19,835.00, 2,876.075 rounded half-up.
        ("20000", "2876.08"),
        # Column 2 of line 76: 8,319.38 plus 20.5% of 11,960.00 above 57,375.00.
        ("70000", "10771.18"),
        # Column 4 of line 76: 36,495.57 plus 29% of 21,044.00 above 177,882.00.
        ("200000", "42598.33"),
    ],
)
def test_line_121_is_line_76_with_no_tax_on_split_income(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    sheet = _sheet(take_home_service, salary)
    kinds = bundled_kinds()

    line_121 = sheet.get(kinds.kind(LINE_121)).value
    assert line_121 == D(expected)
    assert line_121 == sheet.get(kinds.kind(LINE_76)).value + D("0")
    assert line_121.as_tuple().exponent == -2


@pytest.mark.parametrize(
    ("salary", "expected"),
    [
        # Line 26000 of 57,374.81 is in column 1 of line 76: 8,319.35.
        ("57919", "8319.35"),
        # Line 26000 of 57,375.80 is in column 2 of line 76: 8,319.54.
        ("57920", "8319.54"),
    ],
)
def test_line_121_is_line_76_plus_0_at_the_57375_column_boundary(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    sheet = _sheet(take_home_service, salary)
    kinds = bundled_kinds()

    assert sheet.get(kinds.kind(LINE_76)).value == D(expected)
    assert sheet.get(kinds.kind(LINE_121)).value == D(expected)


def test_line_121_names_line_76_and_its_rounding_in_the_trace(
    take_home_service: TakeHomeService,
) -> None:
    sheet = _sheet(take_home_service, "70000")
    kinds = bundled_kinds()
    output = kinds.kind(LINE_121)
    part = kinds.kind(LINE_76)

    assert (
        f"{output.label}: {part.label} 10771.18 = 10771.18 (half-up to 0.01)"
    ) in EnglishTraceRenderer().render_all(sheet.trace)


def test_the_line_121_kind_is_registered_and_non_negative() -> None:
    kind = bundled_kinds().kind(LINE_121)

    assert kind.identifier == LINE_121
    assert non_negative(kind) is True
