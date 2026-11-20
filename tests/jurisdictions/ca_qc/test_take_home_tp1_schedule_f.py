"""Revenu Quebec Schedule F (TP-1.D.F-V, 2025-12), Part A, as the Quebec take-home manifest names
the form: its title, and that it exports line 70, the income subject to the contribution, which
Part B tests against $18,130. The form part has no steps of its own.
"""

from __future__ import annotations

from pathlib import Path

import yaml

import tax_engine.jurisdictions.ca_qc

PART = (
    Path(tax_engine.jurisdictions.ca_qc.__file__).parent
    / "manifests"
    / "2025"
    / "tp1_schedule_f.yaml"
)


def test_the_form_part_names_the_form_and_exports_line_70() -> None:
    part = yaml.safe_load(PART.read_text(encoding="utf-8"))

    assert part["form"]["name"] == "ca-qc/tp1_schedule_f"
    assert part["form"]["title"] == "Contribution to the Health Services Fund"
    assert part["form"]["exports"] == ["ca-qc/tp1_schedule_f_income_subject_line_70"]
    assert part["capabilities"] == []
