"""Schedule 6 (5000-S6, 2025) line 10 "Add lines 7 to 9." (column 1, You), from the salary alone.

Line 10 is "Add lines 7 to 9." (Schedule 6, CRA 5000-S6-25E, confirmed in
docs/cra-forms-2025/5000-s6-25e.txt, lines 211-213, column 1 "You"). The take-home filer has only
line 7 of the three lines (lines 8 and 9 are left out), so line 10 is a `core/sum` over the one
part `ca/cwb_net_income_line_7`, the line 7 amount of this form, and its output is the registered
kind `ca/cwb_family_net_income_line_10`. The form text of line 10 has no floor at zero, so the
result is a signed amount.

Line 7 is composed beside line 10 as its part, and it is computed from the real T1 lines the same
way as in test_take_home_schedule_6_line_7.py: the salary is the only input the caller gives, and
the T1 net income comes from the salary through the real lines.

Line 10 is pinned as a figure for each salary, and its kind is pinned as registered and signed. A
negative net income cannot be made from a salary alone (deductions never exceed the salary), so the
negative branch is not tested here.
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
LINE_10 = "ca/cwb_family_net_income_line_10"
# The real parts composed beside the test's header: the salary, the real Schedule 8, and the real
# T1 taxable-income lines and inputs, so the T1 net income is read from the salary; then the line 7
# part this line adds up, and the line 10 part itself.
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
    "schedule_6_line_10.yaml",
)
HEADER = dedent("""\
    jurisdiction: CA-ON
    version: 1
    valid_from_tax_year: 2025
    outputs:
      - ca/employment_income
    capabilities: []
    """)
# The Schedule 6 declaration, test-local: its one export is line 10, the only line of the sum
# composed here.
SCHEDULE_6 = dedent(f"""\
    form:
      name: {FORM}
      required: true
      exports:
        - {LINE_10}
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
        ("2000", "2000.00"),
        ("6000", "5975.00"),
        ("20000", "19835.00"),
        ("30000", "29735.00"),
        ("35000", "34685.00"),
        ("40000", "39635.00"),
        ("70000", "69335.00"),
    ],
)
def test_line_10_is_the_sum_of_line_7(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    sheet = _schedule_6(take_home_service, salary)

    assert sheet.get(bundled_kinds().kind(LINE_10)).value == D(expected)


def test_the_line_10_kind_is_registered_and_signed() -> None:
    # Signed: line 10 "Add lines 7 to 9." prints no floor at zero, so the kind may be negative.
    kind = bundled_kinds().kind(LINE_10)

    assert kind.identifier == LINE_10
    assert non_negative(kind) is False
