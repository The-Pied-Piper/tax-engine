"""AB428 (2025) line 51's input, as the Alberta take-home manifest part declares it.

Form text (Form AB428, CRA 5009-c-25e.txt in docs/cra-forms-2025): "Line 51 and line 58769: Line 49
plus line 50 =". The line prints no heading, so the declaration has no title. A salary-only caller
has no medical expenses, so a request that leaves the line out is read as blank.

The real part is loaded under a test-local header, as the take-home header is another part's. The
Alberta registries of `support.py` are used, as Alberta is not yet in the registrations.
"""

from __future__ import annotations

import shutil
from pathlib import Path

import tax_engine.jurisdictions.ca_ab
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.domain.manifest import Manifest
from tests.jurisdictions.ca_ab.support import alberta_kinds, alberta_packages, alberta_units

IDENTIFIER = "ca-ab/ab428_medical_expenses_line_51"
PRINTED_BASIS = "Line 51 and line 58769: Line 49 plus line 50"
PART = (
    Path(tax_engine.jurisdictions.ca_ab.__file__).parent
    / "manifests"
    / "2025"
    / "ab428_line_51_input.yaml"
)
HEADER = """\
jurisdiction: CA-AB
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
    source = YamlJurisdictionSource(alberta_packages().roots(), alberta_kinds(), alberta_units())
    return source.load(folder)


def test_a_request_that_leaves_out_line_51_is_read_as_blank(tmp_path: Path) -> None:
    declaration = _manifest(tmp_path).inputs[IDENTIFIER]
    default = declaration.default_artifact(alberta_kinds().kind(IDENTIFIER))
    assert not declaration.required
    assert declaration.basis == PRINTED_BASIS
    assert default is not None and default.is_blank


def test_line_51_is_declared_as_printed(tmp_path: Path) -> None:
    declaration = _manifest(tmp_path).inputs[IDENTIFIER]
    assert declaration.title is None
    assert declaration.reference == "51"
    assert declaration.unit == "ca/cad"
