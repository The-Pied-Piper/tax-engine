"""ON428 (2025) line 43, computed from the real part file through the real engine.

Form text (Form ON428, CRA 5006-c-25e.txt): "Line 43 and line 58769: Line 41 plus line 42 =". The
inputs come from other parts, so this test declares them in a header of its own and loads the
take-home folder's `on428_line_43.yaml` beside it. The output is `ca-
on/on428_medical_expenses_line_43`, exported by the form. The hand figures are asserted (not a CRA
example).
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tests.jurisdictions.ca_on.conftest import TakeHomeService
from tests.kinds import bundled_kinds

D = Decimal
CODE = JurisdictionCode("CA-ON")
INPUTS = (
    "ca-on/on428_medical_expenses_over_limit_line_41",
    "ca-on/on428_other_dependants_medical_expenses_line_42",
)
OUTPUT = "ca-on/on428_medical_expenses_line_43"
PART = "on428_line_43.yaml"

HEADER = "jurisdiction: CA-ON\nversion: 1\nvalid_from_tax_year: 2025\noutputs: []\n"


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
    worksheet = take_home_service(HEADER, FORM, PART).compute(
        TaxCalculationRequest(CODE, 2025, tuple(given))
    )["ca-on/on428"][0]
    value = worksheet.get(kinds.kind(OUTPUT)).value
    assert isinstance(value, Decimal)
    return value


@pytest.mark.parametrize(
    ("values", "expected"), [(("2919.95", "250.50"), "3170.45"), (("0", "0"), "0.00")]
)
def test_line_43(
    take_home_service: TakeHomeService, values: tuple[str, ...], expected: str
) -> None:
    assert _compute(take_home_service, values) == D(expected)
