"""The Prince Edward Island form `ca-pe/pe428_credits` (Form PE428, lines 9 to 54).

The part file names the form; line parts carry the capabilities. Prince Edward Island is not yet
listed, so the part is read as YAML.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

import tax_engine.jurisdictions.ca_pe

PART = (
    Path(tax_engine.jurisdictions.ca_pe.__file__).parent
    / "manifests"
    / "2025"
    / "pe428_credits.yaml"
)


def _part() -> dict[str, Any]:
    part = yaml.safe_load(PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_form_is_named_titled_as_printed_and_required() -> None:
    form = _part()["form"]

    assert form["name"] == "ca-pe/pe428_credits"
    assert form["title"] == "Form PE428: Prince Edward Island Tax"
    assert form["required"] is True


def test_the_form_exports_nothing_yet_and_the_part_declares_no_capabilities() -> None:
    part = _part()

    assert part["form"]["exports"] == []
    assert "supplies" not in part["form"]
    assert part["capabilities"] == []


def test_the_part_keys_mirror_the_alberta_ab428_credits_part() -> None:
    part = _part()

    assert list(part["form"]) == ["name", "title", "required", "exports"]
    assert list(part) == ["form", "capabilities"]
