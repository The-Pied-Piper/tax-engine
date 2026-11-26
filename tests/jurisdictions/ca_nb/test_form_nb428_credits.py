"""The New Brunswick form `ca-nb/nb428_credits` (Form NB428: New Brunswick Tax, lines 9 to 53).

The part file names the form; line parts carry the capabilities. The form's lines read each other
directly. It exports line 26, the credit amounts subtotal, so that the part composes; the ticket
that builds lines 27 to 53 replaces that export with line 53, the New Brunswick non-refundable
credits. The part is read as YAML.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

import tax_engine.jurisdictions.ca_nb

PART = (
    Path(tax_engine.jurisdictions.ca_nb.__file__).parent
    / "manifests"
    / "2025"
    / "nb428_credits.yaml"
)


def _part() -> dict[str, Any]:
    part = yaml.safe_load(PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_form_is_named_titled_as_printed_and_required() -> None:
    form = _part()["form"]

    assert form["name"] == "ca-nb/nb428_credits"
    assert form["title"] == "Form NB428: New Brunswick Tax"
    assert form["required"] is True


def test_the_form_exports_and_the_part_declares_no_capabilities() -> None:
    part = _part()

    assert part["form"]["exports"] == [
        "ca-nb/nb428_credits_subtotal_line_18",
        "ca-nb/nb428_cpp_contributions_line_19",
    ]
    assert "supplies" not in part["form"]
    assert part["capabilities"] == []


def test_the_part_keys_mirror_the_saskatchewan_and_newfoundland_parts() -> None:
    part = _part()

    assert list(part["form"]) == ["name", "title", "required", "exports"]
    assert list(part) == ["form", "capabilities"]
