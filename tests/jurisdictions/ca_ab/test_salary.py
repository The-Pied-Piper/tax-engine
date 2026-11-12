"""The Alberta salary input: the one input a take-home caller gives.

Form text (T1 line 10100, employment income; owner ruling 12 Nov 2026: Alberta has its own copy of
the salary part, as Ontario has `salary.yaml`). The part declares `ca/employment_income`, titled
"Employment income", reference 10100, in Canadian dollars, required.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

import tax_engine.jurisdictions.ca_ab

PART = Path(tax_engine.jurisdictions.ca_ab.__file__).parent / "manifests" / "2025" / "salary.yaml"


def _part() -> dict[str, Any]:
    part = yaml.safe_load(PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_declares_only_the_salary_input() -> None:
    assert list(_part()) == ["inputs"]
    assert len(_part()["inputs"]) == 1


def test_the_salary_input_is_the_required_employment_income() -> None:
    assert _part()["inputs"][0] == {
        "name": "ca/employment_income",
        "title": "Employment income",
        "reference": "10100",
        "unit": "ca/cad",
        "required": True,
    }


def test_the_input_keys_are_in_the_manifest_order() -> None:
    assert list(_part()["inputs"][0]) == ["name", "title", "reference", "unit", "required"]


def test_the_part_is_the_same_as_the_ontario_salary_part() -> None:
    ontario = PART.parents[3] / "ca_on" / "manifests" / "2025" / "salary.yaml"

    assert yaml.safe_load(ontario.read_text(encoding="utf-8")) == _part()
