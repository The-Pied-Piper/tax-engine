"""The Nova Scotia form `ca-ns/ns428` (Form NS428: Nova Scotia Tax, lines 1 to 99).

The part file names the form; line parts carry the capabilities. The form is one form, so its lines
read each other directly and it exports nothing yet: line 99, the Nova Scotia tax for T1 line
42800, is exported by the ticket that builds it. The Nova Scotia package is not yet listed in the
bundled package list, so the part is read as YAML.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

import tax_engine.jurisdictions.ca_ns

PART = Path(tax_engine.jurisdictions.ca_ns.__file__).parent / "manifests" / "2025" / "ns428.yaml"


def _part() -> dict[str, Any]:
    part = yaml.safe_load(PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_form_is_named_titled_as_printed_and_required() -> None:
    form = _part()["form"]

    assert form["name"] == "ca-ns/ns428"
    assert form["title"] == "Form NS428: Nova Scotia Tax"
    assert form["required"] is True


def test_the_form_exports_nothing_yet_and_the_part_declares_no_capabilities() -> None:
    part = _part()

    assert part["form"]["exports"] == []
    assert "supplies" not in part["form"]
    assert part["capabilities"] == []


def test_the_part_keys_mirror_the_saskatchewan_and_newfoundland_parts() -> None:
    part = _part()

    assert list(part["form"]) == ["name", "title", "required", "exports"]
    assert list(part) == ["form", "capabilities"]
