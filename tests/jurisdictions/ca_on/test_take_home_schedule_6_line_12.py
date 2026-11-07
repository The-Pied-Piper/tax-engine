"""Schedule 6 (5000-S6, 2025) line 12 "Line 10 minus line 11" (column 1, You).

Form text (5000-S6-25E, docs/cra-forms-2025/5000-s6-25e.txt, lines 215-220): line 11 is "Total of
UCCB (line 11700 of the return) and RDSP income (line 12500 of the return)" and line 12 is "Line 10
minus line 11 (if negative, enter "0")". Line 12 is a `core/subtract_not_below_zero` of line 10
(`ca/cwb_family_net_income_line_10`) less line 11, with a blank line 11 read as 0. Line 11 is an
optional input (`ca/uccb_and_rdsp_income`, part schedule_6_line_11_inputs.yaml) the take-home filer
usually does not have. The output is the registered, non-negative kind
`ca/cwb_family_net_income_line_12`.

Line 10 is composed from the real line 7 and the real T1 lines, as in
test_take_home_schedule_6_line_10.py; the salary is the only required input. The figures for a
salary alone (line 11 blank) are the ticket's table; the UCCB cases are derived from it by
subtracting line 11 from line 10 and flooring at zero (form text above).
"""

from __future__ import annotations

from decimal import Decimal
from textwrap import dedent

import pytest
import yaml

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tests.jurisdictions.ca_on.conftest import TAKE_HOME, TakeHomeService
from tests.kinds import bundled_kinds, non_negative

D = Decimal
ONTARIO = JurisdictionCode("CA-ON")
FORM = "ca/schedule_6"
LINE_12 = "ca/cwb_family_net_income_line_12"
LINE_11 = "ca/uccb_and_rdsp_income"
# The real parts composed beside the test's header: the salary, the real Schedule 8, and the real
# T1 taxable-income lines and inputs, so the T1 net income is read from the salary; then the line 7
# part this line adds up, the line 10 part, the optional line 11 input and the line 12 part itself.
PARTS = (
    "salary.yaml",
    *(part.name for part in sorted(TAKE_HOME.rglob("schedule_8*.yaml"))),
    "t1_taxable_income_inputs.yaml",
    "t1_taxable_income_line_15000.yaml",
    "t1_taxable_income_line_23300.yaml",
    "t1_taxable_income_line_23400.yaml",
    "t1_taxable_income_line_23600.yaml",
    "t1_taxable_income_line_25700_inputs.yaml",
    "t1_taxable_income_line_26000.yaml",
    "t1_taxable_income.yaml",
    "t1_taxable_income_line_10400_inputs.yaml",
    "schedule_6_line_7.yaml",
    "schedule_6_line_10.yaml",
    "schedule_6_line_11_inputs.yaml",
    "schedule_6_line_12.yaml",
)
HEADER = dedent("""\
    jurisdiction: CA-ON
    version: 1
    valid_from_tax_year: 2025
    outputs:
      - ca/employment_income
    capabilities: []
    """)
# The Schedule 6 declaration, test-local: its one export is line 12, the line under test.
SCHEDULE_6 = dedent(f"""\
    form:
      name: {FORM}
      required: true
      exports:
        - {LINE_12}
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
        ("2000", "2000.00"),
        ("6000", "5975.00"),
        ("20000", "19835.00"),
        ("30000", "29735.00"),
        ("35000", "34685.00"),
        ("40000", "39635.00"),
        ("70000", "69335.00"),
    ],
)
def test_line_12_equals_line_10_when_line_11_is_blank(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    sheet = _schedule_6(take_home_service, salary)

    assert sheet.get(bundled_kinds().kind(LINE_12)).value == D(expected)


@pytest.mark.parametrize(
    ("salary", "uccb", "expected"),
    [
        ("20000", "1000.00", "18835.00"),
        ("20000", "0.00", "19835.00"),
        ("20000", "19835.00", "0.00"),
        ("20000", "25000.00", "0.00"),
    ],
)
def test_line_12_subtracts_line_11_and_floors_at_zero(
    take_home_service: TakeHomeService, salary: str, uccb: str, expected: str
) -> None:
    # Line 10 for a 20000 salary is 19835.00; line 12 is line 10 minus line 11, never below zero.
    sheet = _schedule_6(take_home_service, salary, uccb)

    assert sheet.get(bundled_kinds().kind(LINE_12)).value == D(expected)


def test_the_line_12_kind_is_registered_and_non_negative() -> None:
    # Non-negative: line 12 prints 'if negative, enter "0"'.
    kind = bundled_kinds().kind(LINE_12)

    assert kind.identifier == LINE_12
    assert non_negative(kind) is True


def test_the_line_11_input_kind_is_registered_and_non_negative() -> None:
    kind = bundled_kinds().kind(LINE_11)

    assert kind.identifier == LINE_11
    assert non_negative(kind) is True


def test_the_real_schedule_6_header_exports_line_12() -> None:
    # Line 13 (#266) reads line 12, so the real form part must export it.
    form = next(TAKE_HOME.rglob("schedule_6.yaml")).read_text(encoding="utf-8")

    assert LINE_12 in yaml.safe_load(form)["form"]["exports"]
