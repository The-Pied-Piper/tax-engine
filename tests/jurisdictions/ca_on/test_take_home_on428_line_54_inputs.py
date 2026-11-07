"""ON428 (2025) line 54's input, as the Ontario take-home manifest part declares it.

Form text (ON428, CRA 5006-c-25e.txt in docs/cra-forms-2025): "Line 54 and line 61510: Ontario tax
on split income (complete Form T1206)" is the line's basis in the take-home part. A caller with no
split income leaves the line out, so the request is read as blank, and the line 55 part reads that
blank as 0.

The real part is loaded under a test-local header, as the take-home header is another part's.
"""

from __future__ import annotations

import shutil
from pathlib import Path

import tax_engine.jurisdictions.ca_on
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.domain.manifest import Manifest
from tax_engine.jurisdictions.ca_on.catalog import ON428_TAX_ON_SPLIT_INCOME_LINE_54
from tax_engine.registrations import JURISDICTIONS, artifact_kinds

PRINTED_BASIS = "Line 54 and line 61510: Ontario tax on split income (complete Form T1206)"
PART = Path(tax_engine.jurisdictions.ca_on.__file__).parent / (
    "manifests/take_home/on428_line_54_inputs.yaml"
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


def test_a_request_that_leaves_out_line_54_is_read_as_blank(tmp_path: Path) -> None:
    kinds = artifact_kinds()
    identifier = ON428_TAX_ON_SPLIT_INCOME_LINE_54.identifier
    declaration = _manifest(tmp_path).inputs[identifier]
    default = declaration.default_artifact(kinds.kind(identifier))
    assert not declaration.required
    assert declaration.basis == PRINTED_BASIS
    assert default is not None and default.is_blank
