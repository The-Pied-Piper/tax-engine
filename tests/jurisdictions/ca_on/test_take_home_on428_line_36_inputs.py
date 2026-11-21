"""ON428 (2025) line 36's inputs, as the Ontario take-home manifest part declares them.

Form text (ON428, CRA 5006-c-25e.txt): "Line 36 and line 58689: See line 58689 at canada.ca/on-
tax-info for maximum allowable amounts for attendant care, an adapted van, and moving expenses". A
request that leaves the line out is read as blank, and the step that reads it reads that blank as
0.

CRA 5006-PC (section "Line 58689"): "If the amount you claimed for medical expenses on your return
includes an amount for attendant care expenses that was limited to $10,000 ($20,000 in the year of
death), the maximum Ontario claim for attendant care expenses is $17,627 ($35,253 in the year of
death)". Five more inputs are optional and read as blank when left out: the attendant care expenses
paid, a 0/1 answer that the federal claim was limited, the van, the move, and a 0/1 year of death.

The real part is loaded under a test-local header, as the take-home header is another part's.
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
from tax_engine.jurisdictions.ca_on.catalog import ON428_MEDICAL_EXPENSES_LINE_36
from tax_engine.registrations import JURISDICTIONS, artifact_kinds, units
from tests.kinds import non_negative

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
CATEGORY_INPUTS = [
    ("ca-on/on428_attendant_care_expenses_line_36", AmountKind),
    ("ca-on/on428_attendant_care_federal_limit_applied_line_36", CountKind),
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


def test_a_request_that_leaves_out_line_36_is_read_as_blank(tmp_path: Path) -> None:
    kinds = artifact_kinds()
    identifier = ON428_MEDICAL_EXPENSES_LINE_36.identifier
    declaration = _manifest(tmp_path).inputs[identifier]
    default = declaration.default_artifact(kinds.kind(identifier))
    assert not declaration.required
    assert declaration.basis == PRINTED_BASIS
    assert default is not None and default.is_blank


@pytest.mark.parametrize(("identifier", "kind_type"), CATEGORY_INPUTS)
def test_each_category_input_is_an_optional_blank_non_negative_input(
    tmp_path: Path, identifier: str, kind_type: type
) -> None:
    kind = artifact_kinds().kind(identifier)
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
