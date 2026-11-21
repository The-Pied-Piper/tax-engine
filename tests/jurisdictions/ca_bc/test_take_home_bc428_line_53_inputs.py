"""BC428 (2025) line 53's input, as the British Columbia take-home manifest part declares it.

Form text (Form BC428, CRA 5010-C, read 2026-11-14):
"Line 53 and line 58769: Line 51 plus line 52 = ^". The line is a printed sum over the medical
expenses working (lines 46 to 52), which only exists for blank optional inputs; it is one optional
input, blank read as 0, as Alberta's line 51 is. A salary-only caller has no medical expenses, so
a request that leaves the line out is read as blank.

The real part is loaded under a test-local header, as the take-home header is another part's. The
British Columbia registries of `support.py` are used.
"""

from __future__ import annotations

import shutil
from pathlib import Path

import yaml

import tax_engine.jurisdictions.ca_bc
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.domain.manifest import Manifest
from tests.jurisdictions.ca_bc.support import (
    british_columbia_kinds,
    british_columbia_packages,
    british_columbia_units,
)

IDENTIFIER = "ca-bc/bc428_medical_expenses_line_53"
PRINTED_BASIS = "Line 53 and line 58769: Line 51 plus line 52"
PART = (
    Path(tax_engine.jurisdictions.ca_bc.__file__).parent
    / "manifests"
    / "2025"
    / "bc428_line_53_inputs.yaml"
)
HEADER = """\
jurisdiction: CA-BC
version: 1
valid_from_tax_year: 2025
outputs: [ca/total_income]
capabilities: []
"""


def _owner_form() -> str:
    """A declaration of the form the part names as owner of its inputs, exporting one input."""
    part = yaml.safe_load(PART.read_text(encoding="utf-8"))
    name = part["form"]["name"]
    export = part["inputs"][0]["name"]
    return f"form:\n  name: {name}\n  required: true\n  exports: [{export}]\ncapabilities: []\n"


def _manifest(tmp_path: Path) -> Manifest:
    folder = tmp_path / "manifest"
    folder.mkdir()
    (folder / "header.yaml").write_text(HEADER)
    (folder / "form.yaml").write_text(_owner_form())
    shutil.copy(PART, folder / PART.name)
    source = YamlJurisdictionSource(
        british_columbia_packages().roots(), british_columbia_kinds(), british_columbia_units()
    )
    return source.load(folder)


def test_a_request_that_leaves_out_line_53_is_read_as_blank(tmp_path: Path) -> None:
    declaration = _manifest(tmp_path).inputs[IDENTIFIER]
    default = declaration.default_artifact(british_columbia_kinds().kind(IDENTIFIER))
    assert not declaration.required
    assert declaration.basis == PRINTED_BASIS
    assert declaration.title is None
    assert declaration.reference == "53"
    assert declaration.unit == "ca/cad"
    assert default is not None and default.is_blank
