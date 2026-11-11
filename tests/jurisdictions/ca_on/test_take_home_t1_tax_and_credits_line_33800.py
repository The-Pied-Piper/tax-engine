"""T1 General 2025 (5006-R, Ontario) line 115 / line 33800 "Line 113 multiplied by the percentage
from line 114", from the salary alone.

Line 33800 is "Line 113 multiplied by the percentage from line 114" (T1 General 5006-R, CRA
5006-R-25E, confirmed in docs/cra-forms-2025/5006-r-25e.txt). Line 113 is line 33500
(`ca/non_refundable_credit_amounts`, "Line 106 plus line 112" on that form), and line 114 is the
federal non-refundable tax credit rate of 14.5%, held in the `ca/credit_rate` dataset. Line 33800
is therefore one calculation: 14.5% of line 33500, rounded half-up to the cent with the dataset's
rule, and produces `ca/credit_amounts_at_credit_rate`, a non-negative kind.

The real parts are composed beside a test-local header: the salary, the real Schedule 8 and T2204
parts, the real T1 taxable-income lines and inputs (line 23600 feeds line 30000), line 30000, line
84, line 31260, line 96, line 98, line 101, line 106, line 33500 and the part under test. The form
declaration of line 33800 is test-local: its one export is line 33800.

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
LINE_33500 = "ca/non_refundable_credit_amounts"
LINE_33800 = "ca/credit_amounts_at_credit_rate"
# The real parts composed beside the test's header: the salary, the real Schedule 8 and T2204
# parts, the real T1 taxable-income lines and inputs, lines 30000, 84, 31260, 96, 98, 101, 106 and
# 33500, and the part under test.
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
)
HEADER = dedent("""\
    jurisdiction: CA-ON
    version: 1
    valid_from_tax_year: 2025
    outputs:
      - ca/employment_income
    capabilities: []
    """)
# The T1 tax and credits declaration, test-local: its one export is line 33800, the line under test.
T1_TAX_AND_CREDITS = dedent(f"""\
    form:
      name: {FORM}
      required: true
      exports:
        - {LINE_33800}
    """)

# The direct case: line 33800 fed by line 33500 alone, the input declared in a header of its own,
# and the take-home folder's `t1_tax_and_credits_line_33800.yaml` loaded beside it.
PART = "t1_tax_and_credits_line_33800.yaml"
DIRECT_HEADER = f"""\
jurisdiction: CA-ON
version: 1
valid_from_tax_year: 2025
inputs:
  - name: {LINE_33500}
    required: true
outputs:
  - {LINE_33500}
capabilities: []
"""

DIRECT_FORM = f"""\
form:
  name: {FORM}
  required: true
  exports:
    - {LINE_33800}
capabilities: []
"""


def _sheet(take_home_service: TakeHomeService, salary: str) -> Worksheet:
    """The tax and credits sheet, with lines 33500 and 33800 on it."""
    worksheets = take_home_service(HEADER, T1_TAX_AND_CREDITS, *PARTS).compute(
        ONTARIO, 2025, Artifact(EMPLOYMENT_INCOME, D(salary))
    )
    (sheet,) = worksheets[FORM]
    return sheet


def _line_33800(take_home_service: TakeHomeService, line_33500: str) -> Decimal:
    kinds = bundled_kinds()
    worksheet = take_home_service(DIRECT_HEADER, DIRECT_FORM, PART).compute(
        ONTARIO,
        2025,
        Artifact(kinds.kind(LINE_33500), D(line_33500)),
    )[FORM][0]
    value = worksheet.get(kinds.kind(LINE_33800)).value
    assert isinstance(value, Decimal)
    return value


@pytest.mark.parametrize(
    ("salary", "expected"),
    [
        # $70,000: line 33500 is 21,969.23, and 14.5% of it is 3,185.53835, rounded to 3,185.54.
        ("70000", "3185.54"),
        # $20,000: line 33500 is 18,744.75, and 14.5% of it is 2,717.98875, rounded to 2,717.99.
        ("20000", "2717.99"),
        # $200,000: line 33500 is 21,590.31, and 14.5% of it is 3,130.59495, rounded to 3,130.59.
        ("200000", "3130.59"),
    ],
)
def test_line_33800_is_14_5_percent_of_line_33500(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    sheet = _sheet(take_home_service, salary)
    kinds = bundled_kinds()

    line_33800 = sheet.get(kinds.kind(LINE_33800)).value
    assert line_33800 == D(expected)
    assert line_33800.as_tuple().exponent == -2


@pytest.mark.parametrize(
    ("line_33500", "line_33800"),
    [
        # 20,000.00 x 14.5% = 2,900.000, exactly.
        ("20000.00", "2900.00"),
        # 1.00 x 14.5% = 0.145, a tie at the half-cent: rounded half-up to 0.15, not half-even 0.14.
        ("1.00", "0.15"),
        # 5.00 x 14.5% = 0.725, a tie at the half-cent: rounded half-up to 0.73, not half-even 0.72.
        ("5.00", "0.73"),
        # 1.01 x 14.5% = 0.14645, rounded to the nearest cent, 0.15.
        ("1.01", "0.15"),
        # 0.10 x 14.5% = 0.0145, rounded to the nearest cent, 0.01 (not a tie: 1.45 cents).
        ("0.10", "0.01"),
        # Line 33500 is 0, so line 33800 is 0.
        ("0", "0.00"),
    ],
)
def test_line_33800_rounds_half_up_to_the_cent(
    take_home_service: TakeHomeService, line_33500: str, line_33800: str
) -> None:
    assert _line_33800(take_home_service, line_33500) == D(line_33800)


def test_line_33800_names_line_33500_the_rate_and_its_rounding_in_the_trace(
    take_home_service: TakeHomeService,
) -> None:
    sheet = _sheet(take_home_service, "70000")

    assert (
        "14.5% of line 33500 (21969.23), rounded to the nearest cent."
    ) in EnglishTraceRenderer().render_all(sheet.trace, sheet)


def test_the_line_33800_kind_is_registered_and_non_negative() -> None:
    kind = bundled_kinds().kind(LINE_33800)

    assert kind.identifier == LINE_33800
    assert non_negative(kind) is True
