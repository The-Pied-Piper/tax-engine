"""Revenu Quebec Schedule F (TP-1.D.F-V, 2025-12), Part A, line 68,
"Add lines 41 through 62", as the Quebec take-home
manifest wires it.

Lines 41 to 62 are skipped, so their printed sum, line 68, is one optional input left blank; line
70 reads it as 0.
"""

from __future__ import annotations

from pathlib import Path

import yaml

import tax_engine.jurisdictions.ca_qc

PART = (
    Path(tax_engine.jurisdictions.ca_qc.__file__).parent
    / "manifests"
    / "2025"
    / "tp1_schedule_f_line_68_input.yaml"
)


def test_line_68_is_an_optional_input_left_blank() -> None:
    (declared,) = yaml.safe_load(PART.read_text(encoding="utf-8"))["inputs"]

    assert declared["name"] == "ca-qc/tp1_schedule_f_deductions_line_68"
    assert declared["reference"] == "68"
    assert declared["required"] is False
    assert declared["default"] is None
