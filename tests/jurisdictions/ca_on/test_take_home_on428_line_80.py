"""ON428 (2025) line 80, the Ontario tax reduction, computed from the real part file.

Form text (Form ON428, CRA 5006-c-25e.txt): "Enter "0" on line 80 if any of the following applies
to you:" followed by the printed conditions, one of them "There is an amount on line 72"; "Line 79:
Amount from line 73 above"; "Line 80: Line 78 minus line 79 (if negative, enter "0") Ontario tax
reduction =".

The part has three steps:

1. `core/subtract_not_below_zero`: line 78 (`ca-on/on428_tax_reduction_doubled_line_78`) less line
   73 (`ca-on/on428_tax_with_minimum_tax_addition_line_73`), not below zero, the amount
   `ca-on/on428_tax_reduction_before_conditions_line_80`. Line 79 is a copy of line 73, so it has no
   step of its own.
2. `ca/count_by_conditions`: the form's "There is an amount on line 72" condition
   (`ca-on/on428_line_80_conditions`) on line 72
   (`ca-on/on428_additional_tax_for_minimum_tax_line_72`), giving the count
   `ca-on/on428_tax_reduction_conditions_count_line_80`. The count is 0 when line 72 is an amount
   other than 0, and 1 otherwise. Line 72 is an optional input: a salary-only caller leaves it out,
   it is read as blank, and the blank rule of the part reads that blank as "0".
3. `core/times_count`: step 1 times step 2, the output `ca-on/on428_ontario_tax_reduction_line_80`,
   exported by the form. So a line 72 amount gives 0, and no amount on line 72 gives step 1.

Only the line 72 condition is in this part. The form's other printed conditions are not read here.

The inputs are lines 78, 73 and 72, produced by other parts or given by the caller. This test
declares them as the inputs of its header (line 72 optional, as its real inputs part declares it)
and loads the take-home folder's `on428/on428_line_80.yaml` beside it. The output and the two
intermediate steps are exported by the test's form, so each can be read from the worksheet.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.worksheet import Worksheet
from tests.jurisdictions.ca_on.conftest import TakeHomeService
from tests.kinds import bundled_kinds

D = Decimal
CODE = JurisdictionCode("CA-ON")
LINE_72 = "ca-on/on428_additional_tax_for_minimum_tax_line_72"
LINE_73 = "ca-on/on428_tax_with_minimum_tax_addition_line_73"
LINE_78 = "ca-on/on428_tax_reduction_doubled_line_78"
BEFORE_CONDITIONS = "ca-on/on428_tax_reduction_before_conditions_line_80"
CONDITIONS_COUNT = "ca-on/on428_tax_reduction_conditions_count_line_80"
LINE_80 = "ca-on/on428_ontario_tax_reduction_line_80"
PART = "on428_line_80.yaml"

BASIS = (
    "Line 72: If you entered an amount on line 11 of Part 5 of Form T691, use Worksheet ON428 to "
    "calculate your additional tax for minimum tax purposes"
)
HEADER = f"""\
jurisdiction: CA-ON
version: 1
valid_from_tax_year: 2025
inputs:
  - name: {LINE_78}
    required: true
  - name: {LINE_73}
    required: true
  - name: {LINE_72}
    required: false
    default: null
    basis: '{BASIS}'
outputs:
  - {LINE_78}
  - {LINE_73}
capabilities: []
"""

FORM = f"""\
form:
  name: ca-on/on428
  required: true
  exports:
    - {LINE_80}
capabilities: []
"""
# The steps test also exports the two intermediate kinds, so the test can read each step.
STEPS_FORM = f"""\
form:
  name: ca-on/on428
  required: true
  exports:
    - {LINE_80}
    - {BEFORE_CONDITIONS}
    - {CONDITIONS_COUNT}
capabilities: []
"""


def _worksheet(
    take_home_service: TakeHomeService,
    line_78: str,
    line_73: str,
    line_72: str | None,
    form: str = FORM,
) -> Worksheet:
    kinds = bundled_kinds()
    given = [Artifact(kinds.kind(LINE_78), D(line_78)), Artifact(kinds.kind(LINE_73), D(line_73))]
    if line_72 is not None:
        given.append(Artifact(kinds.kind(LINE_72), D(line_72)))
    return take_home_service(HEADER, form, PART).compute(CODE, 2025, *given)["ca-on/on428"][0]


def _line_80(
    take_home_service: TakeHomeService, line_78: str, line_73: str, line_72: str | None = None
) -> Decimal:
    value = (
        _worksheet(take_home_service, line_78, line_73, line_72)
        .get(bundled_kinds().kind(LINE_80))
        .value
    )
    assert isinstance(value, Decimal)
    return value


@pytest.mark.parametrize(
    ("line_78", "line_73", "line_80"),
    [
        # A $20,000 salary: line 78 is 588.00 and line 73 is 300.14, so line 80 is 287.86.
        ("588.00", "300.14", "287.86"),
        # A $70,000 salary: line 78 is 588.00 and line 73 is 3,311.45, so line 80 floors to 0.00.
        ("588.00", "3311.45", "0.00"),
        # A $150,000 salary: line 78 is 588.00 and line 73 is 14,102.14, so line 80 floors to 0.00.
        ("588.00", "14102.14", "0.00"),
        # Line 78 equal to line 73: the difference is 0, so line 80 is 0.00.
        ("300.14", "300.14", "0.00"),
        # Line 73 above line 78: the difference is negative, so line 80 floors to 0.00.
        ("100.00", "300.14", "0.00"),
        # Line 78 above line 73: the difference is positive, so line 80 is 488.00.
        ("588.00", "100.00", "488.00"),
    ],
)
def test_line_80_is_line_78_minus_line_73_not_below_zero_when_line_72_is_left_out(
    take_home_service: TakeHomeService, line_78: str, line_73: str, line_80: str
) -> None:
    assert _line_80(take_home_service, line_78, line_73) == D(line_80)


@pytest.mark.parametrize(
    ("line_78", "line_73", "line_72"),
    [
        # Line 72 is 100.00, an amount: the condition applies, so line 80 is 0 whatever the
        # difference. Line 78 less line 73 would be 187.86 without it.
        ("588.00", "400.14", "100.00"),
        # Line 72 is one cent, an amount: the condition applies, so line 80 is 0.
        ("588.00", "300.14", "0.01"),
    ],
)
def test_line_80_is_0_when_line_72_is_an_amount(
    take_home_service: TakeHomeService, line_78: str, line_73: str, line_72: str
) -> None:
    assert _line_80(take_home_service, line_78, line_73, line_72) == D("0.00")


def test_line_72_of_0_is_not_an_amount_so_line_80_is_line_78_minus_line_73(
    take_home_service: TakeHomeService,
) -> None:
    # Line 72 is "0.00": the condition "There is an amount on line 72" does not apply, so line 80
    # is line 78 (588.00) less line 73 (300.14), 287.86, as it is with line 72 left out.
    assert _line_80(take_home_service, "588.00", "300.14", "0.00") == D("287.86")


@pytest.mark.parametrize(
    ("line_72", "count"),
    [
        # Line 72 left out is read as blank and then as "0": not an amount, so the count is 1.
        (None, 1),
        ("0.00", 1),
        # Line 72 an amount: the condition applies, so the count is 0.
        ("100.00", 0),
    ],
)
def test_the_steps_are_the_difference_and_the_condition_count(
    take_home_service: TakeHomeService, line_72: str | None, count: int
) -> None:
    # Line 78 is 588.00 and line 73 is 300.14: step 1 is 287.86, and step 3 multiplies it by the
    # count from step 2.
    kinds = bundled_kinds()
    sheet = _worksheet(take_home_service, "588.00", "300.14", line_72, STEPS_FORM)

    assert sheet.get(kinds.kind(BEFORE_CONDITIONS)).value == D("287.86")
    assert sheet.get(kinds.kind(CONDITIONS_COUNT)).value == count
