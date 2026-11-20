"""Revenu Quebec Schedule F (TP-1.D.F-V, 2025-12), Part A, line 34,
"Add lines 20, 22 and 25 through 33", as the Quebec take-home
manifest wires it.

Lines 20 to 33 are skipped, so their printed sum, line 34, is one optional input left blank; line
36 reads it as 0.
"""

from __future__ import annotations

from pathlib import Path

import yaml

import tax_engine.jurisdictions.ca_qc

PART = (
    Path(tax_engine.jurisdictions.ca_qc.__file__).parent
    / "manifests"
    / "2025"
    / "tp1_schedule_f_line_34_input.yaml"
)


def test_line_34_is_an_optional_input_left_blank() -> None:
    (declared,) = yaml.safe_load(PART.read_text(encoding="utf-8"))["inputs"]

    assert declared["name"] == "ca-qc/tp1_schedule_f_lines_20_to_33_total_line_34"
    assert declared["reference"] == "34"
    assert declared["required"] is False
    assert declared["default"] is None
