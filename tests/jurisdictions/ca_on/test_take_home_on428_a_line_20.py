"""ON428-A (2025) line 20, as the Ontario take-home manifest part wires it.

Form text (ON428-A, CRA 5006-a-25e.txt in cra-docs/docs/cra-forms-2025): "Line 14: Amount from line
5 above
(maximum $875) / Line 20: Line 14 minus line 19 (if negative, enter "0") Enter this amount on line
62140 of your Form ON428." Line 14 is a copy of line 5, so line 20 reads line 5 itself
(`ca-on/lift_maximum_credit`, a plain starting input here). Line 19 is `ca-on/lift_reduction`, also
a plain starting input here. Line 20 is one core/subtract_not_below_zero over line 5 less line 19.

The manifest part is loaded from the package. The header and the form's export are made up here,
because the shared scaffold owns them.
"""

from __future__ import annotations

from decimal import Decimal
from textwrap import dedent

import pytest

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.jurisdictions.ca_on.catalog import (
    LIFT_CREDIT_SINGLE,
    LIFT_MAXIMUM_CREDIT,
    LIFT_REDUCTION,
)
from tests.jurisdictions.ca_on.conftest import TakeHomeService

D = Decimal
PART = "on428_a_line_20.yaml"

HEADER = dedent("""\
    jurisdiction: CA-ON
    version: 1
    valid_from_tax_year: 2025
    inputs:
      - name: ca-on/lift_maximum_credit
        required: true
      - name: ca-on/lift_reduction
        required: true
    outputs:
      - ca-on/lift_reduction
    """)
FORM = dedent("""\
    form:
      name: ca-on/on428_a
      required: true
      exports:
        - ca-on/lift_credit_single
    """)


def line_20(take_home_service: TakeHomeService, maximum: str, reduction: str) -> Decimal:
    worksheets = take_home_service(HEADER, FORM, PART).compute(
        JurisdictionCode("CA-ON"),
        2025,
        Artifact(LIFT_MAXIMUM_CREDIT, D(maximum)),
        Artifact(LIFT_REDUCTION, D(reduction)),
    )
    (sheet,) = worksheets["ca-on/on428_a"]
    return sheet.get(LIFT_CREDIT_SINGLE).value


@pytest.mark.parametrize(
    ("maximum", "reduction", "expected"),
    [
        # Line 19 above line 5 gives "0", as the form says.
        ("875.00", "1841.75", "0"),
        # Partly reduced.
        ("875.00", "356.75", "518.25"),
        # Nothing reduced: the full maximum.
        ("875.00", "0", "875.00"),
        # Under the maximum, nothing reduced.
        ("505.00", "0", "505.00"),
        # Exactly equal: the difference is zero.
        ("875.00", "875.00", "0"),
    ],
)
def test_line_20_is_line_5_minus_line_19_not_below_zero(
    take_home_service: TakeHomeService, maximum: str, reduction: str, expected: str
) -> None:
    assert line_20(take_home_service, maximum, reduction) == D(expected)
