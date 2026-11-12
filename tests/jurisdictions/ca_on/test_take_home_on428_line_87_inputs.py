"""ON428 (2025) line 87's input, as the Ontario take-home manifest part declares it.

Form text (ON428, CRA 5006-c-25e.txt in docs/cra-forms-2025): "Line 87 and line 62150: Enter the
amount of qualifying donations that have also been claimed as a charitable donation. ^". The
input is the qualifying donations, as the form takes them; the 25% is computed by the line 87
part, not by the caller. A salary-only caller makes no community food program donation, so a
request that leaves the input out is read as 0, not blank.

The real part is loaded under a test-local header, as the take-home header is another part's.
"""

from __future__ import annotations

import shutil
from decimal import Decimal
from pathlib import Path

import tax_engine.jurisdictions.ca_on
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.domain.manifest import Manifest
from tax_engine.jurisdictions.ca_on.catalog import ON428_QUALIFYING_FOOD_DONATIONS_LINE_87
from tax_engine.registrations import JURISDICTIONS, artifact_kinds, units

D = Decimal
PRINTED_BASIS = (
    "Line 87 and line 62150: Enter the amount of qualifying donations that have also been claimed "
    "as a charitable donation"
)
PART = Path(tax_engine.jurisdictions.ca_on.__file__).parent / (
    "manifests/2025/on428_line_87_inputs.yaml"
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


def test_a_request_that_leaves_out_line_87_is_read_as_zero(tmp_path: Path) -> None:
    kinds = artifact_kinds()
    identifier = ON428_QUALIFYING_FOOD_DONATIONS_LINE_87.identifier
    declaration = _manifest(tmp_path).inputs[identifier]
    default = declaration.default_artifact(kinds.kind(identifier))
    assert not declaration.required
    assert declaration.basis == PRINTED_BASIS
    assert default is not None and not default.is_blank
    assert default.value == D("0")
