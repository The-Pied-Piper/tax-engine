"""The Nova Scotia form `ca-ns/ns428` (Form NS428: Nova Scotia Tax, lines 1 to 99).

The part file names the form; line parts carry the capabilities. The form is one form, so its lines
read each other directly. It exports line 99, the Nova Scotia tax that line 99 says to enter on
line 42800 of the return, and supplies it as `ca/provincial_tax.amount`, the name the federal T1
reads. The Nova Scotia package is not yet listed in the bundled package list, so the part is read as
YAML.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

import tax_engine.jurisdictions.ca_ns

PART = Path(tax_engine.jurisdictions.ca_ns.__file__).parent / "manifests" / "2025" / "ns428.yaml"
LINE_99 = "ca-ns/ns428_nova_scotia_tax_line_99"


def _part() -> dict[str, Any]:
    part = yaml.safe_load(PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_form_is_named_titled_as_printed_and_required() -> None:
    form = _part()["form"]

    assert form["name"] == "ca-ns/ns428"
    assert form["title"] == "Form NS428: Nova Scotia Tax"
    assert form["required"] is True


def test_the_form_exports_line_99_and_supplies_it_as_the_provincial_tax() -> None:
    part = _part()

    assert part["form"]["exports"] == [LINE_99]
    assert part["form"]["supplies"] == {"ca/provincial_tax.amount": LINE_99}
    assert part["capabilities"] == []


def test_the_part_keys_mirror_the_saskatchewan_part() -> None:
    part = _part()

    assert list(part["form"]) == ["name", "title", "required", "exports", "supplies"]
    assert list(part) == ["form", "capabilities"]
