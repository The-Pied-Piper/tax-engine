"""MB428 (2025) line 46, computed from the real part file through the real engine.

Form text (Form MB428, CRA 5007-c-25e.txt):
"Line 46: Line 44 multiplied by the percentage from line 45 ="; line 45 is "Applicable rate 3%".
The upstream lines come in as inputs of a header made up here, and the real
`mb428_credits_line_46.yaml` is loaded beside it.
The hand figures are asserted (not a CRA example).
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import pytest

from tests.jurisdictions.ca_mb.mb428_medical_support import compute_line

D = Decimal
INPUTS = ("ca-mb/mb428_net_income_line_44",)
OUTPUT = "ca-mb/mb428_medical_expenses_rate_amount_line_46"
PART = "mb428_credits_line_46.yaml"


@pytest.mark.parametrize(
    ("line_44", "expected"),
    [("69335.00", "2080.05"), ("39999.99", "1200.00"), ("0", "0.00")],
)
def test_line_46(tmp_path: Path, line_44: str, expected: str) -> None:
    # 3% of 69,335.00 is 2,080.05; 3% of 39,999.99 is 1,199.9997, rounded half-up to 1,200.00.
    assert compute_line(tmp_path, PART, dict(zip(INPUTS, (line_44,), strict=True)), OUTPUT) == D(
        expected
    )
