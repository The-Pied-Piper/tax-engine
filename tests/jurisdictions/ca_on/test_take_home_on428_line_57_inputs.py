"""ON428 (2025) line 57's input, as the Ontario take-home manifest part declares it.

Form text (ON428, CRA 5006-c-25e.txt in docs/cra-forms-2025): "Line 57 and line and line 61520:
Ontario dividend tax credit (use Worksheet ON428)" is the line's basis in the take-home part. A
salary-only caller has no dividend income, so a request that leaves the line out is read as blank,
and the line 71 part reads that blank as 0.

The part is loaded from the test data folder under a test-local header, as the take-home header is
another part's.
"""

from __future__ import annotations

import shutil
from pathlib import Path

import tax_engine.jurisdictions.ca_on
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.domain.manifest import Manifest
from tax_engine.registrations import JURISDICTIONS, artifact_kinds

PRINTED_BASIS = "Line 57 and line and line 61520: Ontario dividend tax credit (use Worksheet ON428)"
LINE_57 = "ca-on/on428_dividend_tax_credit_line_57"
PART = Path(tax_engine.jurisdictions.ca_on.__file__).parent / (
    "manifests/take_home/on428/on428_line_57_inputs.yaml"
)
HEADER = """\
jurisdiction: CA-ON
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
    return YamlJurisdictionSource(JURISDICTIONS.roots(), artifact_kinds()).load(folder)


def test_a_request_that_leaves_out_line_57_is_read_as_blank(tmp_path: Path) -> None:
    kinds = artifact_kinds()
    declaration = _manifest(tmp_path).inputs[LINE_57]
    default = declaration.default_artifact(kinds.kind(LINE_57))
    assert not declaration.required
    assert declaration.basis == PRINTED_BASIS
    assert default is not None and default.is_blank
