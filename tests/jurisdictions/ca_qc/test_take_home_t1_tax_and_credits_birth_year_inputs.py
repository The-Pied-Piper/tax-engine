"""5005-R (2025) year of birth input, as the Quebec take-home manifest part declares it: the filer's
year of birth, the federal count `ca/birth_year` (a shared fact), entered once on the T1 and
exported from there. A request that leaves it out is read as blank; the lines that depend on it
read that blank as 0.
"""

from __future__ import annotations

from typing import Any

import yaml

from tests.jurisdictions.ca_qc.conftest import QUEBEC_PARTS


def _part(name: str) -> dict[str, Any]:
    part = yaml.safe_load((QUEBEC_PARTS / name).read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_declares_only_the_birth_year_input() -> None:
    part = _part("t1_tax_and_credits_birth_year_inputs.yaml")

    assert list(part) == ["form", "inputs"]
    assert part["form"] == {"name": "ca-qc/t1_tax_and_credits"}
    assert part["inputs"] == [
        {
            "name": "ca/birth_year",
            "title": "Year of birth",
            "required": False,
            "default": None,
            "basis": "Line 79 and line 30100: if you were born in 1960 or earlier",
        }
    ]


def test_the_form_exports_the_birth_year() -> None:
    assert "ca/birth_year" in _part("t1_tax_and_credits.yaml")["form"]["exports"]
