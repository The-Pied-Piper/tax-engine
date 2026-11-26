"""The Prince Edward Island form `ca-pe/pe428` (Form PE428, CRA 5002-C) as declared so far: its
name, its title as printed, and the one export the lines after it read, line 8, the Prince Edward
Island tax on taxable income (line 55 is a copy of line 8 and has no step).

The part file names the form and its exports; line parts carry the capabilities. The Prince Edward
Island package is not yet listed, so the part is read as YAML and composed here with the real line
parts, and the kinds come from the Prince Edward Island package list in `support.py`.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest
import yaml

from tax_engine.domain.kinds import AmountKind
from tests.jurisdictions.ca_pe import pe428_support as s
from tests.jurisdictions.ca_pe.support import prince_edward_island_kinds
from tests.kinds import non_negative

D = Decimal
PART = s.PE_PARTS / "pe428.yaml"
EXPORTS = [s.LINE_8]
ALL_LINES = (1, 3, 4, 5, 6, 7, 8)


def _part() -> dict[str, Any]:
    part = yaml.safe_load(PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_form_is_named_titled_as_printed_and_required() -> None:
    form = _part()["form"]

    assert form["name"] == s.FORM_NAME
    assert form["title"] == "Form PE428: Prince Edward Island Tax and Credits"
    assert form["required"] is True


def test_the_form_exports_line_8() -> None:
    assert _part()["form"]["exports"] == EXPORTS


def test_the_form_supplies_nothing_and_the_part_declares_no_capabilities() -> None:
    part = _part()

    assert "supplies" not in part["form"]
    assert list(part["form"]) == ["name", "title", "required", "exports"]
    assert list(part) == ["form", "capabilities"]
    assert part["capabilities"] == []


@pytest.mark.parametrize("identifier", EXPORTS)
def test_each_export_is_a_registered_non_negative_amount_kind(identifier: str) -> None:
    kinds = prince_edward_island_kinds()

    assert identifier in kinds.identifiers()
    kind = kinds.kind(identifier)
    assert isinstance(kind, AmountKind)
    assert non_negative(kind)


@pytest.mark.parametrize(
    ("salary", "expected"),
    [("20000", "1884.33"), ("30000", "2824.83"), ("70000", "8162.75")],
)
def test_the_real_form_part_and_line_parts_compose_to_the_tax_on_taxable_income(
    tmp_path: Path, salary: str, expected: str
) -> None:
    sheet = s.sheet(tmp_path, salary, ALL_LINES, tuple(EXPORTS), form_part=PART)

    assert sheet.get(s.kind(s.LINE_8)).value == D(expected)
