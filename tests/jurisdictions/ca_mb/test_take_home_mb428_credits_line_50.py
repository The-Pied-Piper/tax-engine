"""MB428 (2025) line 50, computed from the real part file through the real engine.

Form text (Form MB428, CRA 5007-c-25e.txt):
"Line 50 and line 58769: Line 48 plus line 49 ="
The upstream lines come in as inputs of a header made up here, and the real
`mb428_credits_line_50.yaml` is loaded beside it.
The hand figures are asserted (not a CRA example).
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import pytest

from tests.jurisdictions.ca_mb.mb428_medical_support import compute_line

D = Decimal
INPUTS = (
    "ca-mb/mb428_medical_expenses_over_limit_line_48",
    "ca-mb/mb428_other_dependants_medical_expenses_line_49",
)
OUTPUT = "ca-mb/mb428_medical_expenses_line_50"
PART = "mb428_credits_line_50.yaml"


@pytest.mark.parametrize(
    ("values", "expected"),
    [(("3272.00", "250.50"), "3522.50"), (("0", "0"), "0.00"), (("0", "1000"), "1000.00")],
)
def test_line_50(tmp_path: Path, values: tuple[str, ...], expected: str) -> None:
    given = dict(zip(INPUTS, values, strict=True))

    assert compute_line(tmp_path, PART, given, OUTPUT) == D(expected)
