"""The Manitoba take-home manifest asks the caller for the gross salary only.

The part `salary.yaml` declares the one input of T1 line 10100, employment income (owner ruling
14 Nov 2026: Manitoba has its own copy, as Ontario has `salary.yaml`). The Manitoba manifest cannot
be built until the Manitoba forms exist (T1 needs `ca/provincial_tax.amount`), so this test reads
the part. The end-to-end ticket lists Manitoba and can move these checks onto the built manifest.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

import tax_engine.jurisdictions

PART = (
    Path(tax_engine.jurisdictions.__file__).parent / "ca_mb" / "manifests" / "2025" / "salary.yaml"
)


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
