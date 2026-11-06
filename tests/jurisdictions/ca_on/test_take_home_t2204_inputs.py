"""The Ontario take-home manifest's T2204 inputs a salary-only caller does not give: line 2, the
self-employment earnings, and line 5, the Schedule 13 premium.

T2204 line 2: "Total self-employment and other earnings eligible for the EI program for access to EI
special benefits". A salary-only caller has none, so a request that leaves the line out is read as
blank, and the line 1 part reads that blank as 0.

T2204 line 5: "Residents of other than Quebec (amount from line 9 of Schedule 13)". A salary-only
caller has no Schedule 13 premium, so a request that leaves the line out is read as blank, and the
line 6 part reads that blank as 0.

The real part is loaded under a test-local header, as the take-home header is another part's.
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
LINE_5 = "ca/t2204_line_5"
PRINTED_BASIS_LINE_5 = "Residents of other than Quebec (amount from line 9 of Schedule 13)"
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


def test_a_request_that_leaves_out_line_5_is_read_as_blank(tmp_path: Path) -> None:
    kinds = artifact_kinds()
    declaration = _manifest(tmp_path).inputs[LINE_5]
    default = declaration.default_artifact(kinds.kind(LINE_5))
    assert not declaration.required
    assert declaration.basis == PRINTED_BASIS_LINE_5
    assert default is not None and default.is_blank
