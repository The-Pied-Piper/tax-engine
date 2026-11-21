"""MB479 (2025) line 14 box B, computed from the real part files through the real engine.

Form text (Form MB479, CRA 5007-TC, 5007-tc-25e.txt):
"Line 14: Number of disability claims Line 60950 multiplied by $113 =".
The count in box A comes in as an input of a header made up here, and the real
`mb479_line_14_amount.yaml` and `mb479_line_14.yaml` are loaded beside it.
The hand figures are asserted (not a CRA example).
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import pytest

from tests.jurisdictions.ca_mb.part_support import MB_PARTS, compute_line

D = Decimal
INPUT = "ca-mb/mb479_disability_claims_number_line_14"
OUTPUT = "ca-mb/mb479_disability_credit_line_14"


@pytest.mark.parametrize(
    ("count", "expected"),
    [("1", "113.00"), ("2", "226.00"), ("3", "339.00"), ("0", "0.00")],
)
def test_line_14(tmp_path: Path, count: str, expected: str) -> None:
    value = compute_line(
        tmp_path,
        "mb479_line_14.yaml",
        {INPUT: count},
        OUTPUT,
        extra_parts=(MB_PARTS / "mb479_line_14_amount.yaml",),
        form_name="ca-mb/mb479",
    )

    assert value == D(expected)
