"""MB428 (2025) line 47, computed from the real part file through the real engine.

Form text (Form MB428, CRA 5007-c-25e.txt):
"Line 47: Enter whichever is less: $1,728 or the amount from line 46."
The upstream lines come in as inputs of a header made up here, and the real
`mb428_credits_line_47.yaml` is loaded beside it.
The hand figures are asserted (not a CRA example).
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import pytest

from tests.jurisdictions.ca_mb.part_support import compute_line

D = Decimal
INPUTS = ("ca-mb/mb428_medical_expenses_rate_amount_line_46",)
OUTPUT = "ca-mb/mb428_medical_expenses_limited_amount_line_47"
PART = "mb428_credits_line_47.yaml"


@pytest.mark.parametrize(
    ("line_46", "expected"),
    [("2080.05", "1728.00"), ("1728.00", "1728.00"), ("1200.50", "1200.50"), ("0", "0.00")],
)
def test_line_47(tmp_path: Path, line_46: str, expected: str) -> None:
    assert compute_line(tmp_path, PART, dict(zip(INPUTS, (line_46,), strict=True)), OUTPUT) == D(
        expected
    )
