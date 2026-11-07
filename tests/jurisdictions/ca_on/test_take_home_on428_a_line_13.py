"""ON428-A (Ontario LIFT credit, 2025) lines 6 and 13, from the salary alone, real engine.

Line 13 is "Line 9 minus line 12 (if negative, enter "0") Your adjusted net income" (ON428-A, CRA
5006-A-25E, confirmed in docs/cra-forms-2025/5006-a-25e.txt). Line 9 adds lines 6 to 8, and the
take-home filer has only line 6: T1 line 23600, net income. The T1 form exports net income as
`ca/net_income`, which reaches this form only as the record list `ca/t1_taxable_income.net_income`.
Line 6, "Net income from line 23600 of your return (or the amount you would have entered if the
instructions on line 23600 said "if negative, show in brackets")", is therefore a
`core/record_total` over that list. Line 13 is a `core/sum_not_below_zero` over the one part,
line 6, because a sum line is built even with one part. Lines 7, 8, 10, 11 and 12 are not built:
the take-home filer has none of them.

The T1 side is a test-local declaration of `ca/t1_taxable_income` exporting `ca/net_income`. Its
real line 15000 (total income) and line 23300 (deductions, read from the real Schedule 8) are
composed in, but the real line 23600 is not: it needs net income before adjustments (line 23400),
which is not built yet. The declaration's one step stands in for
lines 23400 and 23600 together: total income less deductions from total income, not below zero.
The engine does not let one form read another form's plain amounts, only its exports as record
lists, so the stand-in must sit in the T1 form itself, which is why it is declared here.

The salary is the only input the caller gives. Ontario's eligibility for the LIFT credit is not
printed on the form ("go to canada.ca/on-tax-info"), so it is assumed true and not tested here.

Line 6 and line 13 are each pinned as a figure. A negative net income cannot be made from a salary
alone (deductions never exceed the salary, and the stand-in is floored at zero), so the "0" branch
of line 13 is not tested here.
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
ONTARIO = JurisdictionCode("CA-ON")
FORM = "ca-on/on428_a"
LINE_6 = "ca-on/lift_net_income"
LINE_13 = "ca-on/lift_adjusted_net_income"
# The real parts composed beside the test's declarations: the salary, the real Schedule 8 (line
# 22215 and its export read by T1 line 23300), T1 lines 15000 and 23300, and the real ON428-A form
# declaration and line 13 part.
PARTS = (
    "salary.yaml",
    *(part.name for part in sorted(TAKE_HOME.rglob("schedule_8*.yaml"))),
    "t1_taxable_income_line_15000.yaml",
    "t1_taxable_income_line_23300.yaml",
    "on428_a.yaml",
    "on428_a_line_13.yaml",
)
HEADER = dedent("""\
    jurisdiction: CA-ON
    version: 1
    valid_from_tax_year: 2025
    inputs:
      - name: ca/other_employment_income
        required: false
        default: "0"
        basis: 'Other employment income (T1 line 10400)'
    outputs:
      - ca/employment_income
    capabilities: []
    """)
# The T1 declaration, test-local: its one export is net income. Its one step stands in for lines
# 23400 and 23600 (not built yet): total income less deductions from total income, not below zero.
T1 = dedent("""\
    form:
      name: ca/t1_taxable_income
      required: true
      exports:
        - ca/net_income
    capabilities:
      - name: core/subtract_not_below_zero
        consumes:
          amount: ca/total_income
          less: ca/deductions_from_total_income
        produces:
          output: ca/net_income
    """)


def _on428_a(take_home_service: TakeHomeService, salary: str) -> Worksheet:
    worksheets = take_home_service(HEADER, T1, *PARTS).compute(
        ONTARIO, 2025, Artifact(EMPLOYMENT_INCOME, D(salary))
    )
    (sheet,) = worksheets[FORM]
    return sheet


@pytest.mark.parametrize(
    ("salary", "expected"),
    [
        # The $70,000 salary: T1 line 23600 is 69,335.00, so line 6 is that figure.
        ("70000", "69335.00"),
        # The $30,000 salary, under the 32,500 threshold: T1 line 23600 is 29,735.00.
        ("30000", "29735.00"),
    ],
)
def test_line_6_is_the_t1_net_income(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    sheet = _on428_a(take_home_service, salary)
    assert sheet.get(bundled_kinds().kind(LINE_6)).value == D(expected)


@pytest.mark.parametrize(
    ("salary", "expected"),
    [
        # The $70,000 salary: line 13 is line 6, which is not below zero.
        ("70000", "69335.00"),
        # The $30,000 salary: line 13 is line 6.
        ("30000", "29735.00"),
    ],
)
def test_line_13_is_line_6_not_below_zero(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    sheet = _on428_a(take_home_service, salary)
    assert sheet.get(bundled_kinds().kind(LINE_13)).value == D(expected)
