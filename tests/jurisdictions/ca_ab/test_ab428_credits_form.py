"""The Alberta form `ca-ab/ab428_credits` (Form AB428, lines 1 to 58) and the five kinds it exports.

The part file names the form and its exports; line parts carry the capabilities. The Alberta
manifest is partial and Alberta is not yet listed, so the part is read as YAML and the kinds are
taken from the Alberta package list in `support.py`, not from the engine.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import yaml

import tax_engine.jurisdictions.ca_ab
from tax_engine.domain.kinds import AmountKind
from tests.jurisdictions.ca_ab.support import alberta_kinds
from tests.kinds import non_negative

PART = (
    Path(tax_engine.jurisdictions.ca_ab.__file__).parent
    / "manifests"
    / "2025"
    / "ab428_credits.yaml"
)

EXPORTS = [
    "ca-ab/ab428_tax_on_taxable_income_line_8",
    "ca-ab/ab428_tax_on_taxable_income_line_15",
    "ca-ab/ab428_unused_tuition_line_41",
    "ca-ab/ab428_credits_total_line_52",
    "ca-ab/ab428_non_refundable_credits_line_58",
]


def _part() -> dict[str, Any]:
    part = yaml.safe_load(PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_form_is_named_titled_as_printed_and_required() -> None:
    form = _part()["form"]

    assert form["name"] == "ca-ab/ab428_credits"
    assert form["title"] == "Form AB428: Alberta Tax and Credits"
    assert form["required"] is True


def test_the_form_exports_the_five_lines_other_forms_read_in_order() -> None:
    assert _part()["form"]["exports"] == EXPORTS


def test_the_form_supplies_nothing_and_the_part_declares_no_capabilities() -> None:
    part = _part()

    assert "supplies" not in part["form"]
    assert "supplies" not in part
    assert part["capabilities"] == []


def test_the_part_keys_mirror_the_ontario_on428_part() -> None:
    part = _part()

    assert list(part["form"]) == ["name", "title", "required", "exports"]
    assert list(part) == ["form", "capabilities"]


@pytest.mark.parametrize("identifier", EXPORTS)
def test_each_export_is_a_registered_non_negative_amount_kind(identifier: str) -> None:
    kinds = alberta_kinds()

    assert identifier in kinds.identifiers()
    kind = kinds.kind(identifier)
    assert isinstance(kind, AmountKind)
    assert non_negative(kind)
