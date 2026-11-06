"""The Ontario take-home manifest's T2204 line 2 input: the self-employment earnings a salary-only
caller does not give.

T2204 line 2: "Total self-employment and other earnings eligible for the EI program for access to EI
special benefits". A salary-only caller has none, so a request that leaves the line out is read as
blank, and the line 1 part reads that blank as 0. The real part is loaded under a test-local header,
as the take-home header is another part's.
"""

from __future__ import annotations

import shutil
from pathlib import Path

import tax_engine.jurisdictions.ca_on
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.domain.manifest import Manifest
from tax_engine.registrations import JURISDICTIONS, artifact_kinds

LINE_2 = "ca/t2204_self_employment_earnings"
PRINTED_BASIS = (
    "Total self-employment and other earnings eligible for the EI program for access to EI "
    "special benefits"
)
PART = Path(tax_engine.jurisdictions.ca_on.__file__).parent / (
    "manifests/take_home/t2204_inputs.yaml"
)
HEADER = """\
jurisdiction: CA-ON
version: 1
valid_from_tax_year: 2025
outputs: [ca/t2204_line_1]
capabilities: []
"""


def _manifest(tmp_path: Path) -> Manifest:
    folder = tmp_path / "manifest"
    folder.mkdir()
    (folder / "header.yaml").write_text(HEADER)
    shutil.copy(PART, folder / PART.name)
    return YamlJurisdictionSource(JURISDICTIONS.roots(), artifact_kinds()).load(folder)


def test_a_request_that_leaves_out_the_self_employment_earnings_is_read_as_blank(
    tmp_path: Path,
) -> None:
    kinds = artifact_kinds()
    declaration = _manifest(tmp_path).inputs[LINE_2]
    default = declaration.default_artifact(kinds.kind(LINE_2))
    assert not declaration.required
    assert declaration.basis == PRINTED_BASIS
    assert default is not None and default.is_blank
