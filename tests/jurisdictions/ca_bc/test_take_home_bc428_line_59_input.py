"""BC428 (2025) line 59's input, as the British Columbia take-home manifest part declares it.

Form text (Form BC428, CRA 5010-C, docs/cra-forms-2025): "Line 59 and line 58980: Amount of
qualifying gifts also claimed on line 57". A caller with no such gifts has nothing to enter, so a
request that leaves the line out is read as blank.

British Columbia is not yet listed in the registrations, so the real part is loaded under a
test-local header over the British Columbia package list of `support.py`.
"""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

import yaml

import tax_engine.jurisdictions.ca_bc
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.domain.manifest import Manifest
from tax_engine.jurisdictions.ca_bc.catalog import BC428_QUALIFYING_GIFTS_LINE_59
from tests.jurisdictions.ca_bc.support import (
    british_columbia_kinds,
    british_columbia_packages,
    british_columbia_units,
)
from tests.kinds import non_negative

IDENTIFIER = BC428_QUALIFYING_GIFTS_LINE_59.identifier
PRINTED_BASIS = "Line 59 and line 58980: Amount of qualifying gifts also claimed on line 57"
PART = Path(tax_engine.jurisdictions.ca_bc.__file__).parent / (
    "manifests/2025/bc428_line_59_input.yaml"
)
HEADER = """\
jurisdiction: CA-BC
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
        british_columbia_packages().roots(), british_columbia_kinds(), british_columbia_units()
    )
    return source.load(folder)


def _part() -> dict[str, Any]:
    part = yaml.safe_load(PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_declares_only_the_line_59_input() -> None:
    part = _part()

    assert list(part) == ["inputs"]
    assert part["inputs"] == [
        {
            "name": IDENTIFIER,
            "title": "Amount of qualifying gifts also claimed on line 57",
            "reference": "59",
            "unit": "ca/cad",
            "required": False,
            "default": None,
            "basis": PRINTED_BASIS,
        }
    ]
    assert list(part["inputs"][0]) == [
        "name",
        "title",
        "reference",
        "unit",
        "required",
        "default",
        "basis",
    ]


def test_the_qualifying_gifts_line_59_is_a_non_negative_amount_kind() -> None:
    kind = british_columbia_kinds().kind(IDENTIFIER)

    assert IDENTIFIER == "ca-bc/bc428_qualifying_gifts_line_59"
    assert kind is BC428_QUALIFYING_GIFTS_LINE_59
    assert non_negative(kind)


def test_a_request_that_leaves_out_line_59_is_read_as_blank(tmp_path: Path) -> None:
    declaration = _manifest(tmp_path).inputs[IDENTIFIER]
    default = declaration.default_artifact(british_columbia_kinds().kind(IDENTIFIER))

    assert not declaration.required
    assert declaration.basis == PRINTED_BASIS
    assert default is not None and default.is_blank
