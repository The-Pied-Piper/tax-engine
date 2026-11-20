"""Revenu Quebec Schedule F (TP-1.D.F-V, 2025-12), Part A, line 14,
"Correction of employment income (line 105)", as the Quebec take-home
manifest wires it.

Line 14 is an input of the form: a caller who gives no correction leaves it blank, and line 16
reads it as 0.
"""

from __future__ import annotations

from pathlib import Path

import yaml

import tax_engine.jurisdictions.ca_qc

PART = (
    Path(tax_engine.jurisdictions.ca_qc.__file__).parent
    / "manifests"
    / "2025"
    / "tp1_schedule_f_line_14_input.yaml"
)


def test_line_14_is_an_optional_input_left_blank() -> None:
    (declared,) = yaml.safe_load(PART.read_text(encoding="utf-8"))["inputs"]

    assert declared["name"] == "ca-qc/tp1_schedule_f_employment_income_correction_line_14"
    assert declared["reference"] == "14"
    assert declared["required"] is False
    assert declared["default"] is None
