"""Schedule 6 (2025) line 11's input, as the Ontario take-home manifest part declares it.

Form text (Schedule 6, CRA 5000-s6-25e.txt in cra-docs/docs/cra-forms-2025):
"Line 11: Total of UCCB (line 11700 of the return) and RDSP income (line 12500 of the return)" is
the line's basis in the take-home part. A salary-only caller has no UCCB or RDSP income, so a
request that leaves the line out is read as blank, and the line 12 part reads that blank as 0.

The part is loaded from the test data folder under a test-local header, as the take-home header is
another part's.
"""

from __future__ import annotations

from pathlib import Path

import tax_engine.jurisdictions.ca
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.domain.manifest import Manifest
from tax_engine.registrations import JURISDICTIONS, artifact_kinds, units
from tests.manifest_support import inputs_without_form

LINE_11 = "ca/uccb_and_rdsp_income"
PRINTED_BASIS = (
    "Line 11: Total of UCCB (line 11700 of the return) and RDSP income (line 12500 of the return)"
)
PART = Path(tax_engine.jurisdictions.ca.__file__).parent / (
    "forms/schedule_6/schedule_6_line_11_inputs.yaml"
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
    (folder / PART.name).write_text(inputs_without_form(PART), encoding="utf-8")
    return YamlJurisdictionSource(JURISDICTIONS.roots(), artifact_kinds(), units()).load(folder)


def test_a_request_that_leaves_out_line_11_is_read_as_blank(tmp_path: Path) -> None:
    kinds = artifact_kinds()
    declaration = _manifest(tmp_path).inputs[LINE_11]
    default = declaration.default_artifact(kinds.kind(LINE_11))
    assert not declaration.required
    assert declaration.basis == PRINTED_BASIS
    assert default is not None and default.is_blank
