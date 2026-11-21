"""MB428 (2025) line 48, computed from the real part file through the real engine.

Form text (Form MB428, CRA 5007-c-25e.txt):
"Line 48: Line 43 minus line 47 (if negative, enter "0") ="
The upstream lines come in as inputs of a header made up here, and the real
`mb428_credits_line_48.yaml` is loaded beside it.
The hand figures are asserted (not a CRA example).
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import pytest

from tests.jurisdictions.ca_mb.part_support import compute_line

D = Decimal
INPUTS = (
    "ca-mb/mb428_medical_expenses_line_43",
    "ca-mb/mb428_medical_expenses_limited_amount_line_47",
)
OUTPUT = "ca-mb/mb428_medical_expenses_over_limit_line_48"
PART = "mb428_credits_line_48.yaml"


@pytest.mark.parametrize(
    ("values", "expected"),
    [
        (("5000", "1728.00"), "3272.00"),
        (("1000", "1728.00"), "0.00"),
        (("1728.00", "1728.00"), "0.00"),
        (("0", "1728.00"), "0.00"),
    ],
)
def test_line_48(tmp_path: Path, values: tuple[str, ...], expected: str) -> None:
    given = dict(zip(INPUTS, values, strict=True))

    assert compute_line(tmp_path, PART, given, OUTPUT) == D(expected)
