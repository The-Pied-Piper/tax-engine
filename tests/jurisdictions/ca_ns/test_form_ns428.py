"""The Nova Scotia form `ca-ns/ns428` (Form NS428: Nova Scotia Tax, lines 1 to 99).

The part file names the form; line parts carry the capabilities. The form is one form, so its lines
read each other directly. It exports line 99, the Nova Scotia tax that line 99 says to enter on
line 42800 of the return, and supplies it as `ca/provincial_tax.amount`, the name the federal T1
reads. It also exports line 5 (the bracket rate) and lines 81 and 84 (the low-income tax reduction's
income over the base amount, and the reduction left) for the return summary's marginal rate. The
part is read as YAML.
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


def test_the_form_exports_what_the_return_reads_and_supplies_line_99_as_the_provincial_tax() -> (
    None
):
    part = _part()

    assert part["form"]["exports"] == [
        "ca-ns/ns428_bracket_rate_line_5",
        "ca-ns/ns428_line_81",
        "ca-ns/ns428_low_income_reduction_line_84",
        LINE_99,
    ]
    assert part["form"]["supplies"] == {"ca/provincial_tax.amount": LINE_99}
    assert part["capabilities"] == []


def test_the_part_keys_mirror_the_saskatchewan_part() -> None:
    part = _part()

    assert list(part["form"]) == ["name", "title", "required", "exports", "supplies"]
    assert list(part) == ["form", "capabilities"]
