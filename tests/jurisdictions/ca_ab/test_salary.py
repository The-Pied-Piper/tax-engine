"""The Alberta take-home manifest asks the caller for the gross salary and for nothing else.

The part `salary.yaml` declares the one input of T1 line 10100, employment income (owner ruling
12 Nov 2026: Alberta has its own copy, as Ontario has `salary.yaml`). Ontario's counterpart test
reads the built manifest; the Alberta manifest cannot be built until the AB428 forms exist
(T1 needs `ca/provincial_tax.amount`), so this test reads the part. The end-to-end ticket lists
Alberta and can move these checks onto the built manifest.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

import tax_engine.jurisdictions.ca_ab

PART = Path(tax_engine.jurisdictions.ca_ab.__file__).parent / "manifests" / "2025" / "salary.yaml"


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
