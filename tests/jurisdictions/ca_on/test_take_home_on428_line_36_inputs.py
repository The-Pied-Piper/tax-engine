"""ON428 (2025) line 36's input, as the Ontario take-home manifest part declares it.

Form text (ON428, CRA 5006-c-25e.txt): "Line 36 and line 58689: See line 58689 at canada.ca/on-
tax-info for maximum allowable amounts for attendant care, an adapted van, and moving expenses". A
request that leaves the line out is read as blank, and the step that reads it reads that blank as
0.

The real part is loaded under a test-local header, as the take-home header is another part's.
"""

from __future__ import annotations

import shutil
from pathlib import Path

import yaml

import tax_engine.jurisdictions.ca_on
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.domain.manifest import Manifest
from tax_engine.jurisdictions.ca_on.catalog import ON428_MEDICAL_EXPENSES_LINE_36
from tax_engine.registrations import JURISDICTIONS, artifact_kinds, units

PRINTED_BASIS = (
    "Line 36 and line 58689: See line 58689 at canada.ca/on-tax-i"
    "nfo for maximum allowable amounts for attendant care, an adapted van, and moving expenses"
)
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


def _manifest(tmp_path: Path) -> Manifest:
    folder = tmp_path / "manifest"
    folder.mkdir()
    (folder / "header.yaml").write_text(HEADER)
    (folder / "form.yaml").write_text(FORM)
    shutil.copy(PART, folder / PART.name)
    shutil.copy(STEPS, folder / STEPS.name)
    return YamlJurisdictionSource(JURISDICTIONS.roots(), artifact_kinds(), units()).load(folder)


def test_a_request_that_leaves_out_line_36_is_read_as_blank(tmp_path: Path) -> None:
    kinds = artifact_kinds()
    identifier = ON428_MEDICAL_EXPENSES_LINE_36.identifier
    declaration = _manifest(tmp_path).inputs[identifier]
    default = declaration.default_artifact(kinds.kind(identifier))
    assert not declaration.required
    assert declaration.basis == PRINTED_BASIS
    assert default is not None and default.is_blank


def test_the_part_declares_its_form_then_its_inputs() -> None:
    part = yaml.safe_load(PART.read_text())
    assert list(part) == ["form", "inputs"]
    assert part["form"] == {"name": "ca-on/on428"}
