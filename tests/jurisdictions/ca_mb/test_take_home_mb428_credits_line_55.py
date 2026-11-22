"""MB428 (2025) line 55, computed from the real part file through the real engine.

Form text (Form MB428, CRA 5007-c-25e.txt):
"Line 55: Amount from line 14 of your federal Schedule 9 multiplied by 17.4% ="
Schedule 9 line 14 comes from the real federal Schedule 9 parts, given line 12 as its input; the
real `mb428_credits_line_55.yaml` is loaded beside it.
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
OUTPUT = "ca-mb/mb428_donations_credit_at_rate_line_55"
PART = "mb428_credits_line_55.yaml"


@pytest.mark.parametrize(
    ("line_12", "expected"), [("1000", "139.20"), ("200.03", "0.01"), ("0", "0.00")]
)
def test_line_55(tmp_path: Path, line_12: str, expected: str) -> None:
    value = compute_line(
        tmp_path,
        PART,
        {},
        OUTPUT,
        extra_parts=form_parts("schedule_9"),
        part_inputs={LINE_12: line_12},
    )

    assert value == D(expected)
