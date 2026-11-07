"""The Ontario take-home manifest's T1 input a salary-only caller does not give: line 10400, other
employment income.

T1 line 10400: "Line 2 and line 10400: Other employment income". A salary-only caller has no slips,
tips or other employment income, so a request that leaves the line out is read as 0, not blank.

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

D = Decimal
OTHER_EMPLOYMENT_INCOME = "ca/other_employment_income"
PRINTED_BASIS = "Line 2 and line 10400: Other employment income"
PART = Path(tax_engine.jurisdictions.ca_on.__file__).parent / (
    "manifests/take_home/t1_taxable_income/t1_taxable_income_line_10400_inputs.yaml"
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


def test_a_request_that_leaves_out_other_employment_income_is_read_as_zero(
    tmp_path: Path,
) -> None:
    kinds = artifact_kinds()
    declaration = _manifest(tmp_path).inputs[OTHER_EMPLOYMENT_INCOME]
    default = declaration.default_artifact(kinds.kind(OTHER_EMPLOYMENT_INCOME))
    assert not declaration.required
    assert declaration.basis == PRINTED_BASIS
    assert default is not None and not default.is_blank
    assert default.value == D("0")
