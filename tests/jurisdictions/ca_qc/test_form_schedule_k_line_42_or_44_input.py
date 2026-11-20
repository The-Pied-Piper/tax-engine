"""The Schedule K line 42 or 44 input (2025), as the Quebec take-home manifest part declares it.

Revenu Quebec TP-1.D.K-V (2025-12), Schedule K, Part A, line 46: "Add line 41 and, as applicable,
line 42 or line 44". Lines 42 and 44 are the dependent child amounts, printed as alternatives. They
are left out of the take-home (owner ruling, 19 Nov 2026), so they are one optional input, left
blank by a salary-only caller; line 46 reads the blank as 0.

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
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.manifest import Manifest
from tax_engine.jurisdictions.ca_qc.catalog import (
    SCHEDULE_K_DEPENDENT_CHILD_AMOUNT_LINE_42_OR_44,
)
from tests.jurisdictions.ca_qc.support import quebec_kinds, quebec_packages, quebec_units
from tests.kinds import non_negative

IDENTIFIER = SCHEDULE_K_DEPENDENT_CHILD_AMOUNT_LINE_42_OR_44.identifier
PRINTED_BASIS = "Add line 41 and, as applicable, line 42 or line 44."
PART = Path(tax_engine.jurisdictions.ca_qc.__file__).parent / (
    "manifests/2025/tp1_schedule_k_line_42_or_44_input.yaml"
)
HEADER = """\
jurisdiction: CA-QC
version: 1
valid_from_tax_year: 2025
inputs:
  - name: ca/employment_income
    required: true
outputs:
  - ca/employment_income
capabilities: []
"""
FORM = """\
form:
  name: ca-qc/tp1_schedule_k
  required: true
  exports:
    - ca-qc/schedule_k_dependent_child_amount_line_42_or_44
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


def test_the_part_declares_only_the_line_42_or_44_input_as_optional() -> None:
    part = _part()

    assert list(part) == ["form", "inputs"]
    assert part["form"] == {"name": "ca-qc/tp1_schedule_k"}
    (declaration,) = part["inputs"]
    assert declaration == {
        "name": IDENTIFIER,
        "reference": "42 or 44",
        "unit": "ca/cad",
        "required": False,
        "default": None,
        "basis": PRINTED_BASIS,
    }


def test_the_amount_is_a_registered_non_negative_decimal_amount() -> None:
    kind = quebec_kinds().kind(IDENTIFIER)

    assert IDENTIFIER == "ca-qc/schedule_k_dependent_child_amount_line_42_or_44"
    assert kind is SCHEDULE_K_DEPENDENT_CHILD_AMOUNT_LINE_42_OR_44
    assert isinstance(kind, AmountKind)
    assert non_negative(kind)


def test_a_request_that_leaves_out_the_amount_is_left_blank(tmp_path: Path) -> None:
    declaration = _manifest(tmp_path).inputs[IDENTIFIER]
    default = declaration.default_artifact(quebec_kinds().kind(IDENTIFIER))

    assert not declaration.required
    assert default is not None and default.is_blank
