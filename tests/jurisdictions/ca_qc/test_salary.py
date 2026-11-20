"""The Quebec take-home manifest asks the caller for the gross salary only.

The part `salary.yaml` declares the one input of T1 line 10100, employment income (owner ruling
14 Nov 2026: each province has its own copy, as Ontario has `salary.yaml`). Both returns take the
gross salary as their first income line (5005-R line 1 and TP-1 line 101). The Quebec manifest is
not complete until the later line tickets land, so this test reads the part. The end-to-end ticket
can move these checks onto the built manifest.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

import tax_engine.jurisdictions.ca_qc

FOLDER = Path(tax_engine.jurisdictions.ca_qc.__file__).parent / "manifests" / "2025"
PART = FOLDER / "salary.yaml"


def _inputs() -> list[dict[str, Any]]:
    part = yaml.safe_load(PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    assert list(part) == ["inputs"]
    return list(part["inputs"])


def test_the_salary_is_the_only_required_input() -> None:
    required = [declaration["name"] for declaration in _inputs() if declaration["required"]]

    assert required == ["ca/employment_income"]
    assert len(_inputs()) == 1


def test_the_salary_input_is_the_printed_employment_income_in_canadian_dollars() -> None:
    assert _inputs()[0] == {
        "name": "ca/employment_income",
        "title": "Employment income",
        "reference": "10100",
        "unit": "ca/cad",
        "required": True,
    }
    assert list(_inputs()[0]) == ["name", "title", "reference", "unit", "required"]
