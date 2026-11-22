"""The Schedule B line 12 input (2025), as the Quebec take-home manifest part declares it.

Revenu Quebec TP-1.D.B-V (2025-12), Schedule B, Part A, line 12: "Amount from line 275 of your
spouse's return (spouse on December 31, 2025)". The take-home leaves the spouse lines out, so the
amount is an optional input; a request that leaves it out is read as blank, and line 14 reads the
blank as 0 (owner decision on the ticket, 19 Nov 2026).
"""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

import yaml

import tax_engine.jurisdictions.ca_qc
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.manifest import Manifest
from tax_engine.jurisdictions.ca_qc.catalog import SCHEDULE_B_LINE_12
from tests.jurisdictions.ca_qc.support import quebec_kinds, quebec_packages, quebec_units
from tests.kinds import non_negative
from tests.manifest_support import input_named

IDENTIFIER = SCHEDULE_B_LINE_12.identifier
PRINTED_BASIS = "Amount from line 275 of your spouse's return (spouse on December 31, 2025)"
PART = Path(tax_engine.jurisdictions.ca_qc.__file__).parent / (
    "manifests/2025/schedule_b_line_12_input.yaml"
)
HEADER = """\
jurisdiction: CA-QC
version: 1
valid_from_tax_year: 2025
outputs: []
capabilities: []
"""
FORM = """\
form:
  name: ca-qc/schedule_b
  required: true
  exports:
    - ca-qc/schedule_b_line_12
capabilities: []
"""


def _manifest(tmp_path: Path) -> Manifest:
    folder = tmp_path / "manifest"
    folder.mkdir()
    (folder / "00_header.yaml").write_text(HEADER)
    (folder / "01_form.yaml").write_text(FORM)
    shutil.copy(PART, folder / PART.name)
    source = YamlJurisdictionSource(quebec_packages().roots(), quebec_kinds(), quebec_units())
    return source.load(folder)


def _part() -> dict[str, Any]:
    part = yaml.safe_load(PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_declares_only_the_line_12_input_as_optional() -> None:
    part = _part()

    assert list(part) == ["form", "inputs"]
    assert part["form"] == {"name": "ca-qc/schedule_b"}
    (declaration,) = part["inputs"]
    assert declaration == {
        "name": IDENTIFIER,
        "title": "Amount from line 275 of your spouse's return",
        "reference": "12",
        "unit": "ca/cad",
        "required": False,
        "default": None,
        "basis": PRINTED_BASIS,
    }


def test_the_amount_is_a_registered_non_negative_amount() -> None:
    kind = quebec_kinds().kind(IDENTIFIER)

    assert IDENTIFIER == "ca-qc/schedule_b_line_12"
    assert kind is SCHEDULE_B_LINE_12
    assert isinstance(kind, AmountKind)
    assert non_negative(kind)


def test_a_request_that_leaves_out_the_amount_is_read_as_blank(tmp_path: Path) -> None:
    declaration = input_named(_manifest(tmp_path), IDENTIFIER)
    default = declaration.default_artifact(quebec_kinds().kind(IDENTIFIER))

    assert not declaration.required
    assert default is not None and default.is_blank
