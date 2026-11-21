"""ON428 (2025) line 41, computed from the real part file through the real engine.

Form text (Form ON428, CRA 5006-c-25e.txt): "Line 41: Line 36 minus line 40 (if negative, enter "0")
=". Line 36 is the final step of `on428_line_36.yaml`,
`ca-on/on428_medical_expenses_allowed_line_36` (the claim after the printed maximums). The inputs
come from other parts, so this test declares them in a header of its own and loads the take-home
folder's `on428_line_41.yaml` beside it. The output is `ca-
on/on428_medical_expenses_over_limit_line_41`, exported by the form. The hand figures are asserted
(not a CRA example).
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
INPUTS = (
    "ca-on/on428_medical_expenses_allowed_line_36",
    "ca-on/on428_medical_expenses_limited_amount_line_40",
)
OUTPUT = "ca-on/on428_medical_expenses_over_limit_line_41"
PART = "on428_line_41.yaml"

HEADER = "jurisdiction: CA-ON\nversion: 1\nvalid_from_tax_year: 2025\noutputs:\n" + "".join(
    f"  - {name}\n" for name in INPUTS
)

FORM = (
    f"""\
form:
  name: ca-on/on428
  required: true
  exports:
    - {OUTPUT}
inputs:
"""
    + "".join(f"  - name: {name}\n    required: true\n" for name in INPUTS)
    + "capabilities: []\n"
)


def _compute(take_home_service: TakeHomeService, values: tuple[str, ...]) -> Decimal:
    kinds = bundled_kinds()
    given = [Artifact(kinds.kind(n), D(v)) for n, v in zip(INPUTS, values, strict=True)]
    worksheet = take_home_service(HEADER, FORM, PART).compute(CODE, 2025, *given)["ca-on/on428"][0]
    value = worksheet.get(kinds.kind(OUTPUT)).value
    assert isinstance(value, Decimal)
    return value


@pytest.mark.parametrize(
    ("values", "expected"), [(("5000", "2080.05"), "2919.95"), (("1000", "2080.05"), "0.00")]
)
def test_line_41(
    take_home_service: TakeHomeService, values: tuple[str, ...], expected: str
) -> None:
    assert _compute(take_home_service, values) == D(expected)
