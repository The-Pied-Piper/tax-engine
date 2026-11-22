"""MB479 (2025) line 12, computed from the real part files through the real engine.

Form text (Form MB479, CRA 5007-TC, 5007-tc-25e.txt): "Line 12 and line 60900: Add lines 9 to 11."
Lines 9, 10 and 11 are optional inputs of a part (`mb479_line_12_inputs.yaml`), loaded beside the
real `mb479_line_12.yaml` under a header made up here. A line left blank is read as 0, and the sum
is rounded half-up to the cent. The hand figures are asserted (not a CRA example).
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from tests.jurisdictions.ca_mb.mb428_medical_support import MB_PARTS, compute_line

FILE = "mb479_line_12.yaml"
OUTPUT = "ca-mb/mb479_spouse_credits_line_12"
LINE_9 = "ca-mb/mb479_basic_credit_spouse_line_9"
LINE_10 = "ca-mb/mb479_age_credit_spouse_line_10"
LINE_11 = "ca-mb/mb479_disability_credit_spouse_line_11"


def _line_12(tmp_path: Path, given: dict[str, str]) -> str:
    value = compute_line(
        tmp_path,
        FILE,
        {},
        OUTPUT,
        extra_parts=(MB_PARTS / "mb479_line_12_inputs.yaml",),
        part_inputs=given,
        outputs=() if given else (LINE_9,),
        form_name="ca-mb/mb479",
    )
    return str(value)


@pytest.mark.parametrize(
    ("given", "expected"),
    [
        ({}, "0.00"),
        ({LINE_9: "195"}, "195.00"),
        ({LINE_10: "113"}, "113.00"),
        ({LINE_11: "113"}, "113.00"),
        ({LINE_9: "195", LINE_11: "113"}, "308.00"),
        ({LINE_9: "195", LINE_10: "113", LINE_11: "113"}, "421.00"),
        ({LINE_9: "0.005"}, "0.01"),
    ],
)
def test_line_12_adds_lines_9_to_11(tmp_path: Path, given: dict[str, str], expected: str) -> None:
    assert _line_12(tmp_path, given) == expected


def test_the_part_is_one_sum_step_with_a_blank_rule_for_each_line() -> None:
    part = yaml.safe_load((MB_PARTS / FILE).read_text("utf-8"))

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": "ca-mb/mb479"}
    (step,) = part["capabilities"]
    assert list(step) == [
        "name",
        "title",
        "reference",
        "unit",
        "params",
        "consumes",
        "blank",
        "produces",
    ]
    assert step == {
        "name": "core/sum",
        "title": "Spouse or common-law partner credits",
        "reference": "12",
        "unit": "ca/cad",
        "params": {"rounding": "ca-mb/cent_rounding"},
        "consumes": {"parts": [LINE_9, LINE_10, LINE_11]},
        "blank": {LINE_9: "0", LINE_10: "0", LINE_11: "0"},
        "produces": {"output": OUTPUT},
    }
