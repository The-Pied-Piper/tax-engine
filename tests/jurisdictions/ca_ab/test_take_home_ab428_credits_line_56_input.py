"""AB428 (2025) line 56 box A's input, as the Alberta take-home manifest part declares it.

Form text (Form AB428, CRA 5009-c-25e.txt): "Line 56: Amount from line 14 of your federal
Schedule 9". A salary-only caller has none, so a request that leaves the line out is read as
blank. The real part is loaded under a test-local header, as the take-home header is another
part's.
"""

from __future__ import annotations

import shutil
from pathlib import Path

import tax_engine.jurisdictions.ca_ab
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.domain.manifest import Manifest
from tests.jurisdictions.ca_ab.support import alberta_kinds, alberta_packages, alberta_units

IDENTIFIER = "ca-ab/ab428_donations_amount_line_56"
PRINTED_BASIS = "Line 56: Amount from line 14 of your federal Schedule 9"
PART = (
    Path(tax_engine.jurisdictions.ca_ab.__file__).parent
    / "manifests"
    / "2025"
    / "ab428_credits_line_56_input.yaml"
)
HEADER = """\
jurisdiction: CA-AB
version: 1
valid_from_tax_year: 2025
outputs: [ca/total_income]
capabilities: []
"""

FORM = """\
form:
  name: ca-ab/ab428_credits
  required: true
  exports:
    - ca/total_income
capabilities: []
"""


def _manifest(tmp_path: Path) -> Manifest:
    folder = tmp_path / "manifest"
    folder.mkdir()
    (folder / "header.yaml").write_text(HEADER)
    shutil.copy(PART, folder / PART.name)
    (folder / "form.yaml").write_text(FORM)
    source = YamlJurisdictionSource(alberta_packages().roots(), alberta_kinds(), alberta_units())
    return source.load(folder)


def test_the_part_declares_the_one_optional_input_as_printed(tmp_path: Path) -> None:
    manifest = _manifest(tmp_path)

    assert list(manifest.inputs) == [IDENTIFIER]
    declaration = manifest.inputs[IDENTIFIER]
    assert not declaration.required
    assert declaration.basis == PRINTED_BASIS
    assert declaration.title == "Amount from line 14 of your federal Schedule 9"
    assert declaration.reference == "56 box A"
    assert declaration.unit == "ca/cad"


def test_a_request_that_leaves_the_line_out_is_read_as_blank(tmp_path: Path) -> None:
    declaration = _manifest(tmp_path).inputs[IDENTIFIER]
    default = declaration.default_artifact(alberta_kinds().kind(IDENTIFIER))

    assert default is not None and default.is_blank
