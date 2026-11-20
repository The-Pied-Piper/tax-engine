"""5005-R (2025) line 69 (line 25700), deductions from net income: a Quebec manifest input a
salary-only caller does not give.

Form text (CRA 5005-R page 5, https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5005-r/5005-r-25e.txt):
"Line 69 and line 25700: Add lines 59 to 68. =". Lines 59 to 68 are blank for a salary-only filer,
so the printed sum is one optional input, read as 0 when left out, with no step.

The real part is loaded under a test-local header, as the Quebec header is another part's."""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.domain.manifest import Manifest
from tests.jurisdictions.ca_qc.conftest import TakeHomeService
from tests.jurisdictions.ca_qc.support import quebec_kinds, quebec_packages, quebec_units

D = Decimal
KIND = "ca/deductions_from_net_income"
PRINTED_BASIS = "Line 69 and line 25700: Add lines 59 to 68."
PART = "t1_taxable_income_line_25700_inputs.yaml"
HEADER = """\
jurisdiction: CA-QC
version: 1
valid_from_tax_year: 2025
outputs: [ca/deductions_from_net_income]
capabilities: []
"""
FORM = """\
form:
  name: ca-qc/t1_taxable_income
  required: true
  exports:
    - ca/deductions_from_net_income
capabilities: []
"""


def _manifest(take_home_service: TakeHomeService, tmp_path: Path) -> Manifest:
    """The temporary take-home folder the shared builder writes, loaded as a manifest."""
    take_home_service(HEADER, FORM, PART)
    folder = tmp_path / "manifests" / "2025"
    return YamlJurisdictionSource(quebec_packages().roots(), quebec_kinds(), quebec_units()).load(
        folder
    )


def test_a_request_that_leaves_out_the_deductions_from_net_income_is_read_as_zero(
    take_home_service: TakeHomeService, tmp_path: Path
) -> None:
    declaration = _manifest(take_home_service, tmp_path).inputs[KIND]
    default = declaration.default_artifact(quebec_kinds().kind(KIND))
    assert not declaration.required
    assert declaration.basis == PRINTED_BASIS
    assert declaration.reference == "25700"
    assert default is not None and not default.is_blank
    assert default.value == D("0")
