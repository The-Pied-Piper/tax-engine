"""T2204 (2025) line 15, the EI overpayment, as the Ontario take-home manifest part wires it.

T2204 line 15: "Employment insurance overpayment: Enter whichever is less: amount from line 9 or
line 14. If this amount is more than $1, enter it on line 45000 of your return." Line 9 is a pure
copy of line 4, so the part reads line 4. The part has three steps: the lesser of line 4 and
line 14 (`ca/t2204_line_15`), the count of the "more than $1" condition
(`ca/t2204_line_15_count`, 1 when it applies, else 0), and line 15 times that count, the T1 line
45000 amount (`ca/ei_overpayment`).

The manifest part is loaded from the package. The header and the form's export are made up here,
because the shared scaffold owns them. Line 4 (`ca/t2204_premiums_deducted`) and line 14
(`ca/t2204_line_14`) are produced by other tickets, so the test header declares both as required
starting inputs. `ca/ei_overpayment` (the T1 line 45000 amount) is exported by the form too.
"""

from __future__ import annotations

from decimal import Decimal
from textwrap import dedent

import pytest

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.refund import (
    EI_OVERPAYMENT,
    T2204_LINE_14,
    T2204_LINE_15,
    T2204_LINE_15_COUNT,
    T2204_PREMIUMS_DEDUCTED,
)
from tests.jurisdictions.ca_on.conftest import TakeHomeService

D = Decimal

PART = "t2204_line_15.yaml"

HEADER = dedent("""\
    jurisdiction: CA-ON
    version: 1
    valid_from_tax_year: 2025
    inputs:
      - name: ca/t2204_premiums_deducted
        required: true
      - name: ca/t2204_line_14
        required: true
    outputs:
      - ca/t2204_premiums_deducted
      - ca/t2204_line_14
    """)
FORM = dedent("""\
    form:
      name: ca/t2204
      required: true
      exports:
        - ca/t2204_line_15
        - ca/t2204_line_15_count
        - ca/ei_overpayment
    """)


def t2204(take_home_service: TakeHomeService, line_4: str, line_14: str) -> Worksheet:
    """The T2204 worksheet for a line 4 and a line 14."""
    starting = [
        Artifact(T2204_PREMIUMS_DEDUCTED, D(line_4)),
        Artifact(T2204_LINE_14, D(line_14)),
    ]
    (sheet,) = take_home_service(HEADER, FORM, PART).compute(
        JurisdictionCode("CA-ON"), 2025, *starting
    )["ca/t2204"]
    return sheet


@pytest.mark.parametrize(
    ("line_4", "line_14", "line_15", "count", "overpayment"),
    [
        # Salary 2,010 refund case: line 4 is 32.96, line 14 is 22.96.
        ("32.96", "22.96", "22.96", 1, "22.96"),
        # Salary 1,500 and salary 30,000: both lines are 0.
        ("0", "0", "0", 0, "0"),
        # Return DD oracle (salary 70,000, line 4 given 1,148.00): overpayment 70.52.
        ("1148.00", "70.52", "70.52", 1, "70.52"),
        # Line 4 is the lesser, so line 4 wins.
        ("10.00", "22.96", "10.00", 1, "10.00"),
        # Salary 2,033 case: line 15 is 0.34, not more than $1, so the amount is 0.
        ("33.34", "0.34", "0.34", 0, "0"),
        # Exactly $1.00 is not more than $1: count 0, amount 0.
        ("5.00", "1.00", "1.00", 0, "0"),
        # $1.01 is more than $1: count 1, amount 1.01.
        ("5.00", "1.01", "1.01", 1, "1.01"),
        # Tie: line 4 equals line 14, the value is kept.
        ("22.96", "22.96", "22.96", 1, "22.96"),
        # Salary-only $70,000 take-home case: line 4 is 1,077.48, line 14 is 0.
        ("1077.48", "0", "0", 0, "0"),
    ],
)
def test_line_15_count_and_ei_overpayment(
    take_home_service: TakeHomeService,
    line_4: str,
    line_14: str,
    line_15: str,
    count: int,
    overpayment: str,
) -> None:
    sheet = t2204(take_home_service, line_4, line_14)
    assert sheet.get(T2204_LINE_15).value == D(line_15)
    assert sheet.get(T2204_LINE_15_COUNT).value == count
    assert sheet.get(EI_OVERPAYMENT).value == D(overpayment)


@pytest.mark.parametrize("line_4", ["1077.48", "328.00"], ids=["salary_70000", "salary_20000"])
def test_ei_overpayment_prints_cents_at_70000_and_20000(
    take_home_service: TakeHomeService, line_4: str
) -> None:
    # Salary only, so line 14 is 0: the count is 0 and the overpayment is the cent zero of the
    # rounding dataset, not a bare 0.
    overpayment = t2204(take_home_service, line_4, "0").get(EI_OVERPAYMENT).value

    assert str(overpayment) == "0.00"
    assert overpayment.as_tuple().exponent == -2
