"""MB428 (2025) line 56, computed from the real part file through the real engine.

Form text (Form MB428, CRA 5007-c-25e.txt):
"Line 56 and line 58969: Line 54 plus line 55 ="
The upstream lines come in as inputs of a header made up here, and the real
`mb428_credits_line_56.yaml` is loaded beside it.
The hand figures are asserted (not a CRA example).
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import pytest

from tests.jurisdictions.ca_mb.mb428_medical_support import compute_line

D = Decimal
INPUTS = (
    "ca-mb/mb428_donations_credit_at_rate_line_54",
    "ca-mb/mb428_donations_credit_at_rate_line_55",
)
OUTPUT = "ca-mb/mb428_donations_credit_line_56"
PART = "mb428_credits_line_56.yaml"


@pytest.mark.parametrize(
    ("values", "expected"),
    [(("108.00", "174.00"), "282.00"), (("0", "0"), "0.00"), (("10.80", "0"), "10.80")],
)
def test_line_56(tmp_path: Path, values: tuple[str, ...], expected: str) -> None:
    given = dict(zip(INPUTS, values, strict=True))

    assert compute_line(tmp_path, PART, given, OUTPUT) == D(expected)
