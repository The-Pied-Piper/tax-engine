"""The Newfoundland and Labrador form `ca-nl/nl428_credits` (Form NL428: Newfoundland and Labrador
Tax, lines 1 to 62) and the five kinds it exports: line 5, the bracket rate (the figure the return
summary reads for the marginal tax rate), line 8, Newfoundland and Labrador tax on taxable income
at the first bracket rate, line 12, the bracket rate of the next bracket, line 15, tax on taxable
income at that rate, and line 62, Newfoundland and Labrador non-refundable tax credits.

Form text (Form NL428, CRA 5001-C): "Line 62 and line 61500: Line 58 plus line 61 Enter this amount
on line 66." and "Line 63: ... from line 8 or 15", which is why lines 8 and 15 are exported beside
the bracket rates of lines 5 and 12.

The part file names the form and its exports; line parts carry the capabilities. The
Newfoundland and Labrador package is not yet listed in the bundled package list, so the part is
read as YAML and the kinds are taken from the Newfoundland and Labrador package list in
`support.py`, not from the engine.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import yaml

import tax_engine.jurisdictions.ca_nl
from tax_engine.domain.kinds import AmountKind
from tests.jurisdictions.ca_nl.support import newfoundland_kinds
from tests.kinds import non_negative

PART = (
    Path(tax_engine.jurisdictions.ca_nl.__file__).parent
    / "manifests"
    / "2025"
    / "nl428_credits.yaml"
)

EXPORTS = [
    "ca-nl/nl428_bracket_rate_line_5",
    "ca-nl/nl428_tax_on_taxable_income_line_8",
    "ca-nl/nl428_bracket_rate_line_12",
    "ca-nl/nl428_tax_on_taxable_income_line_15",
    "ca-nl/nl428_eligible_dependant_amount_line_23",
    "ca-nl/nl428_non_refundable_credits_line_62",
]


def _part() -> dict[str, Any]:
    part = yaml.safe_load(PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_form_is_named_titled_as_printed_and_required() -> None:
    form = _part()["form"]

    assert form["name"] == "ca-nl/nl428_credits"
    assert form["title"] == "Form NL428: Newfoundland and Labrador Tax"
    assert form["required"] is True


def test_the_form_exports_lines_5_8_12_15_23_and_62_in_order() -> None:
    assert _part()["form"]["exports"] == EXPORTS


def test_the_form_supplies_nothing_and_the_part_declares_no_capabilities() -> None:
    part = _part()

    assert "supplies" not in part["form"]
    assert "supplies" not in part
    assert part["capabilities"] == []


def test_the_part_keys_mirror_the_saskatchewan_and_alberta_credits_parts() -> None:
    part = _part()

    assert list(part["form"]) == ["name", "title", "reference", "required", "exports"]
    assert list(part) == ["form", "capabilities"]


@pytest.mark.parametrize("identifier", EXPORTS)
def test_each_export_is_a_registered_non_negative_amount_kind(identifier: str) -> None:
    kinds = newfoundland_kinds()

    assert identifier in kinds.identifiers()
    kind = kinds.kind(identifier)
    assert isinstance(kind, AmountKind)
    assert non_negative(kind)
