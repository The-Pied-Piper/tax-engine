"""MB428 (2025) line 54, computed from the real part file through the real engine.

Form text (Form MB428, CRA 5007-c-25e.txt):
"Line 54: Amount from line 13 of your federal Schedule 9 multiplied by 10.8% ="
Schedule 9 line 13 comes from the real federal Schedule 9 parts, given line 12 as its input; the
real `mb428_credits_line_54.yaml` is loaded beside it.
The hand figures are asserted (not a CRA example).
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import pytest

from tests.federal_forms import form_parts
from tests.jurisdictions.ca_mb.mb428_medical_support import compute_line

D = Decimal
LINE_12 = "ca/donations_and_gifts_line_12"
OUTPUT = "ca-mb/mb428_donations_credit_at_rate_line_54"
PART = "mb428_credits_line_54.yaml"


@pytest.mark.parametrize(
    ("line_12", "expected"), [("1000", "21.60"), ("150", "16.20"), ("0.05", "0.01"), ("0", "0.00")]
)
def test_line_54(tmp_path: Path, line_12: str, expected: str) -> None:
    value = compute_line(
        tmp_path,
        PART,
        {},
        OUTPUT,
        extra_parts=form_parts("schedule_9"),
        part_inputs={LINE_12: line_12},
    )

    assert value == D(expected)
