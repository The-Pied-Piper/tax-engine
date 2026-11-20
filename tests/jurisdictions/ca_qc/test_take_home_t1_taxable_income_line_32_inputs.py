"""5005-R (2025) line 32 and line 14700: a Quebec manifest input a salary-only caller does not give.

Form text (CRA 5005-R page 3, https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5005-r/5005-r-25e.txt):
"Line 32 and line 14700: Add lines 29 to 31 (see line 25000 in Step 4). =". Lines 29 to 31 are blank
for a salary-only filer, so the printed sum is one optional input, read as 0 when left out, with
no step.

The real part is loaded under a test-local header, as the Quebec header is another part's.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.domain.manifest import Manifest
from tests.jurisdictions.ca_qc.conftest import TakeHomeService
from tests.jurisdictions.ca_qc.support import quebec_kinds, quebec_packages, quebec_units

D = Decimal
KIND = "ca-qc/t1_line_32"
PRINTED_BASIS = "Line 32 and line 14700: Add lines 29 to 31"
PART = "t1_taxable_income_line_32_inputs.yaml"
HEADER = """\
jurisdiction: CA-QC
version: 1
valid_from_tax_year: 2025
outputs: [ca-qc/t1_line_32]
capabilities: []
"""
FORM = """\
form:
  name: ca-qc/t1_taxable_income
  required: true
  exports:
    - ca-qc/t1_line_32
capabilities: []
"""


def _manifest(take_home_service: TakeHomeService, tmp_path: Path) -> Manifest:
    """The temporary take-home folder the shared builder writes, loaded as a manifest."""
    take_home_service(HEADER, FORM, PART)
    folder = tmp_path / "manifests" / "2025"
    return YamlJurisdictionSource(quebec_packages().roots(), quebec_kinds(), quebec_units()).load(
        folder
    )


def test_a_request_that_leaves_out_t1_line_32_is_read_as_zero(
    take_home_service: TakeHomeService, tmp_path: Path
) -> None:
    declaration = _manifest(take_home_service, tmp_path).inputs[KIND]
    default = declaration.default_artifact(quebec_kinds().kind(KIND))
    assert not declaration.required
    assert declaration.basis == PRINTED_BASIS
    assert declaration.reference == "14700"
    assert default is not None and not default.is_blank
    assert default.value == D("0")
