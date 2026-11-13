"""Schedule 6 (5000-S6, 2025) line 13, family net income, as the Ontario take-home manifest parts
wire it.

Form text (5000-S6 2025): "Line 13: Add the
amounts from line 12 in columns 1 and 2. If you had an eligible spouse, continue at line 14; if
not, continue at line 15." Line 13 is a calculation: the sum of line 12 over the columns. The
take-home calculator is single with no eligible spouse, so column 2 is left out and the sum has one
part: line 12 column 1 (`ca/cwb_net_income_less_uccb_rdsp_line_12`, from
schedule_6_line_12.yaml). Line 13 is therefore one core/sum over line 12 column 1 alone.

Line 12 is composed from the real parts, as in test_take_home_schedule_6_line_12.py: the salary is
the only required input, and line 11 (`ca/uccb_and_rdsp_income`) is optional. The output is the
registered, non-negative kind `ca/cwb_family_net_income_line_13`.

The manifest parts are loaded from the package. The header and the form's export are made up here,
because the shared scaffold owns them.
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
LINE_13 = "ca/cwb_family_net_income_line_13"
LINE_11 = "ca/uccb_and_rdsp_income"
# The real parts composed beside the test's header: the salary, the real Schedule 8, and the real
# T1 taxable-income lines and inputs, so the T1 net income is read from the salary; then the line 7
# part, the line 10 part, the optional line 11 input and the line 12 part this line adds up, and
# the line 13 part itself.
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
    "schedule_6_line_11_inputs.yaml",
    "schedule_6_line_12.yaml",
    "schedule_6_line_13.yaml",
)
HEADER = dedent("""\
    jurisdiction: CA-ON
    version: 1
    valid_from_tax_year: 2025
    outputs:
      - ca/employment_income
    capabilities: []
    """)
# The Schedule 6 declaration, test-local: its one export is line 13, the line under test.
SCHEDULE_6 = dedent(f"""\
    form:
      name: {FORM}
      required: true
      exports:
        - {LINE_13}
    """)


def _schedule_6(
    take_home_service: TakeHomeService, salary: str, uccb: str | None = None
) -> Worksheet:
    kinds = bundled_kinds()
    starting = [Artifact(EMPLOYMENT_INCOME, D(salary))]
    if uccb is not None:
        starting.append(Artifact(kinds.kind(LINE_11), D(uccb)))
    worksheets = take_home_service(HEADER, SCHEDULE_6, *PARTS).compute(ONTARIO, 2025, *starting)
    (sheet,) = worksheets[FORM]
    return sheet


@pytest.mark.parametrize(
    ("salary", "expected"),
    [
        # Family net income (line 13) at salaries of $2,000, $6,000, $20,000, $30,000, $35,000,
        # $40,000 and $70,000 with line 11 blank. Column 2 is left out, so each line 13 is line 12
        # column 1 alone, which is the line 12 figure for that salary.
        ("2000", "2000.00"),
        ("6000", "5975.00"),
        ("20000", "19835.00"),
        ("30000", "29735.00"),
        ("35000", "34685.00"),
        ("40000", "39635.00"),
        ("70000", "69335.00"),
    ],
)
def test_schedule_6_line_13_is_line_12_column_1_alone(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    sheet = _schedule_6(take_home_service, salary)

    value = sheet.get(bundled_kinds().kind(LINE_13)).value
    assert value == D(expected)
    assert value.as_tuple().exponent == -2


@pytest.mark.parametrize(
    ("salary", "uccb", "expected"),
    [
        # Line 12 for a 20000 salary is line 10 (19835.00) less line 11, not below zero; line 13 is
        # that line 12 alone.
        ("20000", "1000.00", "18835.00"),
        ("20000", "25000.00", "0.00"),
    ],
)
def test_schedule_6_line_13_follows_line_12_when_line_11_is_given(
    take_home_service: TakeHomeService, salary: str, uccb: str, expected: str
) -> None:
    sheet = _schedule_6(take_home_service, salary, uccb)

    value = sheet.get(bundled_kinds().kind(LINE_13)).value
    assert value == D(expected)
    assert value.as_tuple().exponent == -2


def test_the_line_13_kind_is_registered_and_non_negative() -> None:
    # Non-negative: line 13 sums non-negative line 12 amounts, and the form prints no negative
    # result for it.
    kind = bundled_kinds().kind(LINE_13)

    assert kind.identifier == LINE_13
    assert non_negative(kind) is True
