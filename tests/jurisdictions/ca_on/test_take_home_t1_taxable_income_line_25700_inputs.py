"""The Ontario take-home manifest's T1 taxable income input a salary-only caller does not give: line
25700, the deductions from net income.

T1 line 25700: "Line 68 and line 25700: Add lines 58 to 67." A salary-only caller has none of lines
58 to 67, so a request that leaves the line out is read as 0, and the line 26000 part takes that 0
off net income.

The real part is loaded under a test-local header, as the take-home header is another part's.
"""

from __future__ import annotations

import shutil
from decimal import Decimal
from pathlib import Path

import tax_engine.jurisdictions.ca_on
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.domain.manifest import Manifest
from tax_engine.registrations import JURISDICTIONS, artifact_kinds

LINE_25700 = "ca/deductions_from_net_income"
PRINTED_BASIS = "Line 68 and line 25700: Add lines 58 to 67."
PART = Path(tax_engine.jurisdictions.ca_on.__file__).parent / (
    "manifests/take_home/t1_taxable_income_line_25700_inputs.yaml"
)
HEADER = """\
jurisdiction: CA-ON
version: 1
valid_from_tax_year: 2025
outputs: [ca/deductions_from_net_income]
capabilities: []
"""


def _manifest(tmp_path: Path) -> Manifest:
    folder = tmp_path / "manifest"
    folder.mkdir()
    (folder / "header.yaml").write_text(HEADER)
    shutil.copy(PART, folder / PART.name)
    return YamlJurisdictionSource(JURISDICTIONS.roots(), artifact_kinds()).load(folder)


def test_a_request_that_leaves_out_line_25700_is_read_as_zero(tmp_path: Path) -> None:
    kinds = artifact_kinds()
    declaration = _manifest(tmp_path).inputs[LINE_25700]
    default = declaration.default_artifact(kinds.kind(LINE_25700))
    assert not declaration.required
    assert declaration.basis == PRINTED_BASIS
    assert default is not None and default.value == Decimal(0)
