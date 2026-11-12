"""ON428-A (Ontario LIFT credit, 2025) lines 6 and 13, from the salary alone, real engine.

Line 13 is "Line 9 minus line 12 (if negative, enter "0") Your adjusted net income" (ON428-A, CRA
5006-A-25E, confirmed in docs/cra-forms-2025/5006-a-25e.txt). Line 9 adds lines 6 to 8, and the
take-home filer has only line 6: T1 line 23600, net income. The T1 form exports the net income
before its floor as `ca/net_income_signed`, which reaches this form only as the record list
`ca/t1_taxable_income.net_income_signed`.
Line 6, "Net income from line 23600 of your return (or the amount you would have entered if the
instructions on line 23600 said "if negative, show in brackets")", is therefore a
`core/record_total` over that list. Line 13 is a `core/sum_not_below_zero` over the one part,
line 6, because a sum line is built even with one part. Lines 7, 8, 10, 11 and 12 are not built:
the take-home filer has none of them.

The T1 side is the real `ca/t1_taxable_income` form: its header part and the real lines 15000,
23300 (deductions, read from the real Schedule 8), 23400, 23600, 23600 signed, 26000 and the
optional inputs parts, so net income comes from the salary through the real lines. The engine does
not let one form read another form's plain amounts, only its exports as record lists, which is why
line 6 reads `ca/t1_taxable_income.net_income_signed`: the T1 net income before the floor of line
23600, as line 6 prints it ("if negative, show in brackets"). Line 13 then floors the sum at "0".

ON428-A lines 16 and 17 are composed with line 13, because the form's export is line 17, the
first line that reads line 13; its declaration here exports only that.

The salary is the only input the caller gives. Ontario's eligibility for the LIFT credit is not
printed on the form ("go to canada.ca/on-tax-info"), so it is assumed true and not tested here.

Line 6 and line 13 are each pinned as a figure. A negative net income cannot be made from a salary
alone (deductions never exceed the salary), so the negative branch is tested separately: T1 line
23500 (social benefits repayment) is given above line 23400, so line 6 is the negative net income,
in brackets, and line 13 is "0".
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
from tests.kinds import bundled_kinds

D = Decimal
ONTARIO = JurisdictionCode("CA-ON")
FORM = "ca-on/on428_a"
LINE_6 = "ca-on/lift_net_income"
LINE_13 = "ca-on/lift_adjusted_net_income"
# The real parts composed beside the test's header: the salary, the real Schedule 8, the real T1
# taxable-income lines and inputs, and ON428-A lines 13, 16 and 17.
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
    "on428_a_line_13.yaml",
    "on428_a_line_16.yaml",
    "on428_a_line_17.yaml",
)
HEADER = dedent("""\
    jurisdiction: CA-ON
    version: 1
    valid_from_tax_year: 2025
    outputs:
      - ca/employment_income
    capabilities: []
    """)
# The ON428-A declaration, test-local: lines 13, 16 and 17 are composed, so its one export is line
# 17, which reads line 13. The real header exports lines whose parts are not composed here.
ON428_A = dedent("""\
    form:
      name: ca-on/on428_a
      required: true
      exports:
        - ca-on/lift_single_excess_over_threshold
    """)


def _on428_a(take_home_service: TakeHomeService, salary: str) -> Worksheet:
    worksheets = take_home_service(HEADER, ON428_A, *PARTS).compute(
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


def test_a_negative_net_income_is_line_6_in_brackets_and_line_13_is_zero(
    take_home_service: TakeHomeService,
) -> None:
    # Line 23500 of 75,000 is more than line 23400 of 69,335.00, so net income is -5,665.00. Line 6
    # keeps it as it is, in brackets on the form; line 13 is "Line 9 minus line 12 (if negative,
    # enter "0")", so it is 0.
    kinds = bundled_kinds()
    worksheets = take_home_service(HEADER, ON428_A, *PARTS).compute(
        ONTARIO,
        2025,
        Artifact(EMPLOYMENT_INCOME, D("70000")),
        Artifact(kinds.kind("ca/social_benefits_repayment"), D("75000")),
    )
    (sheet,) = worksheets[FORM]

    assert sheet.get(kinds.kind(LINE_6)).value == D("-5665.00")
    line_13 = sheet.get(kinds.kind(LINE_13)).value
    assert line_13 == D("0.00")
    # The floored zero is the cent zero of the rounding dataset, not a bare 0.
    assert str(line_13) == "0.00"
    assert line_13.as_tuple().exponent == -2
    assert not line_13.is_signed()
    assert (
        "Line 6 (-CA$5665.00), not below 0, gives CA$0.00 (rounded to the nearest cent)."
    ) in EnglishTraceRenderer().render_all(sheet.trace, sheet)


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


def test_line_13_prints_cents_and_names_its_rounding_in_the_trace(
    take_home_service: TakeHomeService,
) -> None:
    sheet = _on428_a(take_home_service, "70000")

    value = sheet.get(bundled_kinds().kind(LINE_13)).value
    assert str(value) == "69335.00"
    assert value.as_tuple().exponent == -2
    assert (
        "Line 6 (CA$69335.00), not below 0, gives CA$69335.00 (rounded to the nearest cent)."
    ) in EnglishTraceRenderer().render_all(sheet.trace, sheet)
