"""The four new ON428 (2025) line 36 inputs of `on428_line_36_inputs.yaml`.

Form text (CRA 5006-PC, section "Line 58689"): the Ontario maximums apply to "attendant care
expenses", "a van adapted for transporting a patient who requires the use of a wheelchair" and
"moving expenses for a patient's move to a more accessible dwelling", with a separate attendant care
figure "in the year of death". Each is an optional input, left out as blank (read as 0 by the steps
that read it).
"""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest
import yaml

import tax_engine.jurisdictions.ca_on
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.domain.kinds import AmountKind, CountKind
from tax_engine.domain.manifest import Manifest
from tax_engine.registrations import JURISDICTIONS, artifact_kinds, units
from tests.kinds import bundled_kinds, non_negative

PART = Path(tax_engine.jurisdictions.ca_on.__file__).parent / (
    "manifests/2025/on428_line_36_inputs.yaml"
)
HEADER = """\
jurisdiction: CA-ON
version: 1
valid_from_tax_year: 2025
outputs: [ca-on/on428_medical_expenses_line_36]
capabilities: []
"""
FORM = """\
form:
  name: ca-on/on428
  required: true
  exports:
    - ca-on/on428_medical_expenses_allowed_line_36
capabilities: []
"""
STEPS = PART.with_name("on428_line_36.yaml")
KINDS = [
    ("ca-on/on428_attendant_care_expenses_line_36", AmountKind),
    ("ca-on/on428_adapted_van_expenses_line_36", AmountKind),
    ("ca-on/on428_patient_move_expenses_line_36", AmountKind),
    ("ca-on/on428_year_of_death_line_36", CountKind),
]


def _manifest(tmp_path: Path) -> Manifest:
    folder = tmp_path / "manifest"
    folder.mkdir()
    (folder / "header.yaml").write_text(HEADER)
    (folder / "form.yaml").write_text(FORM)
    shutil.copy(PART, folder / PART.name)
    shutil.copy(STEPS, folder / STEPS.name)
    return YamlJurisdictionSource(JURISDICTIONS.roots(), artifact_kinds(), units()).load(folder)


@pytest.mark.parametrize(("identifier", "kind_type"), KINDS)
def test_each_category_input_is_an_optional_blank_non_negative_input(
    tmp_path: Path, identifier: str, kind_type: type
) -> None:
    kind = bundled_kinds().kind(identifier)
    declaration = _manifest(tmp_path).inputs[identifier]
    default = declaration.default_artifact(kind)

    assert isinstance(kind, kind_type)
    assert non_negative(kind)
    assert not declaration.required
    assert default is not None and default.is_blank


def test_the_part_declares_its_form_then_its_inputs() -> None:
    part = yaml.safe_load(PART.read_text())
    assert list(part) == ["form", "inputs"]
    assert part["form"] == {"name": "ca-on/on428"}
