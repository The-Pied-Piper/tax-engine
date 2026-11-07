"""T1 (2025) line 23600, net income, computed from the real part files through the real engine.

T1 line 23600: "Line 56 and line 23600: Line 54 minus line 55 (if negative, enter "0")" (5006-R,
page 4). The step subtracts the social benefits repayment (line 23500,
`ca/social_benefits_repayment`) from the net income before adjustments (line 23400,
`ca/net_income_before_adjustments`), not below zero, and the output is `ca/net_income`.

Line 23400 is produced by another ticket (#217), so this test declares it as a required starting
input in a header of its own. Line 23500 is an optional input declared in the take-home folder's
`t1_taxable_income_inputs.yaml`, which this test loads beside the line 23600 part: a request that
leaves it out reads it as its default, "0", as the form says for a filer with no EI or OAS income.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tests.jurisdictions.ca_on.conftest import TakeHomeService
from tests.kinds import bundled_kinds

D = Decimal
CODE = JurisdictionCode("CA-ON")
FORM = "ca/t1_taxable_income"
LINE_23400 = "ca/net_income_before_adjustments"
LINE_23500 = "ca/social_benefits_repayment"
LINE_23600 = "ca/net_income"
PARTS = ("t1_taxable_income_inputs.yaml", "t1_taxable_income_line_23600.yaml")
HEADER = f"""\
jurisdiction: CA-ON
version: 1
valid_from_tax_year: 2025
inputs:
  - name: {LINE_23400}
    required: true
outputs:
  - {LINE_23400}
capabilities: []
"""
FORM_TEXT = f"""\
form:
  name: {FORM}
  required: true
  exports:
    - {LINE_23600}
capabilities: []
"""


def _line_23600(
    take_home_service: TakeHomeService, line_23400: str, line_23500: str | None
) -> Decimal:
    kinds = bundled_kinds()
    starting = [Artifact(kinds.kind(LINE_23400), D(line_23400))]
    if line_23500 is not None:
        starting.append(Artifact(kinds.kind(LINE_23500), D(line_23500)))
    worksheet = take_home_service(HEADER, FORM_TEXT, *PARTS).compute(CODE, 2025, *starting)[FORM][0]
    value = worksheet.get(kinds.kind(LINE_23600)).value
    assert isinstance(value, Decimal)
    return value


@pytest.mark.parametrize(
    ("line_23400", "line_23500", "expected"),
    [
        # A $70,000 salary: line 23400 is 69,335.00, and line 23500 is left out, so it is 0.
        ("69335.00", None, "69335.00"),
        # The $90,000 salary, above the CPP ceiling: line 23400 is 88,926.00, line 23500 left out.
        ("88926.00", None, "88926.00"),
        # Line 23500 given as 1,000: line 23600 is line 23400 less it.
        ("69335.00", "1000", "68335.00"),
        # Line 23500 above line 23400: the difference is negative, so line 23600 is "0", as the
        # form says (if negative, enter "0").
        ("1000.00", "5000", "0.00"),
    ],
)
def test_line_23600_is_line_23400_less_line_23500_and_not_below_zero(
    take_home_service: TakeHomeService, line_23400: str, line_23500: str | None, expected: str
) -> None:
    assert _line_23600(take_home_service, line_23400, line_23500) == D(expected)
