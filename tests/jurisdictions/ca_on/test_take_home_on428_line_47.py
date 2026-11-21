"""ON428 (2025) line 47, computed from the real part file through the real engine.

Form text (Form ON428, CRA 5006-c-25e.txt): "Line 47: Amount from line 13 of your federal Schedule
9 multiplied by 5.05% =". The inputs come from other parts, so this test declares them in a header
of its own and loads the take-home folder's `on428_line_47.yaml` beside it. The output is `ca-
on/on428_donations_credit_at_rate_line_47`, exported by the form. The hand figures are asserted
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
INPUTS = ("ca-on/on428_donations_amount_line_47",)
OUTPUT = "ca-on/on428_donations_credit_at_rate_line_47"
PART = "on428_line_47.yaml"

HEADER = (
    "jurisdiction: CA-ON\nversion: 1\nvalid_from_tax_year: 2025\ninputs:\n"
    + "".join(f"  - name: {name}\n    required: true\n" for name in INPUTS)
    + "outputs:\n"
    + "".join(f"  - {name}\n" for name in INPUTS)
)

FORM = f"""\
form:
  name: ca-on/on428
  required: true
  exports:
    - {OUTPUT}
capabilities: []
"""


def _compute(take_home_service: TakeHomeService, values: tuple[str, ...]) -> Decimal:
    kinds = bundled_kinds()
    given = [Artifact(kinds.kind(n), D(v)) for n, v in zip(INPUTS, values, strict=True)]
    worksheet = take_home_service(HEADER, FORM, PART).compute(CODE, 2025, *given)["ca-on/on428"][0]
    value = worksheet.get(kinds.kind(OUTPUT)).value
    assert isinstance(value, Decimal)
    return value


@pytest.mark.parametrize(("values", "expected"), [(("200",), "10.10"), (("0",), "0.00")])
def test_line_47(
    take_home_service: TakeHomeService, values: tuple[str, ...], expected: str
) -> None:
    assert _compute(take_home_service, values) == D(expected)
