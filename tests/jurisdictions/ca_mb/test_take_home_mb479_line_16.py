"""MB479 (2025) line 16 box B, computed from the real part files through the real engine.

Form text (Form MB479, CRA 5007-TC, 5007-tc-25e.txt):
"Line 16: Number of dependent children Line 60999 multiplied by $26 =".
The count in box A comes in as an input of a header made up here, and the real
`mb479_line_16_amount.yaml` and `mb479_line_16.yaml` are loaded beside it.
The hand figures are asserted (not a CRA example).
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import pytest

from tests.jurisdictions.ca_mb.mb428_medical_support import MB_PARTS, compute_line

D = Decimal
INPUT = "ca-mb/mb479_dependent_children_number_line_16"
OUTPUT = "ca-mb/mb479_dependent_children_credit_line_16"


@pytest.mark.parametrize(
    ("count", "expected"),
    [("1", "26.00"), ("2", "52.00"), ("3", "78.00"), ("0", "0.00")],
)
def test_line_16(tmp_path: Path, count: str, expected: str) -> None:
    value = compute_line(
        tmp_path,
        "mb479_line_16.yaml",
        {INPUT: count},
        OUTPUT,
        extra_parts=(MB_PARTS / "mb479_line_16_amount.yaml",),
        form_name="ca-mb/mb479",
    )

    assert value == D(expected)
