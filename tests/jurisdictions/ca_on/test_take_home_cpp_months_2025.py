"""The Ontario take-home manifest's Schedule 8 line A: the months CPP applied.

Schedule 8 (form 5000-S8), Part 2: "Enter "12" on line A below unless any of the following
conditions apply". A salary-only caller meets none of conditions a) to h), so a request that
leaves the months out is read as 12, which `amount_by_count` needs (it refuses a blank count).
The real part is loaded under a test-local header, as the take-home header is another part's.
"""

from __future__ import annotations

import shutil
from pathlib import Path

import tax_engine.jurisdictions.ca_on
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.domain.manifest import Manifest
from tax_engine.registrations import JURISDICTIONS, artifact_kinds

LINE_A = "ca/cpp_months"
PRINTED_BASIS = 'Enter "12" on line A below unless any of the following conditions apply:'
PART = Path(tax_engine.jurisdictions.ca_on.__file__).parent / (
    "manifests/take_home/schedule_8_inputs.yaml"
)
HEADER = """\
jurisdiction: CA-ON
version: 1
valid_from_tax_year: 2025
outputs: [ca/cpp_months]
capabilities: []
"""


def _manifest(tmp_path: Path) -> Manifest:
    folder = tmp_path / "manifest"
    folder.mkdir()
    (folder / "header.yaml").write_text(HEADER)
    shutil.copy(PART, folder / PART.name)
    return YamlJurisdictionSource(JURISDICTIONS.roots(), artifact_kinds()).load(folder)


def test_a_request_that_leaves_out_the_months_is_read_as_twelve(tmp_path: Path) -> None:
    kinds = artifact_kinds()
    declaration = _manifest(tmp_path).inputs[LINE_A]
    default = declaration.default_artifact(kinds.kind(LINE_A))
    assert not declaration.required
    assert declaration.basis == PRINTED_BASIS
    assert default is not None and default.value == 12
