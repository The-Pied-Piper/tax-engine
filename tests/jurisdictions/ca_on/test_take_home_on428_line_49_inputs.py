"""ON428 (2025) line 49's input, as the Ontario take-home manifest part declares it.

Form text (ON428, CRA 5006-c-25e.txt in cra-docs/docs/cra-forms-2025): "Line 49 and line 58969: Line
47
plus line 48". A salary-only caller has no donations credit, so a request
that leaves the line out is read as 0, not blank.

The real part is loaded under a test-local header, as the take-home header is another part's.
"""

from __future__ import annotations

import shutil
from decimal import Decimal
from pathlib import Path

import tax_engine.jurisdictions.ca_on
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.domain.manifest import Manifest
from tax_engine.jurisdictions.ca_on.catalog import ON428_DONATIONS_CREDIT_LINE_49
from tax_engine.registrations import JURISDICTIONS, artifact_kinds, units

D = Decimal
PRINTED_BASIS = "Line 49 and line 58969: Line 47 plus line 48"
PART = Path(tax_engine.jurisdictions.ca_on.__file__).parent / (
    "manifests/2025/on428_line_49_inputs.yaml"
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
    return YamlJurisdictionSource(JURISDICTIONS.roots(), artifact_kinds(), units()).load(folder)


def test_a_request_that_leaves_out_the_donations_credit_is_read_as_zero(
    tmp_path: Path,
) -> None:
    kinds = artifact_kinds()
    declaration = _manifest(tmp_path).inputs[ON428_DONATIONS_CREDIT_LINE_49.identifier]
    default = declaration.default_artifact(kinds.kind(ON428_DONATIONS_CREDIT_LINE_49.identifier))
    assert not declaration.required
    assert declaration.basis == PRINTED_BASIS
    assert default is not None and not default.is_blank
    assert default.value == D("0")
