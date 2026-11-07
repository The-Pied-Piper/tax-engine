"""Schedule 6 (5000-S6, 2025) line 15, adjusted family net income, as the Ontario take-home manifest
parts wire it.

Form text (5000-S6 2025, docs/cra-forms-2025/5000-s6-25e.txt, lines 235-236): "Line 15: Line 13
minus line 14 Enter this amount on line 23 and line 35. Adjusted family net income" is a
subtraction: line 13 (`ca/cwb_family_net_income_line_13`, from schedule_6_line_13.yaml) less line
14 (`ca/cwb_secondary_earner_exemption`, the optional input of schedule_6_line_14_inputs.yaml). The
take-home filer is single, with no eligible spouse, so line 14 is left out by default and read as
blank, and the line 15 part reads that blank as 0: line 15 is then line 13 alone.

The form prints no floor on line 15, so a line 14 larger than line 13 gives a negative result. The
output is the registered kind `ca/adjusted_family_net_income`, which is signed.

Line 13 is composed from the real parts, as in test_take_home_schedule_6_line_13.py: the salary is
the only required input. The manifest parts are loaded from the package. The header and the form's
export are made up here, because the shared scaffold owns them.
"""

from __future__ import annotations

from decimal import Decimal
from textwrap import dedent

import pytest

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tax_engine.domain.trace import SubtractedLine
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tests.jurisdictions.ca_on.conftest import TAKE_HOME, TakeHomeService
from tests.kinds import bundled_kinds, non_negative

D = Decimal
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)
ONTARIO = JurisdictionCode("CA-ON")
FORM = "ca/schedule_6"
LINE_15 = "ca/adjusted_family_net_income"
LINE_14 = "ca/cwb_secondary_earner_exemption"
# The real parts composed beside the test's header: the salary, the real Schedule 8, and the real
# T1 taxable-income lines and inputs, so the T1 net income is read from the salary; then the line 7
# part, the line 10 part, the optional line 11 input, the line 12 part, the line 13 part this line
# subtracts from, the optional line 14 input and the line 15 part itself.
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
    "schedule_6_line_14_inputs.yaml",
    "schedule_6_line_15.yaml",
)
HEADER = dedent("""\
    jurisdiction: CA-ON
    version: 1
    valid_from_tax_year: 2025
    outputs:
      - ca/employment_income
    capabilities: []
    """)
# The Schedule 6 declaration, test-local: its one export is line 15, the line under test.
SCHEDULE_6 = dedent(f"""\
    form:
      name: {FORM}
      required: true
      exports:
        - {LINE_15}
    """)


def _schedule_6(
    take_home_service: TakeHomeService, salary: str, exemption: str | None = None
) -> Worksheet:
    kinds = bundled_kinds()
    starting = [Artifact(EMPLOYMENT_INCOME, D(salary))]
    if exemption is not None:
        starting.append(Artifact(kinds.kind(LINE_14), D(exemption)))
    worksheets = take_home_service(HEADER, SCHEDULE_6, *PARTS).compute(ONTARIO, 2025, *starting)
    (sheet,) = worksheets[FORM]
    return sheet


@pytest.mark.parametrize(
    ("salary", "expected"),
    [
        # Adjusted family net income (line 15) at salaries of $2,000, $6,000, $20,000, $30,000,
        # $35,000, $40,000 and $70,000 with line 14 blank. Line 14 is read as 0, so each line 15 is
        # the line 13 figure for that salary.
        ("2000", "2000.00"),
        ("6000", "5975.00"),
        ("20000", "19835.00"),
        ("30000", "29735.00"),
        ("35000", "34685.00"),
        ("40000", "39635.00"),
        ("70000", "69335.00"),
    ],
)
def test_schedule_6_line_15_is_line_13_when_line_14_is_blank(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    sheet = _schedule_6(take_home_service, salary)

    assert sheet.get(bundled_kinds().kind(LINE_15)).value == D(expected)


@pytest.mark.parametrize(
    ("salary", "exemption", "expected"),
    [
        # Line 13 for a 20000 salary is 19835.00; line 15 is line 13 less line 14.
        ("20000", "5000.00", "14835.00"),
        ("20000", "19835.00", "0.00"),
        # The form prints no floor on line 15: an exemption above line 13 gives a negative figure.
        ("20000", "25000.00", "-5165.00"),
    ],
)
def test_schedule_6_line_15_subtracts_line_14_without_a_floor(
    take_home_service: TakeHomeService, salary: str, exemption: str, expected: str
) -> None:
    sheet = _schedule_6(take_home_service, salary, exemption)

    assert sheet.get(bundled_kinds().kind(LINE_15)).value == D(expected)


def test_the_line_15_kind_is_registered_and_signed() -> None:
    # Signed: line 15 prints no "if negative" rule, so a line 14 above line 13 gives a negative
    # adjusted family net income.
    kind = bundled_kinds().kind(LINE_15)

    assert kind.identifier == LINE_15
    assert non_negative(kind) is False


@pytest.mark.parametrize(
    ("salary", "exemption", "printed"),
    [
        ("70000", None, "69335.00"),
        ("20000", None, "19835.00"),
        ("20000", "19835.00", "0.00"),
        ("20000", "25000.00", "-5165.00"),
        # Rounded half-up to the cent on the exact difference: 19,835.00 less 0.005 is 19,834.995,
        # on the tie, so 19,835.00; less 0.006 is 19,834.994, so 19,834.99.
        ("20000", "0.005", "19835.00"),
        ("20000", "0.006", "19834.99"),
    ],
)
def test_line_15_prints_cents_through_the_shared_rounding_dataset(
    take_home_service: TakeHomeService, salary: str, exemption: str | None, printed: str
) -> None:
    value = (
        _schedule_6(take_home_service, salary, exemption).get(bundled_kinds().kind(LINE_15)).value
    )

    assert str(value) == printed
    assert value.as_tuple().exponent == -2


def test_the_line_15_step_traces_the_cent_rounding(take_home_service: TakeHomeService) -> None:
    sheet = _schedule_6(take_home_service, "70000")

    (line,) = [
        line
        for line in sheet.trace
        if isinstance(line, SubtractedLine) and line.output.identifier == LINE_15
    ]

    assert line.rounding == CENT
    assert str(line.result) == "69335.00"
