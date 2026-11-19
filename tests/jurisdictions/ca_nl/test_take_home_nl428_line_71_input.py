"""NL428 (2025) line 71's input, as the Newfoundland and Labrador take-home manifest part declares.

Form text (Form NL428, CRA 5001-C): "Line 71: Amount from line 14 of Part 7 of Form T691 multiplied
by 60% =". Form T691 is not built, so the amount from its line 14 is taken as an input, as the form
takes it, and a request that leaves the line out is read as blank. The amount is non-negative: a
claim cannot be below nothing, and the form prints no floor or maximum on the line.

The real part is loaded under a test-local header, as the take-home header is another part's.
Newfoundland and Labrador is not yet listed in the registrations, so the source is built over the
Newfoundland and Labrador package list of `support.py`.
"""

from __future__ import annotations

import shutil
from decimal import Decimal
from pathlib import Path
from typing import Any

import yaml

import tax_engine.jurisdictions.ca_nl
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.manifest import Manifest
from tax_engine.jurisdictions.ca_nl.catalog import NL428_T691_AMOUNT_LINE_71
from tests.jurisdictions.ca_nl.support import (
    newfoundland_kinds,
    newfoundland_packages,
    newfoundland_units,
)
from tests.kinds import non_negative

KIND = NL428_T691_AMOUNT_LINE_71
IDENTIFIER = KIND.identifier
PRINTED_BASIS = "Line 71: Amount from line 14 of Part 7 of Form T691"
PART = Path(tax_engine.jurisdictions.ca_nl.__file__).parent / (
    "manifests/2025/nl428_line_71_input.yaml"
)
HEADER = """\
jurisdiction: CA-NL
version: 1
valid_from_tax_year: 2025
outputs: [ca/total_income]
capabilities: []
"""


def _manifest(tmp_path: Path) -> Manifest:
    folder = tmp_path / "manifest"
    folder.mkdir()
    (folder / "header.yaml").write_text(HEADER)
    shutil.copy(PART, folder / PART.name)
    source = YamlJurisdictionSource(
        newfoundland_packages().roots(), newfoundland_kinds(), newfoundland_units()
    )
    return source.load(folder)


def _part() -> dict[str, Any]:
    part = yaml.safe_load(PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_a_request_that_leaves_out_line_71_is_read_as_blank(tmp_path: Path) -> None:
    kinds = newfoundland_kinds()
    declaration = _manifest(tmp_path).inputs[IDENTIFIER]
    default = declaration.default_artifact(kinds.kind(IDENTIFIER))
    assert not declaration.required
    assert declaration.basis == PRINTED_BASIS
    assert default is not None and default.is_blank


def test_the_t691_amount_line_71_is_a_non_negative_amount_kind() -> None:
    kind = newfoundland_kinds().kind(IDENTIFIER)

    assert IDENTIFIER == "ca-nl/nl428_t691_amount_line_71"
    assert kind is KIND
    assert isinstance(kind, AmountKind)
    assert non_negative(kind)
    assert Artifact(kind, Decimal("1234.56")) is not None


def test_the_part_declares_the_input_with_its_unit_reference_and_title() -> None:
    part = _part()

    assert list(part) == ["inputs"]
    assert part["inputs"] == [
        {
            "name": IDENTIFIER,
            "title": "Amount from line 14 of Part 7 of Form T691",
            "reference": "71 (Form T691)",
            "unit": "ca/cad",
            "required": False,
            "default": None,
            "basis": PRINTED_BASIS,
        }
    ]
