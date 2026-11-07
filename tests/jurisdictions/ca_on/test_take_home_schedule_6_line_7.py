"""Schedule 6 (5000-S6, 2025) line 7 "Net income" (column 1, You), from the salary alone.

Line 7 is "Net income from line 23600 of the return (or the amount you would have entered if the
instructions on line 23600 said "if negative, show in brackets")" (Schedule 6, CRA 5000-S6-25E,
confirmed in docs/cra-forms-2025/5000-s6-25e.txt, lines 193-197, column 1 "You"). The take-home
filer has only that one line of the column, so line 7 is a `core/record_total` over the T1 net
income record list `ca/t1_taxable_income.net_income_signed`: the engine lets one form read another
form's exports only as record lists, and T1 line 23600 is exported before its floor as
`ca/net_income_signed`. The result is a signed amount, because the form prints a negative net
income in brackets and does not floor it at zero.

The T1 side is the real `ca/t1_taxable_income` form: its header part and the real lines 15000,
23300 (deductions, read from the real Schedule 8), 23400, 23600, 23600 signed, 26000 and the
optional inputs parts, so net income comes from the salary through the real lines. Line 7 reads the
signed T1 net income, `ca/net_income_signed`, which is the amount before the floor of line 23600.

The salary is the only input the caller gives. Single, no eligible spouse or dependant, and the
other eligibility answers of Schedule 6 are assumed as the take-home calculator states them; they
do not change line 7 and are not tested here.

Line 7 is pinned as a figure for each salary, and its kind is pinned as registered and signed. A
negative net income cannot be made from a salary alone (deductions never exceed the salary), so the
brackets branch is tested separately: line 23500 (social benefits repayment) is given above line
23400, so the difference is negative, and line 7 is then that negative net income, in brackets
on the form, not "0".
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
from tests.kinds import bundled_kinds, non_negative

D = Decimal
ONTARIO = JurisdictionCode("CA-ON")
FORM = "ca/schedule_6"
LINE_7 = "ca/cwb_net_income_line_7"
# The real parts composed beside the test's header: the salary, the real Schedule 8, and the real
# T1 taxable-income lines and inputs, so the T1 net income is read from the salary.
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
    "schedule_6_line_7.yaml",
)
HEADER = dedent("""\
    jurisdiction: CA-ON
    version: 1
    valid_from_tax_year: 2025
    outputs:
      - ca/employment_income
    capabilities: []
    """)
# The Schedule 6 declaration, test-local: its one export is line 7, the only line composed here.
SCHEDULE_6 = dedent(f"""\
    form:
      name: {FORM}
      required: true
      exports:
        - {LINE_7}
    """)


def _schedule_6(take_home_service: TakeHomeService, salary: str) -> Worksheet:
    worksheets = take_home_service(HEADER, SCHEDULE_6, *PARTS).compute(
        ONTARIO, 2025, Artifact(EMPLOYMENT_INCOME, D(salary))
    )
    (sheet,) = worksheets[FORM]
    return sheet


@pytest.mark.parametrize(
    ("salary", "expected"),
    [
        # Under the 3,500 floor of the CPP enhancement: T1 line 22215 is 0.00, so line 7 is 2,000.
        ("2000", "2000.00"),
        # T1 line 22215 is 25.00, 165.00, 265.00, 315.00, 365.00 and 665.00 for these salaries.
        ("6000", "5975.00"),
        ("20000", "19835.00"),
        ("30000", "29735.00"),
        ("35000", "34685.00"),
        ("40000", "39635.00"),
        ("70000", "69335.00"),
    ],
)
def test_line_7_is_the_t1_net_income(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    sheet = _schedule_6(take_home_service, salary)

    assert sheet.get(bundled_kinds().kind(LINE_7)).value == D(expected)


def test_line_7_is_the_negative_net_income_in_brackets_not_floored(
    take_home_service: TakeHomeService,
) -> None:
    # Line 23500 of 75,000 is more than line 23400 of 69,335.00, so net income is -5,665.00. Line 7
    # keeps it as it is ("show in brackets"), where the floored line 23600 would read "0".
    kinds = bundled_kinds()
    worksheets = take_home_service(HEADER, SCHEDULE_6, *PARTS).compute(
        ONTARIO,
        2025,
        Artifact(EMPLOYMENT_INCOME, D("70000")),
        Artifact(kinds.kind("ca/social_benefits_repayment"), D("75000")),
    )
    (sheet,) = worksheets[FORM]

    assert sheet.get(kinds.kind(LINE_7)).value == D("-5665.00")


def test_the_line_7_kind_is_registered_and_signed() -> None:
    # Signed: the form prints a negative net income in brackets, so the kind may not be negative.
    kind = bundled_kinds().kind(LINE_7)

    assert kind.identifier == LINE_7
    assert non_negative(kind) is False
