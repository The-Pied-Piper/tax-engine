"""ON428 (2025) lines 85 and 86, from the salary alone, real engine.

Form text (Form ON428, CRA 5006-c-25e.txt): "Line 85 and line 62140: Low-income
individuals and families tax (LIFT) credit (complete Schedule ON428-A)" and "Line 86: Line 84 minus
line 85 (if negative, enter "0") =". Line 84 is a copy of line 83, so line 86 is one
core/subtract_not_below_zero: line 83 (`ca-on/on428_tax_after_foreign_tax_credit_line_83`) less
line 85. Line 85 is read from Schedule ON428-A Part A line 20 (`ca-on/lift_credit_single`), a
cross-form read through the form's record list (`ca-on/on428_a.lift_credit_single`), so line 85 is
one core/record_total over that list (`ca-on/on428_lift_credit_line_85`). Line 86 is
`ca-on/on428_tax_after_lift_credit_line_86`. The test's own form declaration exports both.

Schedule ON428-A is the real form: its header and real lines 3, 5, 13, 16, 17, 19 and 20, over the
real Schedule 8 and T1 taxable-income parts, so the LIFT credit comes from the salary through the
real lines. Line 83 is built by another part, so this test declares it as a required input of its
header, as the ON428 line tests do.
"""

from __future__ import annotations

from decimal import Decimal
from textwrap import dedent

import pytest

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tests.jurisdictions.ca_on.conftest import TAKE_HOME, TakeHomeService
from tests.kinds import bundled_kinds

D = Decimal
CODE = JurisdictionCode("CA-ON")
LINE_83 = "ca-on/on428_tax_after_foreign_tax_credit_line_83"
LINE_85 = "ca-on/on428_lift_credit_line_85"
LINE_86 = "ca-on/on428_tax_after_lift_credit_line_86"
PARTS = (
    "salary.yaml",
    *(part.name for part in sorted(TAKE_HOME.rglob("schedule_8*.yaml"))),
    *(part.name for part in sorted(TAKE_HOME.rglob("t1_taxable_income*.yaml"))),
    *(part.name for part in sorted(TAKE_HOME.rglob("on428_a*.yaml"))),
    "on428_line_85.yaml",
    "on428_line_86.yaml",
)
HEADER = dedent(f"""\
    jurisdiction: CA-ON
    version: 1
    valid_from_tax_year: 2025
    inputs:
      - name: {LINE_83}
        required: true
    outputs:
      - {LINE_83}
    capabilities: []
    """)
FORM = dedent(f"""\
    form:
      name: ca-on/on428
      required: true
      exports:
        - {LINE_85}
        - {LINE_86}
    capabilities: []
    """)


def _on428(take_home_service: TakeHomeService, salary: str, line_83: str) -> Worksheet:
    kinds = bundled_kinds()
    given = [Artifact(EMPLOYMENT_INCOME, D(salary)), Artifact(kinds.kind(LINE_83), D(line_83))]
    (sheet,) = take_home_service(HEADER, FORM, *PARTS).compute(CODE, 2025, *given)["ca-on/on428"]
    return sheet


def _value(sheet: Worksheet, identifier: str) -> Decimal:
    value = sheet.get(bundled_kinds().kind(identifier)).value
    assert isinstance(value, Decimal)
    return value


# salary, line 83, line 85, line 86. Line 83 is the worked figure for each salary.
CASES = [
    # $20,000: the full 875.00 LIFT credit, above line 83 (12.28), so line 86 is "0".
    ("20000", "12.28", "875.00", "0"),
    # $40,000: line 17 is 7,135.00, the reduction 356.75, so line 85 is 875.00 less 356.75.
    ("40000", "1000.00", "518.25", "481.75"),
    # $70,000: the reduction takes the whole credit, so line 86 is line 83.
    ("70000", "3311.45", "0", "3311.45"),
    # $150,000: the same.
    ("150000", "14102.14", "0", "14102.14"),
]


@pytest.mark.parametrize(("salary", "line_83", "line_85", "line_86"), CASES)
def test_line_85_is_schedule_on428_a_line_20(
    take_home_service: TakeHomeService, salary: str, line_83: str, line_85: str, line_86: str
) -> None:
    assert _value(_on428(take_home_service, salary, line_83), LINE_85) == D(line_85)


@pytest.mark.parametrize(("salary", "line_83", "line_85", "line_86"), CASES)
def test_line_86_is_line_83_minus_line_85_not_below_zero(
    take_home_service: TakeHomeService, salary: str, line_83: str, line_85: str, line_86: str
) -> None:
    assert _value(_on428(take_home_service, salary, line_83), LINE_86) == D(line_86)


def test_line_86_is_0_when_line_85_equals_line_83(take_home_service: TakeHomeService) -> None:
    # At $20,000 line 85 is 875.00; a line 83 of exactly 875.00 leaves a difference of zero.
    assert _value(_on428(take_home_service, "20000", "875.00"), LINE_86) == D("0")
