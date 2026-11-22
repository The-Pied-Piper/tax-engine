"""The Schedule K line 50 input (2025), as the Quebec take-home manifest part declares it.

Revenu Quebec TP-1.D.K-V (2025-12), Schedule K, Part B, section 1, line 50: "You were covered by
basic prescription drug insurance provided by a group insurance plan (see line 447 in the guide) of
which you, your spouse, your father or your mother was a member, and this plan covered the cost of
medications". The answer is an optional input, a count of 1 for yes and 0 for no. A request that
leaves it out is read as 0, not covered (owner ruling, 19 Nov 2026).

The real part is loaded under a test-local header and form declaration over the Quebec package list
of `support.py`.
"""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

import yaml

import tax_engine.jurisdictions.ca_qc
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.domain.kinds import CountKind
from tax_engine.domain.manifest import Manifest
from tax_engine.jurisdictions.ca_qc.catalog import SCHEDULE_K_GROUP_PLAN_COVERED_LINE_50
from tests.jurisdictions.ca_qc.support import quebec_kinds, quebec_packages, quebec_units
from tests.kinds import non_negative
from tests.manifest_support import input_named

IDENTIFIER = SCHEDULE_K_GROUP_PLAN_COVERED_LINE_50.identifier
PRINTED_BASIS = "Covered by basic prescription drug insurance provided by a group insurance plan"
PART = Path(tax_engine.jurisdictions.ca_qc.__file__).parent / (
    "manifests/2025/tp1_schedule_k_line_50_input.yaml"
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
  name: ca-qc/tp1_schedule_k
  required: true
  exports:
    - ca-qc/schedule_k_group_plan_covered_line_50
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


def test_the_part_declares_only_the_line_50_input_as_optional() -> None:
    part = _part()

    assert list(part) == ["form", "inputs"]
    assert part["form"] == {"name": "ca-qc/tp1_schedule_k"}
    (declaration,) = part["inputs"]
    assert declaration == {
        "name": "ca-qc/schedule_k_group_plan_covered_line_50",
        "title": (
            "You were covered by basic prescription drug insurance provided by a group "
            "insurance plan "
            "of which you, your spouse, your father or your mother was a member, "
            "and this plan covered the cost of medications"
        ),
        "reference": "50",
        "required": False,
        "default": "0",
        "basis": PRINTED_BASIS,
    }


def test_the_answer_is_a_registered_non_negative_count() -> None:
    kind = quebec_kinds().kind(IDENTIFIER)

    assert IDENTIFIER == "ca-qc/schedule_k_group_plan_covered_line_50"
    assert kind is SCHEDULE_K_GROUP_PLAN_COVERED_LINE_50
    assert isinstance(kind, CountKind)
    assert kind.value_type is int
    assert non_negative(kind)


def test_a_request_that_leaves_out_the_answer_is_read_as_0(tmp_path: Path) -> None:
    declaration = input_named(_manifest(tmp_path), IDENTIFIER)
    default = declaration.default_artifact(quebec_kinds().kind(IDENTIFIER))

    assert not declaration.required
    assert default is not None and not default.is_blank
    assert default.value == 0
