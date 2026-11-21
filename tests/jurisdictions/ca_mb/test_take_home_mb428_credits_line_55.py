"""MB428 (2025) line 55, computed from the real part file through the real engine.

Form text (Form MB428, CRA 5007-c-25e.txt):
"Line 55: Amount from line 14 of your federal Schedule 9 multiplied by 17.4% ="
The upstream lines come in as inputs of a header made up here, and the real
`mb428_credits_line_55.yaml` is loaded beside it.
The hand figures are asserted (not a CRA example).
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import pytest

from tests.jurisdictions.ca_mb.part_support import compute_line

D = Decimal
INPUTS = ("ca-mb/mb428_donations_amount_line_55",)
OUTPUT = "ca-mb/mb428_donations_credit_at_rate_line_55"
PART = "mb428_credits_line_55.yaml"


@pytest.mark.parametrize(
    ("amount", "expected"), [("1000", "174.00"), ("0.03", "0.01"), ("0", "0.00")]
)
def test_line_55(tmp_path: Path, amount: str, expected: str) -> None:
    given = dict(zip(INPUTS, (amount,), strict=True))

    assert compute_line(tmp_path, PART, given, OUTPUT) == D(expected)
