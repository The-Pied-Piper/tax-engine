"""NL428 (2025) line 96's input, as the NL take-home manifest part declares it.

Form NL428 (CRA 5001-c-25e.txt, confirmed 2026-11-18), as printed on the form: "Line 96 and line
61880: Reduction for spouse or common-law partner Claim $557". The input is the eligibility claim,
a count: 1 means the reduction is claimed, 0 or blank means not claimed. A salary-only caller
leaves it out, so it is read as blank.

The real part is loaded under a test-local header over the Newfoundland and Labrador package list
of `support.py`.
"""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

import yaml

import tax_engine.jurisdictions.ca_nl
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.kinds import CountKind
from tax_engine.domain.manifest import Manifest
from tax_engine.jurisdictions.ca_nl.catalog import (
    NL428_REDUCTION_FOR_SPOUSE_OR_COMMON_LAW_PARTNER_CLAIMED_LINE_96,
)
from tests.jurisdictions.ca_nl.support import (
    newfoundland_kinds,
    newfoundland_packages,
    newfoundland_units,
)
from tests.kinds import non_negative

KIND = NL428_REDUCTION_FOR_SPOUSE_OR_COMMON_LAW_PARTNER_CLAIMED_LINE_96
IDENTIFIER = KIND.identifier
PRINTED_BASIS = "Line 96 and line 61880: Reduction for spouse or common-law partner Claim $557"
PART = Path(tax_engine.jurisdictions.ca_nl.__file__).parent / (
    "manifests/2025/nl428_line_96_input.yaml"
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


def test_the_part_declares_only_the_line_96_input_as_optional() -> None:
    part = _part()

    assert list(part) == ["inputs"]
    (declaration,) = part["inputs"]
    assert declaration["name"] == IDENTIFIER
    assert declaration["reference"] == "96"
    assert declaration["required"] is False
    assert declaration["default"] is None
    assert declaration["basis"] == PRINTED_BASIS
    assert "title" not in declaration


def test_the_claim_is_a_non_negative_count_kind() -> None:
    kind = newfoundland_kinds().kind(IDENTIFIER)

    assert IDENTIFIER == "ca-nl/nl428_reduction_for_spouse_or_common_law_partner_claimed_line_96"
    assert kind is KIND
    assert isinstance(kind, CountKind)
    assert non_negative(kind)


def test_a_request_that_leaves_out_the_claim_is_read_as_blank(tmp_path: Path) -> None:
    declaration = _manifest(tmp_path).inputs[IDENTIFIER]
    default = declaration.default_artifact(newfoundland_kinds().kind(IDENTIFIER))

    assert not declaration.required
    assert default is not None and default.is_blank


def test_a_claim_of_one_is_taken_as_given() -> None:
    assert Artifact(KIND, 1).value == 1
